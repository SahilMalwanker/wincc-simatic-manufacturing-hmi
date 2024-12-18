import csv
import json

import pytest

import tia_printout as tp


def _cell(x, text, bold):
    return tp.Cell(x, text, bold)


# --------------------------------------------------------------------------- layout rules


def test_hyphenated_key_is_joined_without_hyphen():
    previous = tp.Row([_cell(314, "Communication driv\u2010", True), _cell(408, "SIMATIC S7 1500", False)])
    row = tp.Row([_cell(314, "er", True)])
    assert tp._is_continuation(row, previous)
    tp._merge(row, previous)
    assert previous.cells[0].text == "Communication driver"


def test_long_identifier_wraps_without_space():
    previous = tp.Row([_cell(64, "Name", True), _cell(158, "Paramters_Paint_Mix_Act_Green_Tank_Te", False)])
    row = tp.Row([_cell(158, "mp", False)])
    assert tp._is_continuation(row, previous)
    tp._merge(row, previous)
    assert previous.cells[1].text == "Paramters_Paint_Mix_Act_Green_Tank_Temp"


def test_wrapped_text_keeps_word_boundary():
    previous = tp.Row([_cell(64, "Text", True), _cell(158, "I0.0 - Resin Enhancer Level Sensor", False)])
    row = tp.Row([_cell(158, "Low", False)])
    tp._merge(row, previous)
    assert previous.cells[1].text == "I0.0 - Resin Enhancer Level Sensor Low"


def test_new_property_is_not_a_continuation():
    previous = tp.Row([_cell(64, "Comment", True)])
    row = tp.Row([_cell(64, "Comment", True)])
    assert not tp._is_continuation(row, previous)


def test_props_pair_bold_keys_with_values():
    record = tp.Record("PainMix_DB_RED_Pipe", "HMI tags")
    tp._add_props(record, tp.Row([_cell(64, "Name", True), _cell(158, "PainMix_DB_RED_Pipe", False),
                                  _cell(314, "Display name", True), _cell(565, "Connection", True),
                                  _cell(660, "HMI_Connection_1", False)]))
    assert record.get("Display name") == ""
    assert record.get("Connection") == "HMI_Connection_1"


# --------------------------------------------------------------------------- full printout


def test_device_and_connection(printout):
    s = tp.summary(printout)
    assert s["device"]["type"] == "TP700 Comfort"
    assert s["device"]["resolution"] == "800, 480"
    assert s["device"]["runtime_languages"] == ["English (United States)", "German (Germany)"]
    assert s["connection"]["driver"] == "SIMATIC S7 1500"
    assert s["connection"]["node"].startswith("CPU 1516-3 PN/DP")


def test_screen_inventory(printout):
    kinds = {}
    for screen in printout.screens:
        kinds.setdefault(screen.record.kind, []).append(screen.name)
    assert sorted(kinds["screen"]) == ["Alarm", "Company_Details", "Input_Status", "MainOverview",
                                       "Output_Status", "Parameter", "Recipe", "User_Admin"]
    assert len(kinds["pop-up"]) == 7
    assert sorted(kinds["template"]) == ["Inputs_temp", "Outputs_temp", "PaintMix"]
    assert sum(len(s.objects) for s in printout.screens) == 581
    assert all(o.kind for s in printout.screens for o in s.objects)


def test_animations_and_functions(printout):
    s = tp.summary(printout)
    assert s["animations"] == {"Visibility": 136, "Appearance": 72, "Event": 66, "Tag connection": 53}
    assert s["system_functions"]["ActivateScreen"] == 40
    assert s["graphic_lists"]["Pump_Fan_Red"] == 4


def test_hmi_tags(printout):
    tags = tp.tag_rows(printout)
    assert len(tags) == 117
    by_name = {t["name"]: t for t in tags}
    assert by_name["Paramters_Paint_Mix_Act_Green_Tank_Temp"]["plc_tag"] == "Paramters_Paint_Mix.Act_Green_Tank_Temp"
    assert by_name["UserName_fromHMI"]["connection"] == "<Internal tag>"
    assert by_name["MainT_Agitator"]["table"] == "Paint_Mix"


def test_io_map(printout):
    io = tp.io_rows(printout)
    assert [r["address"] for r in io][:2] == ["I0.0", "I0.1"]
    assert sum(r["direction"] == "input" for r in io) == 20
    assert sum(r["direction"] == "output" for r in io) == 20
    assert io[0]["signal"] == "Resin Enhancer Level Sensor Low"


def test_alarm_tiles(printout):
    rows = tp.alarm_rows(printout)
    assert sum(r["group"] == "warning" for r in rows) == 12
    assert sum(r["group"] == "alarm" for r in rows) == 12
    assert {"Tank Overfill", "PLC Comm. Loss", "Filter Maintenance"} <= {r["label"] for r in rows}


def test_recipes_users_and_navigation(printout):
    recipe = tp.recipe_rows(printout)
    assert len(recipe) == 10
    assert recipe[0]["display_name"] == "Pigment Concentration (%)"
    groups = {g["group"]: g["authorizations"] for g in tp.group_rows(printout)}
    assert groups["Engineer group"] == "Monitor"
    nav = {(r["screen"], r["target"]) for r in tp.navigation_rows(printout)}
    assert ("PaintMix", "Alarm") in nav
    assert ("MainOverview", "BatchDetails") in nav


@pytest.mark.parametrize("name", [
    "hmi_tags.csv", "screens.csv", "screen_objects.csv", "navigation.csv", "io_map.csv",
    "alarm_indicators.csv", "recipe_elements.csv", "user_groups.csv",
])
def test_committed_tables_are_up_to_date(printout, root, name):
    expected = [{k: str(v) for k, v in row.items()} for row in tp.tables(printout)[name]]
    with (root / "data" / name).open(encoding="utf-8") as fh:
        committed = list(csv.DictReader(fh))
    assert committed == expected, f"data/{name} is stale - re-run tools/tia_printout.py"


def test_committed_summary_is_up_to_date(printout, root):
    committed = json.loads((root / "data" / "summary.json").read_text(encoding="utf-8"))
    assert committed == json.loads(json.dumps(tp.summary(printout)))
