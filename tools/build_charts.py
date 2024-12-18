"""Render the README charts (SVG) from the tables written by tia_printout.py.

    python tools/build_charts.py --data data --out assets/charts
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

TEAL, TEAL_LIGHT, INK, MUTED, GRID = "#0f6e78", "#7fbcc3", "#1f2933", "#66727f", "#e3e8ec"
TYPE_GROUPS = {
    "Graphic views": (["graphic_view"], TEAL),
    "Text fields": (["text_field"], TEAL_LIGHT),
    "Buttons": (["button"], "#f2a541"),
    "Shapes": (["rectangle", "circle", "polygon"], "#a7b1bc"),
    "I/O & data fields": (["i_o_field", "graphic_i_o_field", "date_time_field"], "#4f7cac"),
    "Bars": (["bar"], "#2f9e5b"),
    "Other": (["group", "recipe_view", "user_view"], "#d3d8de"),
}
SUBSYSTEMS = [  # keyword in the signal name -> legend label, colour
    ("Resin Enhancer", "Resin enhancer", "#c08a3e"),
    ("Solvent Binder", "Solvent binder", "#d8b63a"),
    ("Red Pigment", "Red pigment", "#d1495b"),
    ("Green Pigment", "Green pigment", "#2f9e5b"),
    ("Blue Pigment", "Blue pigment", "#3d6fb6"),
    ("Pigment", "Pigment circuit", "#8a6fb3"),
    ("Agitator", "Mixing tank & agitator", TEAL),
    ("Mixing Tank", "Mixing tank & agitator", TEAL),
    ("", "Safety, alarms & utilities", "#66727f"),
]

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.edgecolor": GRID,
    "axes.labelcolor": MUTED,
    "xtick.color": MUTED,
    "ytick.color": INK,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "svg.hashsalt": "paint-manufacturing-hmi",
})


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _title(fig: plt.Figure, title: str, subtitle: str) -> None:
    fig.text(0.02, 0.965, title, fontsize=15, fontweight="bold", color=INK, va="top")
    fig.text(0.02, 0.905, subtitle, fontsize=10, color=MUTED, va="top")


def _save(fig: plt.Figure, path: Path) -> None:
    fig.savefig(path, format="svg", facecolor="white", metadata={"Date": None, "Creator": None})
    plt.close(fig)
    print(f"wrote {path}")


def composition_chart(screens: list[dict[str, str]], path: Path) -> None:
    rows = [r for r in screens if int(r["objects"])]
    bars: list[tuple[str, dict[str, int], int]] = []
    for kind, label in (("template", "Navigation template"), ("pop-up", "Valve pop-up")):
        group = [r for r in rows if r["kind"] == kind and (kind != "pop-up" or "Valve" in r["screen"])]
        if group:
            first = group[0]
            bars.append((f"{label} (x{len(group)})", first, int(first["objects"])))
    bars += [(re.sub(r"(?<=[a-z])(?=[A-Z])", " ", r["screen"]).replace("_", " "), r, int(r["objects"])) for r in rows
             if r["kind"] == "screen" or (r["kind"] == "pop-up" and "Valve" not in r["screen"])]
    bars.sort(key=lambda b: b[2])
    fig, ax = plt.subplots(figsize=(10, 6.2))
    fig.subplots_adjust(left=0.2, right=0.97, top=0.78, bottom=0.08)
    y = range(len(bars))
    left = [0] * len(bars)
    for label, (columns, colour) in TYPE_GROUPS.items():
        values = [sum(int(row.get(f"type_{c}", 0)) for c in columns) for _, row, _ in bars]
        ax.barh(list(y), values, left=left, color=colour, label=label, height=0.66, edgecolor="white", linewidth=0.6)
        left = [a + b for a, b in zip(left, values)]
    for i, (_, _, total) in enumerate(bars):
        ax.text(total + 2, i, str(total), va="center", fontsize=9, color=INK, fontweight="bold")
    ax.set_xlim(0, max(b[2] for b in bars) * 1.08)
    ax.set_yticks(list(y), [b[0] for b in bars])
    ax.set_xlabel("configured screen objects")
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", length=0)
    ax.legend(ncol=7, loc="lower left", bbox_to_anchor=(-0.22, 1.01), frameon=False, fontsize=8.5,
              handlelength=1.1, columnspacing=1.0)
    total = sum(int(r["objects"]) for r in rows)
    kinds = Counter(r["kind"] for r in screens)
    _title(fig, "What is on each screen",
           f"{total} configured objects across {kinds['screen']} screens, {kinds['pop-up']} pop-ups and "
           f"{kinds['template']} templates (parsed from the TIA Portal printout)")
    _save(fig, path)


def dynamics_chart(summary: dict, path: Path) -> None:
    labels = {
        "Visibility": "Visibility (pipe flow, valve states)",
        "Appearance": "Appearance (status lamps, alarm tiles)",
        "Event": "Events (operator actions)",
        "Tag connection": "Tag connections (bars, I/O fields)",
    }
    colours = [TEAL, "#f2a541", "#4f7cac", TEAL_LIGHT]
    data = summary["animations"]
    fig = plt.figure(figsize=(10, 4.6))
    _title(fig, "How the screens come alive",
           "Dynamizations configured on screen objects and the WinCC system functions their events call")
    ax = fig.add_axes((0.0, 0.05, 0.42, 0.74))
    values = [data[k] for k in labels]
    ax.pie(values, colors=colours, startangle=90, counterclock=False,
           wedgeprops={"width": 0.36, "edgecolor": "white", "linewidth": 2})
    ax.text(0, 0.08, str(sum(values)), ha="center", va="center", fontsize=24, fontweight="bold", color=INK)
    ax.text(0, -0.2, "dynamizations", ha="center", va="center", fontsize=9, color=MUTED)
    ax.set_aspect("equal")
    legend = fig.add_axes((0.36, 0.05, 0.2, 0.74))
    legend.axis("off")
    for i, (key, label) in enumerate(labels.items()):
        yy = 0.82 - i * 0.2
        legend.add_patch(plt.Rectangle((0.0, yy - 0.035), 0.07, 0.07, color=colours[i], transform=legend.transAxes))
        legend.text(0.11, yy + 0.02, f"{data[key]}", fontsize=12, fontweight="bold", color=INK, va="center")
        legend.text(0.11, yy - 0.06, label, fontsize=8.5, color=MUTED, va="center")
    bars = fig.add_axes((0.775, 0.12, 0.2, 0.64))
    functions = sorted(summary["system_functions"].items(), key=lambda kv: kv[1])
    bars.barh([k for k, _ in functions], [v for _, v in functions], color=TEAL, height=0.6)
    for i, (_, v) in enumerate(functions):
        bars.text(v + 0.6, i, str(v), va="center", fontsize=9, color=INK)
    bars.set_title("System function calls", fontsize=10, color=INK, loc="left", fontweight="bold")
    bars.grid(axis="x", color=GRID)
    bars.set_axisbelow(True)
    bars.tick_params(axis="y", length=0, labelsize=8.5)
    _save(fig, path)


def tag_chart(tags: list[dict[str, str]], path: Path) -> None:
    def source(tag: dict[str, str]) -> str:
        if tag["connection"].startswith("<"):
            return "Internal tag"
        return tag["plc_tag"].split(".")[0].strip('"')

    types = ["Bool", "Int", "Real", "String", "WString"]
    colours = {"Bool": TEAL, "Int": "#4f7cac", "Real": "#f2a541", "String": "#a7b1bc", "WString": "#d3d8de"}
    counts = Counter((source(t), t["data_type"]) for t in tags)
    sources = sorted({s for s, _ in counts}, key=lambda s: sum(v for (src, _), v in counts.items() if src == s))
    fig, ax = plt.subplots(figsize=(10, 4.4))
    fig.subplots_adjust(left=0.2, right=0.97, top=0.72, bottom=0.12)
    left = [0] * len(sources)
    for t in types:
        values = [counts.get((s, t), 0) for s in sources]
        ax.barh(sources, values, left=left, color=colours[t], label=t, height=0.6, edgecolor="white", linewidth=0.6)
        left = [a + b for a, b in zip(left, values)]
    for i, total in enumerate(left):
        ax.text(total + 0.8, i, str(total), va="center", fontsize=9, color=INK, fontweight="bold")
    ax.set_xlim(0, max(left) * 1.08)
    ax.set_xlabel("HMI tags")
    ax.grid(axis="x", color=GRID)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", length=0)
    ax.legend(ncol=5, loc="lower left", bbox_to_anchor=(-0.22, 1.02), frameon=False, fontsize=8.5)
    _title(fig, "Where the HMI tags come from",
           f"{len(tags)} HMI tags, grouped by the S7-1500 data block they read and write (symbolic access)")
    _save(fig, path)


def io_chart(io: list[dict[str, str]], path: Path) -> None:
    def subsystem(signal: str) -> tuple[str, str]:
        return next((label, colour) for key, label, colour in SUBSYSTEMS if key in signal)

    def short(signal: str) -> str:
        for a, b in (("Resin Enhancer", "Resin"), ("Solvent Binder", "Binder"), (" Pigment", ""),
                     ("Sensor", "sens."), ("Level", "level"), ("Overflow", "overflow"), ("Master ", ""),
                     ("High-Temperature", "high temp."), ("High-Pressure", "high press."), (" ON", ""),
                     ("Mixing Tank", "Mix tank"), ("Indicator", "ind."), ("Actuator", "act."),
                     ("Circulation", "circ."), ("Interlock Engaged", "interlock"), ("Emergency Stop", "E-stop"),
                     ("Maintenance", "Maint."), ("Exhaust ", ""), ("Complete", "done")):
            signal = signal.replace(a, b)
        words, lines, line = signal.split(), [], ""
        for w in words:
            if len(line) + len(w) > 14 and line:
                lines.append(line)
                line = w
            else:
                line = f"{line} {w}".strip()
        lines.append(line)
        return "\n".join(lines[:2])

    by_address = {r["address"]: r for r in io}
    fig = plt.figure(figsize=(11, 5.6))
    _title(fig, "Process image at a glance",
           f"{sum(r['direction'] == 'input' for r in io)} digital inputs and "
           f"{sum(r['direction'] == 'output' for r in io)} digital outputs shown on the I/O status screens")
    used: dict[str, str] = {}
    for p, (prefix, name) in enumerate((("I", "Digital inputs"), ("Q", "Digital outputs"))):
        ax = fig.add_axes((0.06 + p * 0.475, 0.16, 0.44, 0.62))
        ax.set_xlim(0, 4)
        ax.set_ylim(0, 6)
        ax.axis("off")
        ax.text(0, 6.15, name, fontsize=11, fontweight="bold", color=INK)
        for byte in range(3):
            for bit in range(8):
                col, row = bit % 4, 5 - (byte * 2 + bit // 4)
                address = f"{prefix}{byte}.{bit}"
                signal = by_address.get(address)
                label, colour = subsystem(signal["signal"]) if signal else ("", "#f1f3f5")
                if signal:
                    used[label] = colour
                ax.add_patch(plt.Rectangle((col + 0.04, row + 0.06), 0.92, 0.88, color=colour,
                                           alpha=0.95 if signal else 1, linewidth=0))
                ax.text(col + 0.1, row + 0.8, address, fontsize=7.5, fontweight="bold",
                        color="white" if signal else "#aab4be", va="top")
                if signal:
                    ax.text(col + 0.1, row + 0.52, short(signal["signal"]), fontsize=6.6, color="white",
                            va="top", linespacing=1.15)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in used.values()]
    fig.legend(handles, list(used), ncol=4, loc="lower center", frameon=False, fontsize=8.5, bbox_to_anchor=(0.5, 0.0))
    _save(fig, path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--data", type=Path, default=Path("data"))
    parser.add_argument("--out", type=Path, default=Path("assets/charts"))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    summary = json.loads((args.data / "summary.json").read_text(encoding="utf-8"))
    composition_chart(_read(args.data / "screens.csv"), args.out / "screen-composition.svg")
    dynamics_chart(summary, args.out / "dynamics.svg")
    tag_chart(_read(args.data / "hmi_tags.csv"), args.out / "tag-sources.svg")
    io_chart(_read(args.data / "io_map.csv"), args.out / "io-map.svg")


if __name__ == "__main__":
    main()
