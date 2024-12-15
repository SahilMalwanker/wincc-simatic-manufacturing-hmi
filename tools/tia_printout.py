"""Extract structured HMI engineering data from a TIA Portal project documentation PDF.

TIA Portal prints every project object as a property table: bold property names, regular
values, and headings whose font size encodes the object level. The table is rebuilt from
glyph positions, weights and sizes (pypdfium2), then walked from top to bottom to collect
screens, screen objects, animations, events, HMI tags, recipes and user groups.

    python tools/tia_printout.py docs/pdf/tia-portal-project-documentation.pdf --out data
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

import pypdfium2 as pdfium
import pypdfium2.raw as pdfium_c

PAGE_HEADER = ("Totally Integrated", "Automation Portal")
BREADCRUMB = re.compile(r"^(?P<device>[^/\[\]]+) \[(?P<type>[^\]]+)\](?: / (?P<path>.+))?$")
SCREEN_KINDS = {
    "Screens": "screen",
    "Screen management / Templates": "template",
    "Screen management / Pop-up screens": "pop-up",
    "Screen management / Slide-in screens": "slide-in",
    "Screen management": "global",
}
IO_LABEL = re.compile(r"^(?P<address>[IQ]\d+\.\d) - (?P<signal>.+)$")
WORD_GAP = 1.5  # pt between glyphs that marks a space
CELL_GAP = 9.0  # pt between glyphs that starts a new table cell
LINE_TOLERANCE = 2.0
# heading levels by font size relative to body text (15 / 13 / 11 / 10 pt vs 9 pt)
LEVELS = ((1.55, 4), (1.33, 3), (1.17, 2), (1.06, 1))
BREADCRUMB_LEVEL, TITLE_LEVEL, RECORD_LEVEL, ITEM_LEVEL = 4, 3, 2, 1


@dataclass
class Cell:
    x: float
    text: str
    bold: bool


@dataclass
class Row:
    cells: list[Cell]
    level: int = 0

    @property
    def heading(self) -> str | None:
        """Text of a single bold cell (headings, object names), else None."""
        if len(self.cells) == 1 and self.cells[0].bold:
            return self.cells[0].text
        return None


@dataclass
class Record:
    """A printed object: a screen, a screen object, an HMI tag, a user group, ..."""

    name: str
    section: str
    parent: str = ""
    kind: str = ""
    props: list[tuple[str, str]] = field(default_factory=list)
    groups: list[str] = field(default_factory=list)

    def get(self, key: str, default: str = "") -> str:
        return next((v for k, v in self.props if k == key), default)

    def values(self, key: str) -> list[str]:
        return [v for k, v in self.props if k == key]


@dataclass
class Screen:
    record: Record
    objects: list[Record] = field(default_factory=list)

    @property
    def name(self) -> str:
        return self.record.name


@dataclass
class Printout:
    device: dict[str, str]
    screens: list[Screen]
    records: list[Record]

    def find(self, section: str, parent: str | None = None) -> list[Record]:
        """Records of a section (optionally below a title), excluding the titles themselves."""
        return [
            r for r in self.records
            if r.section == section and r.kind != "title" and (parent is None or r.parent.startswith(parent))
        ]

    def titled(self, section: str, title: str) -> Record:
        return next((r for r in self.records if r.section == section and r.name == title), Record(title, section))


# --------------------------------------------------------------------------- layout

Glyph = tuple[float, float, float, str, float, int]  # y, left, right, char, height, weight


def _page_glyphs(page: pdfium.PdfPage) -> list[Glyph]:
    textpage = page.get_textpage()
    glyphs = []
    for i in range(textpage.count_chars()):
        char = textpage.get_text_range(i, 1)
        if not char.strip():
            continue
        left, bottom, right, top = textpage.get_charbox(i, loose=True)
        weight = pdfium_c.FPDFText_GetFontWeight(textpage.raw, i)
        glyphs.append(((bottom + top) / 2, left, right, char, top - bottom, weight))
    textpage.close()
    return glyphs


def _lines(glyphs: list[Glyph]) -> list[list[Glyph]]:
    lines: list[list[Glyph]] = []
    current_y = None
    for glyph in sorted(glyphs, key=lambda g: -g[0]):
        if current_y is None or abs(glyph[0] - current_y) > LINE_TOLERANCE:
            lines.append([])
            current_y = glyph[0]
        lines[-1].append(glyph)
    return [sorted(line, key=lambda g: g[1]) for line in lines]


def _cells(line: list[Glyph], bold_weight: int) -> list[Cell]:
    cells: list[Cell] = []
    last_right = 0.0
    for _, left, right, char, _, weight in line:
        bold = weight >= bold_weight
        gap = left - last_right
        if not cells or gap > CELL_GAP or bold != cells[-1].bold:
            cells.append(Cell(left, char, bold))
        else:
            cells[-1].text += (" " if gap > WORD_GAP else "") + char
        last_right = right
    return cells


def _level(line: list[Glyph], body_height: float) -> int:
    heights = sorted(g[4] for g in line)
    ratio = heights[len(heights) // 2] / body_height
    return next((level for threshold, level in LEVELS if ratio >= threshold), 0)


def _is_continuation(row: Row, previous: Row) -> bool:
    """Wrapped key or value text printed on the next line of the same table cell."""
    if row.level or not previous.cells or previous.level:
        return False
    for cell in row.cells:
        match = next((c for c in previous.cells if abs(c.x - cell.x) <= 3 and c.bold == cell.bold), None)
        if match is None:
            return False
        if cell.bold and not (cell.text[0].islower() or cell.text[0] in "(/" or match.text.endswith("\u2010")):
            return False
    return True


def _merge(row: Row, previous: Row) -> None:
    for cell in row.cells:
        target = next(c for c in previous.cells if abs(c.x - cell.x) <= 3 and c.bold == cell.bold)
        if target.text.endswith("\u2010"):  # hyphenated word
            target.text = target.text[:-1] + cell.text
        elif " " not in target.text and (cell.text[0].islower() or cell.text[0].isdigit()):  # long identifier
            target.text += cell.text
        else:
            target.text = f"{target.text} {cell.text}"


def read_rows(pdf_path: str | Path) -> list[Row]:
    """Read the whole printout as table rows, page headers removed and wrapped cells joined."""
    pdf = pdfium.PdfDocument(str(pdf_path))
    try:
        pages = [_page_glyphs(page) for page in pdf]
    finally:
        pdf.close()
    glyphs = [g for page in pages for g in page]
    weights = sorted({g[5] for g in glyphs})
    bold_weight = weights[-1] if len(weights) > 1 else weights[0] + 1
    body_height = Counter(round(g[4], 1) for g in glyphs).most_common(1)[0][0]
    rows: list[Row] = []
    for page in pages:
        for line in _lines(page):
            row = Row(_cells(line, bold_weight), _level(line, body_height))
            if row.cells and row.cells[0].text in PAGE_HEADER:
                continue
            if rows and _is_continuation(row, rows[-1]):
                _merge(row, rows[-1])
            else:
                rows.append(row)
    return rows


# --------------------------------------------------------------------------- records


def _starts_record(rows: list[Row], i: int) -> bool:
    """A record heading is followed (optionally after 'General') by 'Name <heading>'."""
    name = rows[i].heading
    for j in (i + 1, i + 2):
        if j >= len(rows):
            return False
        cells = rows[j].cells
        if len(cells) >= 2 and cells[0].text == "Name" and cells[1].text == name:
            return True
        if rows[j].heading != "General":
            return False
    return False


def _add_props(record: Record, row: Row) -> None:
    if (heading := row.heading) is not None:
        record.groups.append(heading)
        return
    key = None
    for cell in row.cells:
        if cell.bold:
            if key is not None:
                record.props.append((key, ""))
            key = cell.text
        elif key is not None:
            record.props.append((key, cell.text))
            key = None
        else:  # unlabelled value, e.g. layer lists
            record.props.append((cell.text, ""))
    if key is not None:
        record.props.append((key, ""))


def parse_rows(rows: list[Row]) -> Printout:
    device: dict[str, str] = {}
    screens: list[Screen] = []
    records: list[Record] = []
    section, title = "", ""
    current: Record | None = None
    for i, row in enumerate(rows):
        heading = row.heading
        if row.level == BREADCRUMB_LEVEL and heading and (m := BREADCRUMB.match(heading)):
            device.setdefault("name", m["device"])
            device.setdefault("type", m["type"])
            section, title, current = m["path"] or "", "", None
            continue
        kind = SCREEN_KINDS.get(section)
        if kind:
            if row.level == TITLE_LEVEL and heading:
                current = Record(heading, section, kind=kind)
                screens.append(Screen(current))
            elif row.level == RECORD_LEVEL and heading and heading.startswith("Hardcopy of "):
                continue
            elif row.level == ITEM_LEVEL and heading and screens and not heading.startswith("Function list\\"):
                current = Record(heading, section, parent=screens[-1].name)
                screens[-1].objects.append(current)
            elif current is not None:
                _add_props(current, row)
                if current.kind == "" and current.props and current.props[0][0] == "Type":
                    current.kind = current.props.pop(0)[1]
            continue
        if row.level == TITLE_LEVEL and heading:
            title = heading
            current = Record(heading, section, kind="title")
            records.append(current)
        elif row.level >= ITEM_LEVEL and heading and _starts_record(rows, i):
            current = Record(heading, section, parent=title)
            records.append(current)
        elif current is not None:
            _add_props(current, row)
    return Printout(device, screens, records)


def parse_printout(pdf_path: str | Path) -> Printout:
    return parse_rows(read_rows(pdf_path))


# --------------------------------------------------------------------------- tables

ANIMATION_KINDS = ("Visibility", "Appearance", "Tag connection", "Event")


def _animations(obj: Record) -> Counter:
    return Counter(g.split("\\", 1)[1] for g in obj.groups if g.startswith("Dynamizations\\"))


def _functions(obj: Record) -> list[str]:
    return [g.split("\\", 1)[1] for g in obj.groups if g.startswith("Function list\\")]


def _texts(obj: Record) -> list[str]:
    # "Text" alone is the printout's placeholder for an unset button caption
    return [v for k, v in obj.props if k in ("Text", "Text OFF", "Text ON") and v and v != "Text"]


def _tags_used(screen: Screen, tag_names: set[str]) -> set[str]:
    used = set()
    for record in (screen.record, *screen.objects):
        for _, value in record.props:
            token = value.strip().rstrip("-").strip().strip('"')
            if token in tag_names:
                used.add(token)
    return used


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def tag_rows(p: Printout) -> list[dict[str, str]]:
    return [
        {
            "name": t.name,
            "table": re.sub(r" \[\d+\]$", "", t.parent),
            "data_type": t.get("Data type"),
            "connection": t.get("Connection") or "<internal>",
            "plc_tag": t.get("PLC tag"),
            "access_mode": t.get("Access mode"),
            "acquisition_cycle": t.get("Acquisition cycle"),
        }
        for t in p.find("HMI tags")
    ]


def screen_rows(p: Printout) -> list[dict[str, object]]:
    tag_names = {t.name for t in p.find("HMI tags")}
    types = sorted({o.kind for s in p.screens for o in s.objects})
    rows = []
    for s in p.screens:
        counts = Counter(o.kind for o in s.objects)
        animations = sum((_animations(o) for o in s.objects), Counter())
        rows.append(
            {
                "screen": s.name,
                "kind": s.record.kind,
                "number": s.record.get("Number"),
                "template": s.record.get("Template"),
                "objects": len(s.objects),
                **{f"type_{_slug(t)}": counts.get(t, 0) for t in types},
                **{f"anim_{_slug(k)}": animations.get(k, 0) for k in ANIMATION_KINDS},
                "functions": sum(len(_functions(o)) for o in s.objects),
                "tags_used": len(_tags_used(s, tag_names)),
            }
        )
    return rows


def object_rows(p: Printout) -> list[dict[str, str]]:
    return [
        {
            "screen": s.name,
            "object": o.name,
            "type": o.kind,
            "x": o.get("X position"),
            "y": o.get("Y position"),
            "animations": ";".join(sorted(_animations(o).elements())),
            "functions": ";".join(_functions(o)),
            "text": " | ".join(_texts(o)),
        }
        for s in p.screens
        for o in s.objects
    ]


def navigation_rows(p: Printout) -> list[dict[str, str]]:
    """Screen changes and pop-ups triggered by operator events."""
    rows: dict[tuple[str, ...], dict[str, str]] = {}
    for s in p.screens:
        for o in s.objects:
            event = next(iter(o.values("Event name")), "")
            targets = {"ActivateScreen": o.values("Screen name"), "ShowPopupScreen": o.values("Name of the screen")}
            for function, names in targets.items():
                for target in names:
                    row = {"screen": s.name, "object": o.name, "event": event, "function": function, "target": target}
                    rows[tuple(row.values())] = row
    return list(rows.values())


def io_rows(p: Printout) -> list[dict[str, str]]:
    found = {}
    for s in p.screens:
        for o in s.objects:
            for text in _texts(o):
                if m := IO_LABEL.match(text):
                    direction = "input" if m["address"].startswith("I") else "output"
                    found[m["address"]] = {"address": m["address"], "direction": direction, "signal": m["signal"]}

    def order(address: str) -> tuple[str, int, int]:
        byte, bit = address[1:].split(".")
        return address[0], int(byte), int(bit)

    return [found[a] for a in sorted(found, key=order)]


def alarm_rows(p: Printout, screen: str = "Alarm") -> list[dict[str, str]]:
    """Alarm and warning indicator labels, grouped by the heading printed above them."""
    s = next(x for x in p.screens if x.name == screen)
    texts = sorted(
        (int(o.get("Y position") or 0), int(o.get("X position") or 0), t)
        for o in s.objects
        if o.kind == "Text field"
        for t in _texts(o)
    )
    headings = [(y, t) for y, _, t in texts if t.startswith("Operational ")]
    rows = []
    for y, x, text in sorted(texts, key=lambda t: (round(t[0] / 25), t[1])):  # visual reading order
        group = next((h for hy, h in reversed(headings) if hy < y), None)
        if group and not text.startswith("Operational "):
            rows.append({"group": group.removeprefix("Operational ").rstrip("s").lower(), "label": text, "x": x, "y": y})
    return rows


def recipe_rows(p: Printout) -> list[dict[str, str]]:
    return [
        {"element": r.name, "display_name": r.get("Display name"), "tag": r.get("Tag"), "data_type": r.get("Tag data type")}
        for r in p.find("", "Recipes")
        if r.name.startswith("Recipe_element_")
    ]


def group_rows(p: Printout) -> list[dict[str, str]]:
    return [
        {
            "group": r.name,
            "number": r.get("Number"),
            "authorizations": "; ".join(a.strip() for a in r.get("Authorizations").split(";") if a.strip()),
        }
        for r in p.find("User administration", "Groups")
    ]


def summary(p: Printout) -> dict[str, object]:
    objects = [o for s in p.screens for o in s.objects]
    tags = p.find("HMI tags")
    runtime = p.titled("", "Runtime settings")
    connection = next((r for r in p.find("", "Connections") if r.get("Communication driver")), Record("", ""))
    languages = [g for g in runtime.groups if re.match(r"^[A-Z][a-z]+ \([A-Z][\w ]+\)$", g)]
    return {
        "device": {
            **p.device,
            "start_screen": runtime.get("Start screen"),
            "resolution": runtime.get("Screen resolution"),
            "style": runtime.get("Style of the HMI device"),
            "runtime_languages": sorted(set(languages)),
        },
        "connection": {k: connection.get(v) for k, v in (
            ("driver", "Communication driver"), ("station", "Station"), ("partner", "Partner"), ("node", "Node"))},
        "screens": dict(Counter(s.record.kind for s in p.screens)),
        "objects": len(objects),
        "object_types": dict(Counter(o.kind for o in objects).most_common()),
        "animations": dict(sum((_animations(o) for o in objects), Counter()).most_common()),
        "system_functions": dict(Counter(f for o in objects for f in _functions(o)).most_common()),
        "events": dict(Counter(e for o in objects for e in o.values("Event name")).most_common()),
        "hmi_tags": len(tags),
        "tag_data_types": dict(Counter(t.get("Data type") for t in tags).most_common()),
        "recipe_elements": len(recipe_rows(p)),
        "user_groups": len(group_rows(p)),
        "graphic_lists": {r.name: len(r.values("Entry type")) for r in p.find("Text and graphic lists", "Graphic lists")},
    }


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def tables(p: Printout) -> dict[str, list[dict[str, object]]]:
    return {
        "hmi_tags.csv": tag_rows(p),
        "screens.csv": screen_rows(p),
        "screen_objects.csv": object_rows(p),
        "navigation.csv": navigation_rows(p),
        "io_map.csv": io_rows(p),
        "alarm_indicators.csv": alarm_rows(p),
        "recipe_elements.csv": recipe_rows(p),
        "user_groups.csv": group_rows(p),
    }


def export(p: Printout, out: Path) -> list[Path]:
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for name, rows in tables(p).items():
        _write_csv(out / name, rows)
        written.append(out / name)
    (out / "summary.json").write_text(json.dumps(summary(p), indent=2) + "\n", encoding="utf-8")
    written.append(out / "summary.json")
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("pdf", type=Path, help="TIA Portal project documentation (PDF)")
    parser.add_argument("--out", type=Path, default=Path("data"), help="output folder")
    args = parser.parse_args()
    for path in export(parse_printout(args.pdf), args.out):
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
