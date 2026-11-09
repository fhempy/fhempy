"""HTML of the detail page: what the advisor learned and recommends, with
two small SVG charts. Colors follow the FHEMWEB style (currentColor)."""

import html

STYLE = """<style>
.fha{max-width:900px;margin:0 0 16px 0;line-height:1.45}
.fha h3{margin:14px 0 6px 0}
.fha .big{font-size:1.25em;font-weight:bold;margin:4px 0}
.fha .muted{opacity:.7}
.fha .scroll{overflow-x:auto}
.fha table{border-collapse:collapse;width:100%;margin:6px 0}
.fha td,.fha th{padding:4px 8px;border-bottom:1px solid rgba(128,128,128,.3);
text-align:left;vertical-align:top}
.fha td.n,.fha th.n{text-align:right;white-space:nowrap}
.fha svg{width:100%;height:auto;max-width:900px}
.fha .air{stroke:#e07a2f;fill:none;stroke-width:2}
.fha .felt{stroke:#3b82c4;fill:none;stroke-width:2.5}
.fha .wall{stroke:#8a8a8a;fill:none;stroke-width:1.5;stroke-dasharray:4 3}
.fha .grid{stroke:rgba(128,128,128,.25);stroke-width:1}
.fha .bar{fill:#3b82c4}
.fha .bar.no{fill:rgba(128,128,128,.45)}
.fha text{fill:currentColor;font-size:11px}
.fha .legend span{display:inline-block;margin-right:14px}
.fha .sw{display:inline-block;width:14px;height:3px;vertical-align:middle;
margin-right:4px}
</style>"""


def esc(text):
    return html.escape(str(text), quote=True)


def fmt(value, digits=1, unit=""):
    if value is None:
        return "–"
    return f"{value:.{digits}f}{unit}"


