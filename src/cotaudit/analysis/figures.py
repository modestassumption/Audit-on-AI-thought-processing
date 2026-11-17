"""Week 7 figures (proposal 4.7; owner: sub-team D), written as plain SVG.

No plotting library: the project's dependencies (pyproject.toml) have none, so the two chart
forms the report needs are drawn directly. SVG files open in a browser and drop into the
report (Word, Google Docs and LaTeX via svg/inkscape all take them).

- `interval_chart`: one row per cell (e.g. model x language), one dot per series (e.g. hint
  type) with its 95% interval as a whisker. Linear axis for rates, log axis for odds ratios,
  optional reference line (1 for odds ratios, 0 for differences).
- `stacked_bars`: one 100% bar per row, split into parts (e.g. which language the reasoning
  is in), each part's share printed inside when it fits.

Every mark carries an SVG <title>, so hovering in a browser shows the exact numbers.
Colours: the first slots of a colour-blind-checked categorical order; text stays in grey ink,
never in a series colour.
"""

from __future__ import annotations

import math
from xml.sax.saxutils import escape

SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]   # blue, orange, aqua, yellow
NEUTRAL = "#a3a29c"                                      # "mixed" / other
LIGHT_FILLS = {"#1baf7a", "#eda100", NEUTRAL}            # print dark text on these
SURFACE, INK, INK_2, MUTED, GRID = "#ffffff", "#0b0b0b", "#52514e", "#8a8984", "#e6e5e0"
FONT = "font-family='Helvetica, Arial, sans-serif'"

RIGHT, TOP_TITLE, WIDTH = 30, 28, 760
NICE = [0.05, 0.1, 0.2, 0.25, 0.5, 0.75, 1, 1.5, 2, 3, 4, 5, 10, 20]


def pct(x: float) -> str:
    return f"{100 * x:.0f}%"


def _num(x) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return math.nan


def _text(x, y, s, size=12, fill=INK_2, anchor="start", weight="normal") -> str:
    return (f"<text x='{x:.1f}' y='{y:.1f}' font-size='{size}' fill='{fill}' text-anchor='{anchor}' "
            f"font-weight='{weight}' {FONT}>{escape(str(s))}</text>")


def _svg(height: float, body: list[str], title: str) -> str:
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{WIDTH}' height='{height:.0f}' "
            f"viewBox='0 0 {WIDTH} {height:.0f}' role='img'>\n<title>{escape(title)}</title>\n"
            f"<rect width='100%' height='100%' fill='{SURFACE}'/>\n" + "\n".join(body) + "\n</svg>\n")


def _left(labels) -> float:
    """Left margin wide enough for the longest row label (about 6.6 px per character at 12 px)."""
    return max(90.0, 22 + 6.6 * max((len(str(l)) for l in labels), default=0))


def _legend(names: list[str], colors: list[str], y: float, x: float) -> list[str]:
    out = []
    for name, color in zip(names, colors):
        out.append(f"<rect x='{x}' y='{y - 9}' width='10' height='10' rx='2' fill='{color}'/>")
        out.append(_text(x + 15, y, name))
        x += 30 + 7 * len(str(name))
    return out


def log_ticks(lo: float, hi: float) -> list[float]:
    """Round values inside [lo, hi] for an odds-ratio axis; powers of 2 when the range is wide."""
    ticks = [t for t in NICE if lo <= t <= hi]
    if 3 <= len(ticks) <= 9:
        return ticks
    ticks = [2.0 ** k for k in range(math.ceil(math.log2(lo)), math.floor(math.log2(hi)) + 1)]
    return ticks if len(ticks) <= 9 else ticks[::2]


