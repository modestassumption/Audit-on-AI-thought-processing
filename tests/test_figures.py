import importlib.util
import math
import xml.etree.ElementTree as ET

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from cotaudit.analysis.figures import SERIES, interval_chart, log_ticks, stacked_bars

NS = "{http://www.w3.org/2000/svg}"


def parse(svg: str) -> ET.Element:
    return ET.fromstring(svg)                       # fails if the SVG is not well-formed XML


def circles(root: ET.Element) -> list[ET.Element]:
    return root.findall(f".//{NS}circle")


def row(label, series, value, low=None, high=None, n=None):
    return {"row": label, "series": series, "value": value, "low": low, "high": high, "n": n}


def test_dots_sit_at_their_value_and_whiskers_span_the_interval():
    svg = interval_chart([row("a", "s", 0.0, 0.0, 0.2), row("b", "s", 1.0, 0.8, 1.0), row("c", "s", 0.5, 0.3, 0.7)],
                         ["s"], title="t", x_label="x")
    root = parse(svg)
    xs = [float(c.get("cx")) for c in circles(root)]
    assert xs[2] == pytest.approx((xs[0] + xs[1]) / 2)          # 0.5 is halfway between 0 and 1
    whiskers = [ln for ln in root.findall(f".//{NS}line") if ln.get("stroke") == SERIES[0]]
    assert len(whiskers) == 3
    w = whiskers[2]
    span = xs[1] - xs[0]
    assert float(w.get("x1")) == pytest.approx(xs[0] + 0.3 * span)
    assert float(w.get("x2")) == pytest.approx(xs[0] + 0.7 * span)


def test_series_get_fixed_colours_and_missing_values_draw_nothing():
    rows = [row("a", "expert", 0.2), row("a", "leaked", 0.4), row("b", "expert", math.nan), row("b", "metadata", 0.3)]
    root = parse(interval_chart(rows, ["expert", "metadata", "leaked"], title="t", x_label="x"))
    fills = [c.get("fill") for c in circles(root)]
    assert fills == [SERIES[0], SERIES[2], SERIES[1]]            # colour follows the series, not the order drawn


def test_hover_text_and_labels_are_escaped():
    svg = interval_chart([row("R&D <x>", "s", 0.25, 0.1, 0.4, n=12)], ["s"], title="a < b", x_label="x")
    root = parse(svg)
    tip = circles(root)[0].find(f"{NS}title").text
    assert tip == "R&D <x>, s: 25% (95% interval 10% to 40%), n = 12"


def test_log_axis_and_reference_line():
    assert log_ticks(0.5, 2.0) == [0.5, 0.75, 1, 1.5, 2]
    assert log_ticks(0.01, 100) == [2.0 ** k for k in range(-6, 7, 2)]
    svg = interval_chart([row("a", "or", 0.5, 0.25, 1.0), row("b", "or", 2.0, 1.0, 4.0), row("c", "or", 1.0)],
                         ["or"], title="t", x_label="x", x_min=0.25, x_max=4, log=True, ref=1.0)
    xs = [float(c.get("cx")) for c in circles(parse(svg))]
    assert xs[2] - xs[0] == pytest.approx(xs[1] - xs[2])         # 0.5 and 2 are equally far from 1
    assert "stroke-dasharray" in svg


def test_stacked_bar_widths_are_proportional():
    root = parse(stacked_bars([("m · ml", {"en": 3, "ml": 1, "mixed": 0}), ("empty", {})], ["en", "ml", "mixed"],
                              title="t"))
    rects = [r for r in root.findall(f".//{NS}rect") if r.find(f"{NS}title") is not None]
    assert len(rects) == 2                                        # a zero part and an empty row draw nothing
    w = [float(r.get("width")) + 2 for r in rects]                # each block gives up a 2 px gap
    assert w[0] == pytest.approx(3 * w[1])
    assert rects[0].find(f"{NS}title").text == "m · ml: 3 of 4 in en (75%)"


def load_script():
    """scripts/figures.py, loaded by path (its module name would clash with cotaudit.analysis.figures)."""
    path = Path(__file__).resolve().parents[1] / "scripts" / "figures.py"
    spec = importlib.util.spec_from_file_location("figures_script", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_script_charts_from_runs():
    script = load_script()
    rng = np.random.default_rng(1)
    runs = []
    for q in range(40):
        for lang in ("en", "hi"):
            hints = [("expert", lang), ("leaked", lang)] + ([("expert", "en")] if lang != "en" else [])
            for hint, hint_lang in hints:
                runs.append({"model": "m", "qid": f"q{q}", "lang": lang, "hint_type": hint, "hint_lang": hint_lang,
                             "influenced": int(rng.random() < 0.3), "undetermined": False,
                             "reasoning": "The answer is B." if rng.random() < 0.5 else "उत्तर B है"})
    det = pd.DataFrame(runs)
    same = det[det["hint_lang"] == det["lang"]]
    svg = script.hint_rate_chart(same, "influenced", ["expert", "metadata", "leaked"], "t", "x", 200, 21)
    assert len(circles(parse(svg))) == 4                         # 2 languages x 2 hint types present
    h4 = script.h4_chart(det, "influenced", "t", "x", 200, 21)
    assert len(circles(parse(h4))) == 2                          # Hindi only: English vs. own-language hint
    assert script.h4_chart(same, "influenced", "t", "x", 200, 21) is None   # no English hints: no H4 figure
    lang = parse(script.language_chart(det, 0.6, 200, 21))
    labels = [t.text for t in lang.findall(f".//{NS}text")]
    assert "m · English questions" in labels and "m · Hindi questions" in labels