def line_chart(series, hours, width=880, height=220):
    """series: list of (css class, list of values per point)"""
    values = [v for _, points in series for v in points if v is not None]
    if not values:
        return ""
    low, high = min(values), max(values)
    low, high = int(low - 1), int(high + 1.999)
    left, right, top, bottom = 34, 24, 10, 22
    w, h = width - left - right, height - top - bottom
    n = max(len(series[0][1]) - 1, 1)

    def x(i):
        return left + w * i / n

    def y(v):
        return top + h * (high - v) / max(high - low, 1)

    parts = [f'<svg viewBox="0 0 {width} {height}" role="img">']
    step = 1 if high - low <= 8 else 2
    for t in range(low, high + 1, step):
        parts.append(
            f'<line class="grid" x1="{left}" x2="{width - right}" '
            f'y1="{y(t):.1f}" y2="{y(t):.1f}"/>'
            f'<text x="{left - 4}" y="{y(t) + 4:.1f}" text-anchor="end">{t}°</text>'
        )
    every = max(hours // 8, 1)
    for hour in range(0, hours + 1, every):
        xi = x(hour * n / hours)
        parts.append(
            f'<text x="{xi:.1f}" y="{height - 6}" text-anchor="middle">+{hour} h</text>'
        )
    for css, points in series:
        coords = " ".join(
            f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(points) if v is not None
        )
        parts.append(f'<polyline class="{esc(css)}" points="{coords}"/>')
    parts.append("</svg>")
    return "".join(parts)


def bar_chart(results, threshold_pct, width=880, height=200):
    if not results:
        return ""
    left, right, top, bottom = 34, 10, 10, 22
    w, h = width - left - right, height - top - bottom
    high = max(max(r["saving_pct"] for r in results), threshold_pct, 5)
    high = (int(high / 5) + 1) * 5
    bar_w = w / len(results)
    parts = [f'<svg viewBox="0 0 {width} {height}" role="img">']
    for t in range(0, high + 1, 5 if high <= 30 else 10):
        yy = top + h * (1 - t / high)
        parts.append(
            f'<line class="grid" x1="{left}" x2="{width - right}" y1="{yy:.1f}" '
            f'y2="{yy:.1f}"/><text x="{left - 4}" y="{yy + 4:.1f}" '
            f'text-anchor="end">{t}%</text>'
        )
    for i, r in enumerate(results):
        pct = max(r["saving_pct"], 0)
        bh = h * pct / high
        css = "bar" if pct >= threshold_pct else "bar no"
        xx = left + i * bar_w + 3
        hours = r["hours"]
        label = f"{hours}h" if hours < 48 else f"{hours // 24}d"
        parts.append(
            f'<rect class="{css}" x="{xx:.1f}" y="{top + h - bh:.1f}" '
            f'width="{bar_w - 6:.1f}" height="{bh:.1f}"><title>{label}: '
            f"{pct:.1f}% / {r['saving_kwh']:.1f} kWh</title></rect>"
            f'<text x="{xx + (bar_w - 6) / 2:.1f}" y="{height - 6}" '
            f'text-anchor="middle">{label}</text>'
        )
    parts.append("</svg>")
    return "".join(parts)


def page(view):
    """view: dict prepared by the module (see heating_advisor.detail_view)"""
    if not view:
        return (
            STYLE + '<div class="fha"><p>The heating advisor is starting, '
            "this page shows what it learned in a few minutes.</p></div>"
        )
    out = [STYLE, '<div class="fha">']
    out.append(f'<div class="big">{esc(view["headline"])}</div>')
    out.append(f'<div class="muted">{esc(view["subline"])}</div>')
    for text in view.get("explain", []):
        out.append(f"<p>{esc(text)}</p>")
    curve = view.get("curve")
    if curve:
        out.append("<h3>If you leave now and turn the heating off</h3>")
        out.append(
            '<div class="legend muted">'
            '<span><i class="sw" style="background:#3b82c4"></i>felt</span>'
            '<span><i class="sw" style="background:#e07a2f"></i>air</span>'
            '<span><i class="sw" style="background:#8a8a8a"></i>walls</span>'
            "</div>"
        )
        out.append(
            line_chart(
                [
                    ("wall", curve["wall"]),
                    ("air", curve["air"]),
                    ("felt", curve["felt"]),
                ],
                curve["hours"],
            )
        )
    if view.get("savings"):
        out.append("<h3>Saving by length of absence</h3>")
        out.append(bar_chart(view["savings"], view["threshold_pct"]))
        out.append(
            '<div class="muted">Blue: worth it (at least '
            f"{view['threshold_pct']:g}% and {view['threshold_kwh']:g} kWh). "
            "Includes heating up the walls again until it feels warm.</div>"
        )
    if view.get("rooms"):
        out.append(
            "<h3>Rooms</h3><table><tr><th>Room</th><th class='n'>Air</th>"
            "<th class='n'>Walls</th><th class='n'>Felt</th>"
            "<th class='n'>Off 24 h</th><th class='n'>Worth from</th>"
            "<th class='n'>Heat up</th><th>Model</th></tr>"
        )
        for r in view["rooms"]:
            out.append(
                f"<tr><td>{esc(r['name'])}</td>"
                f"<td class='n'>{fmt(r.get('air'), 1, '°')}</td>"
                f"<td class='n'>{fmt(r.get('wall'), 1, '°')}</td>"
                f"<td class='n'>{fmt(r.get('felt'), 1, '°')}</td>"
                f"<td class='n'>{fmt(r.get('off24'), 1, '°')}</td>"
                f"<td class='n'>{esc(r.get('worth', '–'))}</td>"
                f"<td class='n'>{fmt(r.get('reheat'), 1, ' h')}</td>"
                f"<td>{esc(r.get('model', ''))}</td></tr>"
            )
        out.append("</table></div>")
    if view.get("devices"):
        out.append("<h3>Devices used</h3><table>")
        for room, names in view["devices"]:
            out.append(f"<tr><td>{esc(room)}</td><td>{esc(', '.join(names))}</td></tr>")
        out.append(
            "</table><div class='muted'>Not right? Add devices to the attribute "
            "exclude_devices or extra_devices.</div>"
        )
    out.append("</div>")
    return "".join(out)