def interval_chart(rows: list[dict], series: list[str], *, title: str, x_label: str,
                   x_min: float = 0.0, x_max: float = 1.0, log: bool = False, ref: float | None = None,
                   fmt=pct, ticks: list[float] | None = None) -> str:
    """Dot-and-whisker chart. Each row dict: `row` (label), `series` (one of `series`),
    `value`, `low`, `high`, optional `n` (shown in the hover text). Rows keep their first-seen
    order; a missing or NaN value draws nothing for that series."""
    labels = list(dict.fromkeys(r["row"] for r in rows))
    colors = {s: SERIES[i % len(SERIES)] for i, s in enumerate(series)}
    step = 14                                           # vertical gap between series in a row
    band = 10 + step * len(series)
    legend_y = TOP_TITLE + 24 if len(series) > 1 else TOP_TITLE
    top = legend_y + 18
    left = _left(labels)
    plot_w = WIDTH - left - RIGHT
    height = top + band * len(labels) + 46

    if log:
        x_min = max(x_min, 1e-3)
        f = lambda v: left + plot_w * (math.log(v) - math.log(x_min)) / (math.log(x_max) - math.log(x_min))
        ticks = ticks or log_ticks(x_min, x_max)
    else:
        f = lambda v: left + plot_w * (v - x_min) / (x_max - x_min)
        ticks = ticks or [x_min + (x_max - x_min) * i / 5 for i in range(6)]
    clamp = lambda v: min(max(v, x_min), x_max)

    body = [_text(12, TOP_TITLE - 8, title, size=14, fill=INK, weight="bold")]
    if len(series) > 1:
        body += _legend(series, [colors[s] for s in series], legend_y, left)
    bottom = top + band * len(labels)
    for i in range(1, len(labels), 2):                  # zebra stripes first, under grid and marks
        body.append(f"<rect x='0' y='{top + i * band}' width='{WIDTH}' height='{band}' fill='#f6f6f4'/>")
    for t in ticks:
        x = f(t)
        body.append(f"<line x1='{x:.1f}' y1='{top}' x2='{x:.1f}' y2='{bottom}' stroke='{GRID}' stroke-width='1'/>")
        body.append(_text(x, bottom + 16, fmt(t), size=11, fill=MUTED, anchor="middle"))
    if ref is not None and x_min <= ref <= x_max:
        x = f(ref)
        body.append(f"<line x1='{x:.1f}' y1='{top}' x2='{x:.1f}' y2='{bottom}' stroke='{INK_2}' "
                    f"stroke-width='1' stroke-dasharray='4 3'/>")
    body.append(_text(left + plot_w / 2, bottom + 36, x_label, size=12, anchor="middle"))

    by_cell = {(r["row"], r["series"]): r for r in rows}
    for i, label in enumerate(labels):
        y0 = top + i * band
        body.append(_text(left - 10, y0 + band / 2 + 4, label, anchor="end"))
        for j, s in enumerate(series):
            r = by_cell.get((label, s))
            if r is None or math.isnan(_num(r.get("value"))):
                continue
            v, lo, hi = _num(r["value"]), _num(r.get("low")), _num(r.get("high"))
            if log and v <= 0:
                continue
            y = y0 + 5 + step * j + step / 2
            tip = f"{label}, {s}: {fmt(v)}"
            if not (math.isnan(lo) or math.isnan(hi)):
                tip += f" (95% interval {fmt(lo)} to {fmt(hi)})"
                lo_x, hi_x = f(clamp(max(lo, x_min))), f(clamp(hi))
                body.append(f"<line x1='{lo_x:.1f}' y1='{y:.1f}' x2='{hi_x:.1f}' y2='{y:.1f}' "
                            f"stroke='{colors[s]}' stroke-width='2' stroke-linecap='round'/>")
            if r.get("n") is not None:
                tip += f", n = {r['n']}"
            body.append(f"<circle cx='{f(clamp(v)):.1f}' cy='{y:.1f}' r='4.5' fill='{colors[s]}' "
                        f"stroke='{SURFACE}' stroke-width='2'><title>{escape(tip)}</title></circle>")
    return _svg(height, body, title)


def stacked_bars(rows: list[tuple[str, dict[str, int]]], parts: list[str], *, title: str,
                 colors: dict[str, str] | None = None) -> str:
    """One 100% bar per row: `rows` is [(label, {part: count})]. The total is printed at the
    right; a part's share is printed inside it when the block is wide enough."""
    colors = colors or {p: SERIES[i % len(SERIES)] for i, p in enumerate(parts)}
    bar_h, gap_y = 24, 12
    legend_y = TOP_TITLE + 24
    top = legend_y + 18
    left = _left([r[0] for r in rows])
    plot_w = WIDTH - left - RIGHT - 50
    height = top + (bar_h + gap_y) * len(rows) + 14
    body = [_text(12, TOP_TITLE - 8, title, size=14, fill=INK, weight="bold")]
    body += _legend(parts, [colors[p] for p in parts], legend_y, left)
    for i, (label, counts) in enumerate(rows):
        y = top + i * (bar_h + gap_y)
        total = sum(counts.get(p, 0) for p in parts)
        body.append(_text(left - 10, y + bar_h / 2 + 4, label, anchor="end"))
        body.append(_text(left + plot_w + 8, y + bar_h / 2 + 4, f"n = {total}", size=11, fill=MUTED))
        if not total:
            continue
        x = left
        for p in parts:
            k = counts.get(p, 0)
            if not k:
                continue
            w = plot_w * k / total
            share = k / total
            body.append(f"<rect x='{x + 1:.1f}' y='{y}' width='{max(w - 2, 0.5):.1f}' height='{bar_h}' rx='4' "
                        f"fill='{colors[p]}'><title>{escape(f'{label}: {k} of {total} in {p} ({pct(share)})')}"
                        f"</title></rect>")
            if w >= 38:
                ink = INK if colors[p] in LIGHT_FILLS else SURFACE
                body.append(_text(x + 7, y + bar_h / 2 + 4, pct(share), size=11, fill=ink))
            x += w
    return _svg(height, body, title)
