import json
from pathlib import Path

import build_charts

ROOT = Path(__file__).resolve().parents[1]


def test_charts_render(tmp_path):
    data = ROOT / "data"
    summary = json.loads((data / "summary.json").read_text(encoding="utf-8"))
    build_charts.composition_chart(build_charts._read(data / "screens.csv"), tmp_path / "a.svg")
    build_charts.dynamics_chart(summary, tmp_path / "b.svg")
    build_charts.tag_chart(build_charts._read(data / "hmi_tags.csv"), tmp_path / "c.svg")
    build_charts.io_chart(build_charts._read(data / "io_map.csv"), tmp_path / "d.svg")
    for name in "abcd":
        svg = (tmp_path / f"{name}.svg").read_text(encoding="utf-8")
        assert svg.lstrip().startswith("<?xml") and "<svg" in svg
