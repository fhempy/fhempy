/*
 * Timeline of the fhempy module timeline on its detail page.
 * fhempyTimeline(device): loads the last days with get <device> entries and
 * shows them as story per day. Older days are loaded on demand, hidden events
 * of a day with get <device> details <day>.
 */
(function () {
  "use strict";

  var device = "";
  var days = [];
  var periods = [];
  var firstDay = "";
  var loading = false;
  var keepScroll = true;
  var expanded = {};
  var wide = false;
  var WIDE_MIN = 1100;
  var NARROW_MAX = 520;
  var filter = { categories: {}, search: "" };

  var categoryInfo = {
    security: { title: "Security", color: "#d0662a" },
    presence: { title: "Presence", color: "#7a5cc4" },
    light: { title: "Light", color: "#d4a514" },
    climate: { title: "Climate", color: "#2f8fc4" },
    energy: { title: "Energy", color: "#3d9a50" },
    devices: { title: "Devices", color: "#8a8f94" }
  };

  function esc(t) { return $("<div>").text(t === undefined || t === null ? "" : String(t)).html(); }

  function storageGet(key) {
    try { return window.localStorage.getItem("fhempyTimeline." + key); } catch (e) { return null; }
  }

  function storageSet(key, value) {
    try { window.localStorage.setItem("fhempyTimeline." + key, value); } catch (e) { /* private mode */ }
  }

  function css() {
    if ($("#fhempyTimelineCss").length) return;
    $("head").append('<style id="fhempyTimelineCss">' +
      "#fhempyTimeline{max-width:900px;margin:0 0 20px;font-family:'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif;line-height:1.4}" +
      "#fhempyTimeline .ftlBar{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:0 0 8px}" +
      "#fhempyTimeline .ftlTitle{font-size:18px;font-weight:600;margin-right:auto}" +
      "#fhempyTimeline .ftlChip{border:1px solid rgba(128,128,128,0.4);border-radius:14px;padding:2px 11px;cursor:pointer;font-size:13px;white-space:nowrap;user-select:none}" +
      "#fhempyTimeline .ftlChip.ftlOn{border-color:transparent;background:rgba(75,139,190,0.18)}" +
      "#fhempyTimeline .ftlChip .ftlDot{margin-right:5px}" +
      "#fhempyTimeline .ftlPeriod{background:rgba(208,102,42,0.14);border-color:transparent}" +
      "#fhempyTimeline input.ftlSearch{border-radius:14px;padding:3px 10px;border:1px solid rgba(128,128,128,0.4);min-width:140px}" +
      "#fhempyTimeline input.ftlDate{border-radius:14px;padding:2px 8px;border:1px solid rgba(128,128,128,0.4)}" +
      "#fhempyTimeline.ftlRoom{max-width:none;margin-top:6px}" +
      "#fhempyTimeline.ftlWideMode .ftlDay{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(0,1fr);column-gap:36px;align-items:start}" +
      "#fhempyTimeline.ftlWideMode .ftlDayHead{grid-column:1/-1}" +
      "#fhempyTimeline.ftlWideMode .ftlDaySide .ftlHiddenRow{padding-left:0}" +
      "#fhempyTimeline.ftlWideMode .ftlDaySide .ftlTrends{margin-left:0;grid-template-columns:repeat(auto-fill,minmax(min(220px,100%),1fr))}" +
      "#fhempyTimeline.ftlNarrow .ftlEntry{grid-template-columns:40px 10px minmax(0,1fr);gap:6px}" +
      "#fhempyTimeline.ftlNarrow .ftlActions{grid-column:3;justify-content:flex-start}" +
      "#fhempyTimeline.ftlNarrow .ftlAction{opacity:0.6}" +
      "#fhempyTimeline.ftlNarrow .ftlTrends,#fhempyTimeline.ftlNarrow .ftlHiddenRow,#fhempyTimeline.ftlNarrow .ftlQuiet{margin-left:0;padding-left:0}" +
      "#fhempyTimeline .ftlScroll{overflow-y:auto;overscroll-behavior:contain;-webkit-overflow-scrolling:touch;padding-right:4px}" +
      "#fhempyTimeline .ftlDay{border-top:1px solid rgba(128,128,128,0.3);padding:10px 0 6px}" +
      "#fhempyTimeline .ftlDayHead{display:flex;flex-wrap:wrap;gap:4px 12px;align-items:baseline;margin-bottom:6px}" +
      "#fhempyTimeline .ftlDayName{font-weight:600;font-size:15px}" +
      "#fhempyTimeline .ftlDayInfo{font-size:12px;opacity:0.7}" +
      "#fhempyTimeline .ftlAway{font-size:11px;font-weight:600;color:#d0662a;border:1px solid #d0662a;border-radius:8px;padding:0 6px}" +
      "#fhempyTimeline .ftlEntry{display:grid;grid-template-columns:44px 10px minmax(0,1fr) auto;gap:8px;padding:4px 0;align-items:start}" +
      "#fhempyTimeline .ftlTime{font-size:13px;opacity:0.7;font-variant-numeric:tabular-nums;padding-top:1px}" +
      "#fhempyTimeline .ftlDot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-top:5px}" +
      "#fhempyTimeline .ftlText{min-width:0}" +
      "#fhempyTimeline .ftlMeta{font-size:12px;opacity:0.65}" +
      "#fhempyTimeline .ftlBarLine{height:4px;border-radius:2px;margin-top:4px;opacity:0.55;max-width:100%}" +
      "#fhempyTimeline .ftlAlert{background:rgba(208,102,42,0.13);border-radius:6px;padding:5px 6px;margin:0 -6px}" +
      "#fhempyTimeline .ftlAlert .ftlText{color:#d0662a;font-weight:600}" +
      "#fhempyTimeline .ftlAction{font-size:11px;opacity:0;cursor:pointer;white-space:nowrap;border:1px solid rgba(128,128,128,0.4);border-radius:4px;padding:0 5px}" +
      "#fhempyTimeline .ftlEntry:hover .ftlAction{opacity:0.8}" +
      "#fhempyTimeline .ftlActions{display:flex;flex-wrap:wrap;justify-content:flex-end;gap:4px;align-items:flex-start}" +
      "@media (hover:none){#fhempyTimeline .ftlAction{opacity:0.6}}" +
      "#fhempyTimeline .ftlChildren{margin:4px 0 0 0;padding-left:10px;border-left:2px solid rgba(128,128,128,0.3)}" +
      "#fhempyTimeline .ftlLink{cursor:pointer;font-size:12px;opacity:0.75;text-decoration:underline}" +
      "#fhempyTimeline .ftlToggle{display:inline-block;margin-top:2px}" +
      "#fhempyTimeline .ftlHiddenRow{padding:2px 0 4px 68px}" +
      "#fhempyTimeline .ftlTrends{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(250px,100%),1fr));gap:8px 16px;margin:4px 0 4px 68px}" +
      "#fhempyTimeline .ftlTrend{font-size:12px}" +
      "#fhempyTimeline .ftlTrendDev{border-left:2px solid rgba(128,128,128,0.3);padding:2px 0 4px 8px;min-width:0}" +
      "#fhempyTimeline .ftlTrendName{font-size:13px;font-weight:600;margin-bottom:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}" +
      "#fhempyTimeline .ftlReading{opacity:0.85}" +
      "#fhempyTimelineTip{position:fixed;z-index:10000;pointer-events:none;background:rgba(40,40,40,0.92);color:#fff;font-size:12px;" +
      "padding:2px 7px;border-radius:4px;white-space:nowrap;display:none;font-family:'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif}" +
      "#fhempyTimeline a.ftlDevice,#fhempyTimelineDetails a.ftlDevice{color:inherit;text-decoration:none}" +
      "#fhempyTimeline a.ftlDevice:hover,#fhempyTimelineDetails a.ftlDevice:hover{text-decoration:underline}" +
      "#fhempyTimeline .ftlTrend .ftlAction{opacity:0;font-size:10px}" +
      "#fhempyTimeline .ftlTrend:hover .ftlAction{opacity:0.8}" +
      "#fhempyTimeline .ftlTrend svg{display:block;width:100%;height:26px}" +
      "svg[data-curve]{cursor:zoom-in}" +
      "#fhempyTimelineCurve{font-family:'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif;line-height:1.4}" +
      "#fhempyTimelineCurve .ftcNav{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:0 0 12px}" +
      "#fhempyTimelineCurve .ftcStep{width:30px;height:30px;border-radius:50%;border:1px solid rgba(128,128,128,0.4);background:none;color:inherit;" +
      "font-size:18px;line-height:26px;cursor:pointer;padding:0}" +
      "#fhempyTimelineCurve .ftcStep:disabled{opacity:0.3;cursor:default}" +
      "#fhempyTimelineCurve .ftcRange{font-weight:600;font-size:15px;min-width:120px;text-align:center}" +
      "#fhempyTimelineCurve .ftcChips{display:flex;gap:6px;margin-left:auto}" +
      "#fhempyTimelineCurve .ftlChip{border:1px solid rgba(128,128,128,0.4);border-radius:14px;padding:2px 11px;cursor:pointer;font-size:13px;user-select:none}" +
      "#fhempyTimelineCurve .ftlChip.ftlOn{border-color:transparent;background:rgba(75,139,190,0.18)}" +
      "#fhempyTimelineCurve .ftcStats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin:0 0 10px}" +
      "#fhempyTimelineCurve .ftcStat{border-radius:8px;background:rgba(128,128,128,0.09);padding:6px 10px;min-width:0}" +
      "#fhempyTimelineCurve .ftcStat b{display:block;font-size:20px;font-weight:600;font-variant-numeric:tabular-nums;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}" +
      "#fhempyTimelineCurve .ftcStat span{font-size:11px;opacity:0.65;white-space:nowrap}" +
      "#fhempyTimelineCurve .ftcChart{position:relative;touch-action:pan-y;transition:opacity .15s}" +
      "#fhempyTimelineCurve .ftcChart.ftcLoading{opacity:0.4}" +
      "#fhempyTimelineCurve .ftcChart svg{display:block;width:100%;overflow:visible;cursor:crosshair}" +
      "#fhempyTimelineCurve .ftcChart text{fill:currentColor;opacity:0.6;font-size:11px}" +
      "#fhempyTimelineCurve .ftcTip{position:absolute;top:0;pointer-events:none;background:rgba(40,40,40,0.92);color:#fff;font-size:12px;" +
      "padding:4px 8px;border-radius:6px;white-space:nowrap;display:none}" +
      "#fhempyTimelineCurve .ftcTip b{font-size:15px}" +
      "#fhempyTimelineCurve .ftcEmpty{display:flex;align-items:center;justify-content:center;opacity:0.6}" +
      "#fhempyTimelineCurve .ftcFoot{display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center;margin-top:10px;font-size:13px}" +
      "#fhempyTimelineCurve .ftcFoot a{color:inherit;opacity:0.8}" +
      "#fhempyTimelineCurve .ftlAction{font-size:12px;cursor:pointer;border:1px solid rgba(128,128,128,0.4);border-radius:4px;padding:1px 6px}" +
      "@media (max-width:600px){#fhempyTimelineCurve .ftcStats{grid-template-columns:repeat(2,minmax(0,1fr))}" +
      "#fhempyTimelineCurve .ftcChips{margin-left:0;width:100%;justify-content:center}#fhempyTimelineCurve .ftcNav{justify-content:center}}" +
      "#fhempyTimeline .ftlQuiet{opacity:0.75;font-size:13px;padding-left:68px}" +
      "#fhempyTimeline .ftlMore{margin:14px 0;text-align:center}" +
      "#fhempyTimeline .ftlButton{display:inline-block;padding:4px 16px;border-radius:14px;background:#4B8BBE;color:#fff;cursor:pointer;font-weight:600}" +
      "#fhempyTimeline .ftlEmpty{opacity:0.75;margin:16px 0}" +
      "#fhempyTimelineDevice{font-family:'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif;line-height:1.4}" +
      "#fhempyTimelineDevice .ftlBar{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:0 0 10px}" +
      "#fhempyTimelineDevice .ftlChip{border:1px solid rgba(128,128,128,0.4);border-radius:14px;padding:2px 11px;cursor:pointer;font-size:13px}" +
      "#fhempyTimelineDevice .ftlChip.ftlOn{border-color:transparent;background:rgba(75,139,190,0.18)}" +
      "#fhempyTimelineDevice .ftlButton{display:inline-block;padding:4px 16px;border-radius:14px;background:#4B8BBE;color:#fff;cursor:pointer;font-weight:600;text-decoration:none}" +
      "#fhempyTimelineDevice .ftlSection{font-weight:600;margin:10px 0 4px}" +
      "#fhempyTimelineDevice .ftlTrend{font-size:12px;margin-bottom:8px}" +
      "#fhempyTimelineDevice .ftlTrend svg{display:block;width:100%;height:44px}" +
      "#fhempyTimelineDevice .ftlEntry{display:grid;grid-template-columns:44px 10px minmax(0,1fr) auto;gap:8px;padding:3px 0;align-items:start}" +
      "#fhempyTimelineDevice .ftlTime{font-size:13px;opacity:0.7;font-variant-numeric:tabular-nums;padding-top:1px}" +
      "#fhempyTimelineDevice .ftlDot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-top:5px}" +
      "#fhempyTimelineDevice .ftlMeta{font-size:12px;opacity:0.65}" +
      "#fhempyTimelineDevice .ftlBarLine{height:4px;border-radius:2px;margin-top:4px;opacity:0.55;max-width:100%}" +
      "#fhempyTimelineDevice .ftlAlert{background:rgba(208,102,42,0.13);border-radius:6px;padding:5px 6px;margin:0 -6px}" +
      "#fhempyTimelineDevice .ftlAction{font-size:11px;cursor:pointer;border:1px solid rgba(128,128,128,0.4);border-radius:4px;padding:0 5px;white-space:nowrap}" +
      "#fhempyTimelineDevice .ftlAxis{display:flex;font-size:11px;opacity:0.6;margin:-4px 0 6px}" +
      "#fhempyTimelineDevice .ftlAxis span{flex:1;text-align:center}" +
      "#fhempyTimelineDevice .ftlEmpty{opacity:0.75;margin:8px 0}" +
      "#fhempyTimelineDetails .ftlDetail{display:grid;grid-template-columns:70px 1fr auto;gap:8px;padding:3px 0;border-bottom:1px solid rgba(128,128,128,0.2);font-size:13px}" +
      "#fhempyTimelineDetails .ftlAction{font-size:11px;cursor:pointer;margin-left:4px;border:1px solid rgba(128,128,128,0.4);border-radius:4px;padding:0 5px;white-space:nowrap}" +
      "@media (max-width:600px){#fhempyTimeline .ftlTrends,#fhempyTimeline .ftlHiddenRow,#fhempyTimeline .ftlQuiet{margin-left:0;padding-left:0}}" +
      "</style>");
  }

  function pad(n) { return n < 10 ? "0" + n : String(n); }

  function clock(ts) {
    var d = new Date(ts * 1000);
    return pad(d.getHours()) + ":" + pad(d.getMinutes());
  }

  function dayDate(day) {
    var p = day.split("-");
    return new Date(+p[0], +p[1] - 1, +p[2]);
  }

  function dayIso(date) {
    return date.getFullYear() + "-" + pad(date.getMonth() + 1) + "-" + pad(date.getDate());
  }

  function addDays(day, n) {
    var d = dayDate(day);
    d.setDate(d.getDate() + n);
    return dayIso(d);
  }

  function dayTitle(day) {
    var d = dayDate(day);
    var today = dayIso(new Date());
    if (day === today) return "Today";
    if (day === addDays(today, -1)) return "Yesterday";
    return d.toLocaleDateString(undefined, { weekday: "short", day: "numeric", month: "long" });
  }

  function shortDate(day) {
    return dayDate(day).toLocaleDateString(undefined, { day: "numeric", month: "short" });
  }

  function duration(seconds) {
    seconds = Math.max(0, Math.round(seconds));
    if (seconds < 60) return seconds + " s";
    var m = Math.round(seconds / 60);
    if (m < 60) return m + " min";
    var h = Math.floor(m / 60);
    if (h < 48) return h + " h " + (m % 60 ? (m % 60) + " min" : "");
    return Math.round(h / 24) + " days";
  }

  function cmd(command, callback) {
    FW_cmd(FW_root + "?cmd=" + encodeURIComponent(command) + "&XHR=1", callback);
  }

  function load(from, to, append) {
    if (loading) return;
    loading = true;
    renderLoading();
    cmd("get " + device + " entries " + from + " " + to, function (r) {
      loading = false;
      var data;
      try {
        data = JSON.parse(r);
      } catch (e) {
        renderError(r);
        return;
      }
      if (data.error) {
        renderError(data.error);
        return;
      }
      days = append ? days.concat(data.days) : data.days;
      keepScroll = append;
      periods = data.periods || [];
      firstDay = data.first;
      render();
    });
  }

  function loadOlder() {
    if (!days.length) return;
    var oldest = days[days.length - 1].day;
    load(addDays(oldest, -7), addDays(oldest, -1), true);
  }

  function visible(entry) {
    if (filter.categories[entry.category] === false) return false;
    if (!filter.search) return true;
    var text = (entry.text + " " + (entry.room || "") + " " + entry.device).toLowerCase();
    if (text.indexOf(filter.search) >= 0) return true;
    return (entry.children || []).some(visible);
  }

  function deviceLink(name, text) {
    if (!name) return esc(text);
    return '<a class="ftlDevice" data-device="' + esc(name) + '" href="' + esc(FW_root + "?detail=" + encodeURIComponent(name)) +
      '" title="History of ' + esc(name) + ' (Ctrl+click opens the device)">' + esc(text) + "</a>";
  }

  function onChangeAction(item) {
    if (!item.device || item.on_change) return "";
    return '<span class="ftlAction" data-onchange="' + esc(item.device + ":" + item.reading) +
      '" title="Add ' + esc(item.reading) + " to event-on-change-reading of " + esc(item.device) +
      ': events only when the value changes">Only on change</span>';
  }

  function dot(category) {
    var info = categoryInfo[category] || categoryInfo.devices;
    return '<span class="ftlDot" style="background:' + info.color + '" title="' + esc(info.title) + '"></span>';
  }

  function entryMeta(entry, dayEnd) {
    var parts = [];
    if (entry.room) parts.push(esc(entry.room.split(",")[0]));
    if (entry.count > 1 && entry.end) {
      parts.push(entry.count + "× until " + clock(entry.end));
    } else if (entry.count > 1) {
      parts.push(entry.count + "×");
    } else if (entry.end) {
      parts.push(duration(entry.end - entry.ts));
    } else if (entry.running) {
      // still on: how long so far
      parts.push((entry.value ? "still " + esc(entry.value) + " for " : "running for ") + duration(Date.now() / 1000 - entry.ts));
    }
    return parts.join(" · ");
  }

  function durationBar(entry) {
    var end = entry.end || (entry.running ? Date.now() / 1000 : null);
    if (!end || entry.count > 1) return "";
    var pct = Math.min(100, Math.max(2, (end - entry.ts) / 864));
    var info = categoryInfo[entry.category] || categoryInfo.devices;
    return '<div class="ftlBarLine" style="width:' + pct.toFixed(1) + "%;background:" + info.color + '"></div>';
  }

  function entryHtml(entry) {
    var html = '<div class="ftlEntry' + (entry.alert ? " ftlAlert" : "") + '">' +
      '<span class="ftlTime">' + clock(entry.ts) + "</span>" + dot(entry.category) +
      '<div class="ftlText">' + deviceLink(entry.device, entry.text);
    var meta = entryMeta(entry);
    if (meta) html += '<div class="ftlMeta">' + meta + "</div>";
    html += durationBar(entry);
    if (entry.children) {
      html += '<div class="ftlChildren" style="display:none">';
      entry.children.forEach(function (child) { html += entryHtml(child); });
      html += "</div>";
      html += '<div><span class="ftlLink ftlToggle" data-key="g' + entry.ts + '">Show ' + entry.children.length + " devices</span></div>";
    }
    html += "</div>";
    if (entry.device) {
      html += '<span class="ftlActions">' + onChangeAction(entry) + '<span class="ftlAction" data-hide="' + esc(entry.device + ":" + entry.reading) +
        '" title="Don\'t show ' + esc(entry.device + ":" + entry.reading) + ' anymore">Show less</span></span>';
    } else {
      html += "<span></span>";
    }
    return html + "</div>";
  }

  // hover values: data-tip holds [x in %, start of the hour, value] per point
  function tipAttr(tips, withDay) {
    return " data-tip='" + JSON.stringify(tips) + "'" + (withDay ? ' data-tipday="1"' : "");
  }

  // a click on a curve opens it big (showCurve)
  function curveAttr(trend, day, days) {
    return ' data-curve="' + esc(trend.device + ":" + trend.reading) + '" data-day="' + day + '" data-days="' + days + '"';
  }

  function sparkline(trend, dayStart) {
    var pts = [], tips = [];
    var low = trend.min, high = trend.max;
    var span = high - low || 1;
    trend.points.forEach(function (v, i) {
      if (v === null) return;
      var x = i * 100 / 23;
      pts.push(x.toFixed(1) + "," + (24 - (v - low) / span * 20).toFixed(1));
      tips.push([+x.toFixed(2), dayStart + i * 3600, v]);
    });
    var info = categoryInfo[trend.category] || categoryInfo.devices;
    if (!pts.length) return "";
    var line = pts.length > 1 ? '<polyline fill="none" stroke="' + info.color + '" stroke-width="1.5" vector-effect="non-scaling-stroke" points="' + pts.join(" ") + '"/>' : "";
    return '<svg viewBox="0 0 100 26" preserveAspectRatio="none"' + tipAttr(tips) +
      curveAttr(trend, dayIso(new Date(dayStart * 1000)), 1) + ">" + line + "</svg>";
  }

  function trendHtml(t, dayStart) {
    return '<div class="ftlTrend"><span class="ftlReading">' + esc(t.reading) + '</span> <span style="opacity:0.7">' +
      fmt(t.min) + (t.changed ? " – " + fmt(t.max) : "") + "</span> " + onChangeAction(t) + sparkline(t, dayStart) + "</div>";
  }

  // curves of one device together under its name
  function trendGroupsHtml(trends, dayStart) {
    var groups = [], byDevice = {};
    trends.forEach(function (t) {
      if (!byDevice[t.device]) {
        byDevice[t.device] = { device: t.device, label: t.label || t.text, trends: [] };
        groups.push(byDevice[t.device]);
      }
      byDevice[t.device].trends.push(t);
    });
    var html = "";
    groups.forEach(function (g) {
      html += '<div class="ftlTrendDev"><div class="ftlTrendName">' + deviceLink(g.device, g.label) +
        (g.trends.length > 1 ? ' <span style="opacity:0.6;font-weight:normal">' + g.trends.length + " curves</span>" : "") + "</div>";
      g.trends.forEach(function (t) { html += trendHtml(t, dayStart); });
      html += "</div>";
    });
    return html;
  }

  function trendsHtml(day) {
    var trends = day.trends.filter(function (t) { return visible(t); });
    if (!trends.length) return "";
    // curves which stayed the same all day only on demand
    var changed = trends.filter(function (t) { return t.changed; });
    var same = trends.filter(function (t) { return !t.changed; });
    var dayStart = dayDate(day.day).getTime() / 1000;
    var html = '<div class="ftlHiddenRow"><span class="ftlLink ftlTrendToggle" data-key="t' + day.day + '">Curves (' + changed.length + " changed" +
      (same.length ? ", " + same.length + " unchanged" : "") + ")</span></div>" +
      '<div class="ftlTrendBox" style="display:none"><div class="ftlTrends">';
    html += trendGroupsHtml(changed, dayStart);
    html += "</div>";
    if (same.length) {
      html += '<div class="ftlHiddenRow"><span class="ftlLink ftlSameToggle" data-key="s' + day.day + '">Show ' + same.length +
        " unchanged curves</span></div>" + '<div class="ftlTrends ftlSame" style="display:none">';
      html += trendGroupsHtml(same, dayStart);
      html += "</div>";
    }
    return html + "</div>";
  }

  function fmt(v) {
    return Math.abs(v) >= 100 ? Math.round(v).toString() : (Math.round(v * 10) / 10).toString();
  }

  function dayHtml(day) {
    var entries = day.entries.filter(visible);
    var info = [];
    info.push(entries.length + (entries.length === 1 ? " entry" : " entries"));
    if (day.hidden) info.push(day.hidden.toLocaleString() + " hidden events");
    var html = '<div class="ftlDay"><div class="ftlDayHead"><span class="ftlDayName">' + esc(dayTitle(day.day)) + "</span>" +
      (day.absent ? '<span class="ftlAway">away</span>' : "") +
      '<span class="ftlDayInfo">' + info.join(" · ") + "</span></div>";
    // newest first, like the days; on wide screens the curves are shown next to the story
    html += '<div class="ftlDayMain">';
    entries.slice().reverse().forEach(function (entry) { html += entryHtml(entry); });
    if (day.hidden) {
      html += '<div class="ftlHiddenRow"><span class="ftlLink ftlDetails" data-day="' + day.day + '">+ ' +
        day.hidden.toLocaleString() + " technical events and measurements</span></div>";
    }
    return html + '</div><div class="ftlDaySide">' + trendsHtml(day) + "</div></div>";
  }

  function quietHtml(group) {
    var first = group[group.length - 1].day, last = group[0].day;
    var hidden = group.reduce(function (s, d) { return s + d.hidden; }, 0);
    var away = group.some(function (d) { return d.absent; });
    var title = group.length === 1 ? dayTitle(first) : shortDate(first) + " – " + shortDate(last);
    var html = '<div class="ftlDay"><div class="ftlDayHead"><span class="ftlDayName">' + esc(title) + "</span>" +
      (away ? '<span class="ftlAway">away</span>' : "") +
      '<span class="ftlDayInfo">' + (group.length === 1 ? "quiet day" : group.length + " quiet days") +
      (hidden ? " · " + hidden.toLocaleString() + " hidden events" : "") + "</span></div>";
    html += '<div class="ftlDayMain"></div><div class="ftlDaySide">';
    group.forEach(function (day) { html += trendsHtml(day); });
    return html + "</div></div>";
  }

  function barHtml() {
    var html = '<div class="ftlBar"><span class="ftlTitle">Timeline</span>' +
      '<span class="ftlChip ftlRange" data-days="1">Today</span>' +
      '<span class="ftlChip ftlRange" data-days="7">7 days</span>';
    periods.slice(0, 4).forEach(function (p) {
      html += '<span class="ftlChip ftlPeriod" data-from="' + p.start + '" data-to="' + p.end + '" title="Nobody was at home">Away ' +
        esc(shortDate(p.start)) + " – " + esc(shortDate(p.end)) + "</span>";
    });
    html += '<input type="date" class="ftlDate" title="Go to day" min="' + esc(firstDay) + '" max="' + dayIso(new Date()) + '">' +
      "</div><div class=\"ftlBar\">";
    Object.keys(categoryInfo).forEach(function (c) {
      html += '<span class="ftlChip' + (filter.categories[c] === false ? "" : " ftlOn") + '" data-category="' + c + '">' +
        dot(c) + esc(categoryInfo[c].title) + "</span>";
    });
    html += '<input type="search" class="ftlSearch" placeholder="Search devices, rooms" value="' + esc(filter.search) + '">';
    return html + "</div>";
  }

  // only the list of days scrolls, filters and the page stay where they are
  function fitScroll() {
    var list = $("#fhempyTimeline .ftlScroll");
    if (!list.length) return;
    var top = list[0].getBoundingClientRect().top + (window.scrollY || 0) + ($("#content").scrollTop() || 0);
    var height = window.innerHeight - top - 12;
    list.css("max-height", Math.max(height, Math.round(window.innerHeight * 0.7)) + "px");
  }

  function render() {
    var root = $("#fhempyTimeline");
    wide = root.width() >= WIDE_MIN;
    root.toggleClass("ftlWideMode", wide);
    // phones: buttons below the text instead of next to it
    root.toggleClass("ftlNarrow", root.width() < NARROW_MAX);
    var scrollTop = root.find(".ftlScroll").scrollTop() || 0;
    var html = barHtml() + '<div class="ftlScroll">';
    if (!days.length) {
      html += '<div class="ftlEmpty">Nothing recorded yet. The timeline fills up as soon as something happens at home.</div>';
    }
    var quiet = [];
    days.forEach(function (day) {
      if (day.entries.filter(visible).length === 0) {
        quiet.push(day);
        return;
      }
      if (quiet.length) { html += quietHtml(quiet); quiet = []; }
      html += dayHtml(day);
    });
    if (quiet.length) html += quietHtml(quiet);
    if (days.length && days[days.length - 1].day > firstDay) {
      html += '<div class="ftlMore"><span class="ftlButton ftlOlder">Show older days</span></div>';
    }
    html += "</div>";
    var search = root.find(".ftlSearch");
    var focused = search.is(":focus");
    root.html(html);
    restoreExpanded(root);
    fitScroll();
    var list = root.find(".ftlScroll");
    list.scrollTop(keepScroll ? scrollTop : 0);
    keepScroll = true;
    // the next older days are loaded when the end of the list is reached
    list.on("scroll", function () {
      if (this.scrollTop + this.clientHeight >= this.scrollHeight - 40 && root.find(".ftlOlder").length) loadOlder();
    });
    if (focused) {
      search = root.find(".ftlSearch");
      search.focus();
      var len = search.val().length;
      search[0].setSelectionRange(len, len);
    }
  }

  function renderLoading() {
    var root = $("#fhempyTimeline");
    if (!root.children().length) root.html('<div class="ftlEmpty">Loading the timeline…</div>');
    root.find(".ftlOlder").text("Loading…");
  }

  function renderError(text) {
    $("#fhempyTimeline").html('<div class="ftlEmpty">The timeline could not be loaded: ' + esc(text) + "</div>");
  }

  function periodSparkline(trend, from, to) {
    var low = trend.min, span = trend.max - trend.min || 1;
    var info = categoryInfo[trend.category] || categoryInfo.devices;
    var lines = [], line = [], last = null, tips = [];
    trend.points.forEach(function (p) {
      // no value for more than 2 hours: gap in the curve
      if (last !== null && p[0] - last > 7200) { lines.push(line); line = []; }
      last = p[0];
      var x = (p[0] + 1800 - from) * 100 / (to - from);
      line.push(x.toFixed(2) + "," + (36 - (p[1] - low) / span * 30).toFixed(1));
      tips.push([+x.toFixed(2), p[0], p[1]]);
    });
    lines.push(line);
    var html = '<svg viewBox="0 0 100 40" preserveAspectRatio="none"' + tipAttr(tips, true) +
      curveAttr(trend, dayIso(new Date((to - 1) * 1000)), Math.round((to - from) / 86400)) + ">";
    for (var t = from + 86400; t < to; t += 86400) {
      var x = ((t - from) * 100 / (to - from)).toFixed(2);
      html += '<line x1="' + x + '" x2="' + x + '" y1="0" y2="40" stroke="rgba(128,128,128,0.25)" stroke-width="1" vector-effect="non-scaling-stroke"/>';
    }
    lines.forEach(function (pts) {
      if (pts.length > 1) {
        html += '<polyline fill="none" stroke="' + info.color + '" stroke-width="1.5" vector-effect="non-scaling-stroke" points="' + pts.join(" ") + '"/>';
      } else if (pts.length) {
        var xy = pts[0].split(",");
        html += '<line x1="' + xy[0] + '" x2="' + (+xy[0] + 0.4) + '" y1="' + xy[1] + '" y2="' + xy[1] + '" stroke="' + info.color + '" stroke-width="3" vector-effect="non-scaling-stroke"/>';
      }
    });
    return html + "</svg>";
  }

  function deviceEntryHtml(entry) {
    var meta = entryMeta(entry);
    return '<div class="ftlEntry' + (entry.alert ? " ftlAlert" : "") + '"><span class="ftlTime">' + clock(entry.ts) + "</span>" +
      dot(entry.category) + '<div class="ftlText">' + esc(entry.text) + (meta ? '<div class="ftlMeta">' + meta + "</div>" : "") +
      durationBar(entry) + "</div><span>" + onChangeAction(entry) + "</span></div>";
  }

  function deviceHtml(data, days) {
    var html = '<div class="ftlBar"><span class="ftlMeta" style="margin-right:auto">' +
      esc([data.type, (data.room || "").split(",")[0]].filter(function (x) { return x; }).join(" · ")) + "</span>" +
      '<span class="ftlChip ftlDeviceDays' + (days === 7 ? " ftlOn" : "") + '" data-days="7">7 days</span>' +
      '<span class="ftlChip ftlDeviceDays' + (days === 31 ? " ftlOn" : "") + '" data-days="31">31 days</span>' +
      '<a class="ftlButton ftlOpen" href="' + esc(FW_root + "?detail=" + encodeURIComponent(data.device)) + '">Open device</a></div>';
    var changed = data.trends.filter(function (t) { return t.changed; });
    var same = data.trends.filter(function (t) { return !t.changed; });
    if (changed.length) {
      html += '<div class="ftlSection">Curves</div>';
      changed.forEach(function (t) {
        html += '<div class="ftlTrend ftlWide">' + esc(t.reading) + ' <span style="opacity:0.7">' + fmt(t.min) + " – " + fmt(t.max) +
          "</span> " + onChangeAction(t) + periodSparkline(t, data.from, data.to) + "</div>";
      });
      if (days <= 7) {
        html += '<div class="ftlAxis">';
        for (var day = data.from; day < data.to; day += 86400) {
          html += "<span>" + esc(new Date((day + 43200) * 1000).toLocaleDateString(undefined, { weekday: "short" })) + "</span>";
        }
        html += "</div>";
      }
    }
    if (same.length) {
      html += '<div class="ftlMeta" style="margin:4px 0 8px">Unchanged: ' + same.map(function (t) {
        return esc(t.reading) + " " + fmt(t.min);
      }).join(" · ") + "</div>";
    }
    html += '<div class="ftlSection">Story</div>';
    if (!data.entries.length) {
      html += '<div class="ftlEmpty">Nothing in the story of this device in the last ' + days + " days.</div>";
    }
    var lastDay = "";
    data.entries.forEach(function (entry) {
      var day = dayIso(new Date(entry.ts * 1000));
      if (day !== lastDay) {
        html += '<div class="ftlDayName" style="margin:8px 0 2px">' + esc(dayTitle(day)) + "</div>";
        lastDay = day;
      }
      html += deviceEntryHtml(entry);
    });
    return html;
  }

  // curve popup: one reading big, day / 7 days / 31 days, step back and forth
  var curve = null;

  function niceTicks(low, high) {
    if (high - low < 1e-9) { low -= Math.max(Math.abs(low) * 0.05, 0.5); high += Math.max(Math.abs(high) * 0.05, 0.5); }
    var raw = (high - low) / 4;
    var mag = Math.pow(10, Math.floor(Math.log(raw) / Math.LN10));
    var step = [1, 2, 2.5, 5, 10].map(function (f) { return f * mag; }).filter(function (f) { return f >= raw; })[0];
    var ticks = [];
    for (var v = Math.floor(low / step) * step; v <= high + step * 0.001; v += step) ticks.push(+v.toFixed(10));
    if (ticks[ticks.length - 1] < high) ticks.push(+(ticks[ticks.length - 1] + step).toFixed(10));
    return ticks;
  }

  function curveRangeText(data, days) {
    if (days === 1) return dayTitle(data.day);
    return shortDate(addDays(data.day, 1 - days)) + " – " + shortDate(data.day);
  }

  // 31 days: 6 hour steps instead of hours, otherwise the curve is too busy
  function bucketPoints(points, span, from) {
    var result = [], bucket = null;
    points.forEach(function (p) {
      var start = p[0] - ((p[0] - from) % span);
      if (!bucket || bucket[0] !== start) {
        bucket = [start, 0, p[2], p[3], 0];
        result.push(bucket);
      }
      bucket[1] += p[1];
      bucket[4] += 1;
      bucket[2] = Math.min(bucket[2], p[2]);
      bucket[3] = Math.max(bucket[3], p[3]);
    });
    return result.map(function (b) { return [b[0], Math.round(b[1] / b[4] * 100) / 100, b[2], b[3]]; });
  }

  function pointTime(ts, days) {
    var text = clock(ts) + "–" + clock(ts + curve.span);
    if (days === 1) return text;
    return new Date(ts * 1000).toLocaleDateString(undefined, { weekday: "short", day: "numeric", month: "short" }) + ", " + text;
  }

  function curveStats(data, days) {
    var pts = data.raw || data.points;
    if (!pts.length) return "";
    var low = pts[0], high = pts[0];
    pts.forEach(function (p) { if (p[2] < low[2]) low = p; if (p[3] > high[3]) high = p; });
    var last = pts[pts.length - 1];
    var when = function (p) {
      if (days === 1) return clock(p[0]);
      var date = new Date(p[0] * 1000);
      return (days <= 7 ? date.toLocaleDateString(undefined, { weekday: "short" }) : shortDate(dayIso(date))) + " " + clock(p[0]);
    };
    var stat = function (value, text) { return '<div class="ftcStat"><b>' + fmt(value) + "</b><span>" + text + "</span></div>"; };
    return '<div class="ftcStats">' +
      stat(last[1], data.day === data.today ? "Latest · " + clock(last[0]) : "Last · " + when(last)) +
      stat(data.min, "Min · " + when(low)) + stat(data.max, "Max · " + when(high)) +
      stat(data.avg, "Average") + "</div>";
  }

  // time axis: hours of a day, weekdays or dates
  function timeAxis(data, days, x, top, h, height) {
    var svg = "", t;
    if (days === 1) {
      for (t = data.from; t <= data.to; t += 3 * 3600) {
        svg += '<text x="' + x(t).toFixed(1) + '" y="' + (height - 6) + '" text-anchor="middle">' + clock(t).slice(0, 2) + "</text>";
      }
    } else {
      var every = days <= 7 ? 1 : 7;
      for (var i = 0; i < days; i++) {
        t = dayDate(addDays(data.day, i - days + 1)).getTime() / 1000;
        if (i % every) continue;
        if (i) svg += '<line x1="' + x(t).toFixed(1) + '" x2="' + x(t).toFixed(1) + '" y1="' + top + '" y2="' + (top + h) + '" stroke="currentColor" stroke-opacity="0.12"/>';
        var label = days <= 7 ? new Date((t + 43200) * 1000).toLocaleDateString(undefined, { weekday: "short" }) : shortDate(addDays(data.day, i - days + 1));
        svg += '<text x="' + x(days <= 7 ? t + 43200 : t).toFixed(1) + '" y="' + (height - 6) + '" text-anchor="' + (days <= 7 ? "middle" : "start") + '">' + esc(label) + "</text>";
      }
    }
    return svg;
  }

  // min-max band and average line, gaps where values are missing for more than 2 hours
  function curveLines(data, x, y, color) {
    var svg = "";
    var parts = [], part = [], last = null;
    data.points.forEach(function (p) {
      if (last !== null && p[0] - last > curve.span + 7200) { parts.push(part); part = []; }
      last = p[0];
      part.push(p);
    });
    parts.push(part);
    parts.forEach(function (pts) {
      var mid = function (p) { return x(p[0] + curve.span / 2).toFixed(1); };
      if (pts.length === 1) {
        svg += '<circle cx="' + mid(pts[0]) + '" cy="' + y(pts[0][1]).toFixed(1) + '" r="2.5" fill="' + color + '"/>';
        return;
      }
      var band = pts.map(function (p) { return mid(p) + "," + y(p[3]).toFixed(1); }).concat(
        pts.slice().reverse().map(function (p) { return mid(p) + "," + y(p[2]).toFixed(1); }));
      svg += '<polygon points="' + band.join(" ") + '" fill="' + color + '" fill-opacity="0.15"/>';
      svg += '<polyline fill="none" stroke="' + color + '" stroke-width="2" stroke-linejoin="round" points="' +
        pts.map(function (p) { return mid(p) + "," + y(p[1]).toFixed(1); }).join(" ") + '"/>';
    });
    return svg;
  }

  function curveChart(data, days, width) {
    var height = width < 500 ? 200 : 260;
    var left = 46, right = 10, top = 10, bottom = 24;
    var w = width - left - right, h = height - top - bottom;
    if (!data.points.length) {
      return '<div class="ftcEmpty" style="height:' + height + 'px">No values in this period</div>';
    }
    var ticks = niceTicks(data.min, data.max);
    var low = ticks[0], span = ticks[ticks.length - 1] - low || 1;
    var x = function (ts) { return left + (ts - data.from) * w / (data.to - data.from); };
    var y = function (v) { return top + h - (v - low) * h / span; };
    var info = categoryInfo[data.category] || categoryInfo.devices;
    var svg = '<svg width="' + width + '" height="' + height + '" viewBox="0 0 ' + width + " " + height + '">';
    ticks.forEach(function (t) {
      svg += '<line x1="' + left + '" x2="' + (left + w) + '" y1="' + y(t).toFixed(1) + '" y2="' + y(t).toFixed(1) +
        '" stroke="currentColor" stroke-opacity="0.12"/>' +
        '<text x="' + (left - 6) + '" y="' + (y(t) + 4).toFixed(1) + '" text-anchor="end">' + fmt(t) + "</text>";
    });
    svg += timeAxis(data, days, x, top, h, height);
    svg += curveLines(data, x, y, info.color);
    svg += '<line class="ftcCross" y1="' + top + '" y2="' + (top + h) + '" stroke="currentColor" stroke-opacity="0.35" style="display:none"/>' +
      '<circle class="ftcDot" r="4" fill="' + info.color + '" stroke="#fff" stroke-width="1.5" style="display:none"/>';
    curve.geometry = { x: x, y: y, left: left, w: w };
    return svg + '</svg><div class="ftcTip"></div>';
  }

  function curveHover(e) {
    if (!curve || !curve.data || !curve.data.points.length || !curve.geometry) return;
    var chart = $(this), svg = chart.find("svg")[0];
    if (!svg) return;
    var ev = e.originalEvent && e.originalEvent.touches && e.originalEvent.touches.length ? e.originalEvent.touches[0] : e;
    var rect = svg.getBoundingClientRect();
    var px = ev.clientX - rect.left, g = curve.geometry;
    var best = null;
    var half = curve.span / 2;
    curve.data.points.forEach(function (p) {
      if (!best || Math.abs(g.x(p[0] + half) - px) < Math.abs(g.x(best[0] + half) - px)) best = p;
    });
    var cx = g.x(best[0] + half), cy = g.y(best[1]);
    chart.find(".ftcCross").attr({ x1: cx, x2: cx }).show();
    chart.find(".ftcDot").attr({ cx: cx, cy: cy }).show();
    var tip = chart.find(".ftcTip");
    tip.html("<b>" + fmt(best[1]) + "</b>" + (best[2] !== best[3] ? ' <span style="opacity:0.75">' + fmt(best[2]) + " – " + fmt(best[3]) + "</span>" : "") +
      "<br>" + esc(pointTime(best[0], curve.days))).show();
    var left = Math.max(0, Math.min(cx - tip.outerWidth() / 2, rect.width - tip.outerWidth()));
    var top = cy - tip.outerHeight() - 12;
    tip.css({ left: left, top: top < 0 ? cy + 12 : top });
  }

  function curveLeave() {
    $(this).find(".ftcCross, .ftcDot, .ftcTip").hide();
  }

  function renderCurve() {
    var d = $("#fhempyTimelineCurve"), data = curve.data, days = curve.days;
    if (data.error) {
      d.html('<div class="ftlEmpty">' + esc(data.error) + "</div>");
      return;
    }
    var chips = [[1, "Day"], [7, "7 days"], [31, "31 days"]].map(function (c) {
      return '<span class="ftlChip ftcDays' + (days === c[0] ? " ftlOn" : "") + '" data-days="' + c[0] + '">' + c[1] + "</span>";
    }).join("");
    var html = '<div class="ftcNav"><button class="ftcStep" data-step="-1" title="Earlier (←)">‹</button>' +
      '<span class="ftcRange">' + esc(curveRangeText(data, days)) + "</span>" +
      '<button class="ftcStep" data-step="1" title="Later (→)"' + (data.day >= data.today ? " disabled" : "") + ">›</button>" +
      '<span class="ftcChips">' + chips + "</span></div>" + curveStats(data, days) +
      '<div class="ftcChart"></div><div class="ftcFoot">' +
      '<a href="#" class="ftcHistory">History of ' + esc(data.label) + "</a>" +
      '<a href="' + esc(FW_root + "?detail=" + encodeURIComponent(data.device)) + '">Open device</a>' +
      onChangeAction(data) + "</div>";
    d.html(html);
    var chart = d.find(".ftcChart");
    chart.html(curveChart(data, days, Math.max(260, Math.floor(chart.width()))));
  }

  function loadCurve() {
    var d = $("#fhempyTimelineCurve");
    d.find(".ftcChart").addClass("ftcLoading");
    var request = curve.target + " " + curve.day + " " + curve.days;
    curve.request = request;
    cmd("get " + device + " curve " + request, function (r) {
      if (!curve || curve.request !== request) return;
      try { curve.data = JSON.parse(r); } catch (e) { curve.data = { error: r }; }
      curve.span = curve.days > 7 ? 6 * 3600 : 3600;
      curve.data.raw = curve.data.points;
      if (curve.data.points && curve.span > 3600) curve.data.points = bucketPoints(curve.data.points, curve.span, curve.data.from);
      if (!d.hasClass("ui-dialog-content")) {
        openDialog(d, 880, function () {
          $(this).dialog("destroy").remove();
          $(document).off(".ftlCurve");
          $(window).off(".ftlCurve");
          curve = null;
        });
        $(document).on("keydown.ftlCurve", function (e) {
          if (e.key === "Escape" && d.hasClass("ui-dialog-content")) d.dialog("close");
          else if (e.key === "ArrowLeft") stepCurve(-1);
          else if (e.key === "ArrowRight") stepCurve(1);
        });
        $(window).on("resize.ftlCurve", function () { if (curve && curve.data) renderCurve(); });
      }
      d.dialog("option", "title", (curve.data.label || curve.target.split(":")[0]) + " · " + curve.target.split(":")[1]);
      renderCurve();
    });
  }

  function stepCurve(direction) {
    if (!curve || !curve.data || curve.data.error) return;
    var day = addDays(curve.day, direction * curve.days);
    if (day > curve.data.today) {
      if (curve.day >= curve.data.today) return;
      day = curve.data.today;
    }
    curve.day = day;
    loadCurve();
  }

  function showCurve(target, day, days) {
    hideTip();
    var d = $("#fhempyTimelineCurve");
    if (!d.length) {
      d = $('<div id="fhempyTimelineCurve"></div>');
      $("body").append(d);
      d.on("click", ".ftcStep", function () { stepCurve(+$(this).attr("data-step")); });
      d.on("click", ".ftcDays", function () {
        curve.days = +$(this).attr("data-days");
        loadCurve();
      });
      d.on("click", ".ftcHistory", function (e) {
        e.preventDefault();
        var name = curve.data.device;
        d.dialog("close");
        showDevice(name);
      });
      d.on("click", "[data-onchange]", onChangeClick);
      d.on("mousemove touchstart touchmove", ".ftcChart", curveHover);
      d.on("mouseleave", ".ftcChart", curveLeave);
    }
    curve = { target: target, day: day, days: days || 1 };
    loadCurve();
  }

  function curveClick(e) {
    e.preventDefault();
    var svg = $(this);
    showCurve(svg.attr("data-curve"), svg.attr("data-day"), +svg.attr("data-days"));
  }

  function showDevice(name, days) {
    days = days || 7;
    cmd("get " + device + " device " + name + " " + days, function (r) {
      var data;
      try { data = JSON.parse(r); } catch (e) { data = { error: r }; }
      var d = $("#fhempyTimelineDevice");
      if (!d.length) {
        d = $('<div id="fhempyTimelineDevice"></div>');
        $("body").append(d);
        d.on("click", "[data-onchange]", onChangeClick);
        d.on("click", ".ftlDeviceDays", function () {
          showDevice(d.attr("data-device"), +$(this).attr("data-days"));
        });
      }
      d.attr("data-device", name);
      d.html(data.error ? '<div class="ftlEmpty">' + esc(data.error) + "</div>" : deviceHtml(data, days));
      if (!d.hasClass("ui-dialog-content")) {
        openDialog(d, 760, function () { $(this).dialog("destroy").remove(); });
      }
      d.dialog("option", "title", data.text || name);
    });
  }

  // popups: Close button, Escape and a tap next to the popup close them,
  // also on phones where the title bar button is hard to hit
  function openDialog(d, width, close) {
    d.dialog({
      modal: true,
      closeOnEscape: true,
      width: Math.min(width, $(window).width() - 20),
      maxHeight: $(window).height() - 40,
      position: { my: "center top+10", at: "center top", of: window, collision: "fit" },
      buttons: [{ text: "Close", click: function () { $(this).dialog("close"); } }],
      close: close
    });
    d.dialog("widget").css("position", "fixed");
    $(".ui-widget-overlay").last().on("click", function () {
      if (d.hasClass("ui-dialog-content")) d.dialog("close");
    });
  }

  function deviceClick(e) {
    // ctrl, shift or middle click open the device as usual
    if (e.ctrlKey || e.metaKey || e.shiftKey || e.button !== 0) return;
    e.preventDefault();
    showDevice($(this).attr("data-device"));
  }

  function showDetails(day) {
    cmd("get " + device + " details " + day, function (r) {
      var rows;
      try { rows = JSON.parse(r); } catch (e) { rows = []; }
      if (rows.error) rows = [];
      $("#fhempyTimelineDetails").remove();
      var d = $('<div id="fhempyTimelineDetails"></div>');
      var html = '<div style="margin-bottom:8px;opacity:0.75">Measurements and technical events of ' + esc(dayTitle(day)) +
        " (newest first, at most 500). Signal strength, last seen and similar are only counted.</div>";
      if (!rows.length) html += "<div>Nothing stored for this day.</div>";
      rows.forEach(function (row) {
        html += '<div class="ftlDetail"><span>' + clock(row.ts) + "</span><span>" + deviceLink(row.device, row.text) + "</span>" +
          "<span>" + onChangeAction(row) +
          '<span class="ftlAction" data-show="' + esc(row.device + ":" + row.reading) + '" title="Show ' +
          esc(row.device + ":" + row.reading) + ' in the timeline from now on">Always show</span>' +
          '<span class="ftlAction" data-ignore="' + esc(row.device + ":" + row.reading) + '" title="Don\'t record ' +
          esc(row.device + ":" + row.reading) + ' at all anymore (attribute skip_events)">Ignore completely</span></span></div>';
      });
      d.html(html);
      $("body").append(d);
      openDialog(d, 700, function () { $(this).dialog("destroy").remove(); });
      d.dialog("option", "title", "Hidden events");
      d.on("click", "[data-onchange]", onChangeClick);
      d.on("click", "a.ftlDevice", deviceClick);
      d.on("click", "[data-show]", function () {
        var target = $(this).attr("data-show");
        var el = $(this);
        cmd("set " + device + " show " + target, function () { el.text("Shown from now on").removeClass("ftlAction"); });
      });
      d.on("click", "[data-ignore]", function () {
        var target = $(this).attr("data-ignore");
        cmd("set " + device + " ignore " + target, function () {
          d.find('[data-ignore="' + target.replace(/["\\]/g, "") + '"]').text("Ignored from now on")
            .removeAttr("data-ignore").removeClass("ftlAction");
        });
      });
    });
  }

  function onChangeClick() {
    var target = $(this).attr("data-onchange");
    var el = $(this);
    cmd("set " + device + " on_change " + target, function (r) {
      if (r && r.trim()) {
        el.text(r.trim());
        return;
      }
      days.forEach(function (day) {
        day.trends.concat(day.entries).forEach(function (t) {
          if (t.device + ":" + t.reading === target) t.on_change = true;
        });
      });
      $('[data-onchange="' + target.replace(/["\\]/g, "") + '"]').text("Only on change ✓").removeAttr("data-onchange").removeClass("ftlAction");
    });
  }

  function setExpanded(toggle, open) {
    if (toggle.hasClass("ftlToggle")) {
      var children = toggle.parent().siblings(".ftlChildren");
      children.toggle(open);
      toggle.text(open ? "Hide devices" : "Show " + children.children().length + " devices");
    } else if (toggle.hasClass("ftlTrendToggle")) {
      toggle.parent().next(".ftlTrendBox").toggle(open);
    } else {
      var same = toggle.parent().next(".ftlSame");
      same.css("display", open ? "grid" : "none");
      toggle.text(open ? "Hide unchanged curves" : "Show " + same.children().length + " unchanged curves");
    }
  }

  // what the user opened stays open when the timeline is drawn again,
  // e.g. after "Show less" or a filter
  function restoreExpanded(root) {
    root.find("[data-key]").each(function () {
      if (isOpen($(this).attr("data-key"))) setExpanded($(this), true);
    });
  }

  // curves are open by default where there is room for them next to the story
  function isOpen(key) {
    if (Object.prototype.hasOwnProperty.call(expanded, key)) return expanded[key];
    return wide && key.charAt(0) === "t";
  }

  function bind() {
    var root = $("#fhempyTimeline");
    root.on("click", ".ftlRange", function () {
      var n = +$(this).attr("data-days");
      var today = dayIso(new Date());
      load(addDays(today, 1 - n), today, false);
    });
    root.on("click", ".ftlPeriod", function () {
      var from = $(this).attr("data-from"), to = $(this).attr("data-to");
      var span = (dayDate(to) - dayDate(from)) / 86400000;
      if (span > 30) from = addDays(to, -30);
      load(from, to, false);
    });
    root.on("change", ".ftlDate", function () {
      var day = $(this).val();
      if (day) load(addDays(day, -6), day, false);
    });
    root.on("click", "[data-category]", function () {
      var c = $(this).attr("data-category");
      filter.categories[c] = filter.categories[c] === false;
      storageSet("categories", JSON.stringify(filter.categories));
      render();
    });
    root.on("input", ".ftlSearch", function () {
      filter.search = $(this).val().toLowerCase();
      render();
    });
    root.on("click", ".ftlOlder", loadOlder);
    $(window).on("resize", function () {
      var root = $("#fhempyTimeline");
      if ((root.width() >= WIDE_MIN) !== wide || (root.width() < NARROW_MAX) !== root.hasClass("ftlNarrow")) render();
      else fitScroll();
    });
    root.on("click", ".ftlToggle, .ftlTrendToggle, .ftlSameToggle", function () {
      var key = $(this).attr("data-key");
      expanded[key] = !isOpen(key);
      setExpanded($(this), expanded[key]);
    });
    root.on("click", "[data-onchange]", onChangeClick);
    root.on("click", "a.ftlDevice", deviceClick);
    root.on("click", ".ftlDetails", function () {
      showDetails($(this).attr("data-day"));
    });
    root.on("click", "[data-hide]", function () {
      var target = $(this).attr("data-hide");
      cmd("set " + device + " hide " + target, function () {
        days.forEach(function (day) {
          day.entries = day.entries.filter(function (e) { return e.device + ":" + e.reading !== target; });
        });
        render();
      });
    });
  }

  // value and time of the curve point under the mouse or finger
  function showTip(e) {
    var svg = this;
    var tips;
    try { tips = JSON.parse(svg.getAttribute("data-tip")); } catch (err) { return; }
    var ev = e.originalEvent && e.originalEvent.touches && e.originalEvent.touches.length ? e.originalEvent.touches[0] : e;
    var rect = svg.getBoundingClientRect();
    if (!tips.length || !rect.width) return;
    var x = (ev.clientX - rect.left) * 100 / rect.width;
    var best = tips[0];
    tips.forEach(function (t) { if (Math.abs(t[0] - x) < Math.abs(best[0] - x)) best = t; });
    var text = clock(best[1]) + "–" + clock(best[1] + 3600) + ": " + fmt(best[2]);
    if (svg.getAttribute("data-tipday")) {
      text = new Date(best[1] * 1000).toLocaleDateString(undefined, { weekday: "short", day: "numeric", month: "short" }) + " " + text;
    }
    var cursor = svg.querySelector(".ftlCursor");
    if (!cursor) {
      cursor = document.createElementNS("http://www.w3.org/2000/svg", "line");
      cursor.setAttribute("class", "ftlCursor");
      cursor.setAttribute("y1", "0");
      cursor.setAttribute("y2", "100");
      cursor.setAttribute("stroke", "rgba(128,128,128,0.6)");
      cursor.setAttribute("stroke-width", "1");
      cursor.setAttribute("vector-effect", "non-scaling-stroke");
      svg.appendChild(cursor);
    }
    cursor.setAttribute("x1", best[0]);
    cursor.setAttribute("x2", best[0]);
    var tip = $("#fhempyTimelineTip");
    if (!tip.length) tip = $('<div id="fhempyTimelineTip"></div>').appendTo("body");
    tip.text(text).show();
    var left = rect.left + best[0] * rect.width / 100 - tip.outerWidth() / 2;
    left = Math.max(4, Math.min(left, $(window).width() - tip.outerWidth() - 4));
    tip.css({ left: left, top: Math.max(4, rect.top - tip.outerHeight() - 4) });
  }

  function hideTip() {
    $("#fhempyTimelineTip").hide();
    $("svg[data-tip] .ftlCursor").remove();
  }

  function bindTips() {
    if (bindTips.done) return;
    bindTips.done = true;
    $(document).on("mousemove touchstart touchmove", "svg[data-tip]", showTip);
    $(document).on("click", "svg[data-curve]", curveClick);
    $(document).on("mouseleave", "svg[data-tip]", hideTip);
    $(document).on("touchstart", function (e) {
      if (!$(e.target).closest("svg[data-tip]").length) hideTip();
    });
    document.addEventListener("scroll", hideTip, true);
  }

  // room view: the summary of the timeline device takes the whole width
  // instead of its row in the device table
  window.fhempyTimelineRoom = function (name) {
    var marker = $("#fhempyTimelineRoom");
    var row = marker.closest("tr");
    if (!$("#fhempyTimeline").length) {
      var page = row.parents("table").last();
      $('<div id="fhempyTimeline" class="ftlRoom"></div>').insertBefore(page.length ? page : marker);
    }
    row.hide();
    var block = row.closest("table.block");
    if (block.length && !block.find("> tbody > tr:visible, > tr:visible").length) {
      block.closest("tr").hide().prev("tr.devTypeTr").hide();
    }
    if (device !== name) window.fhempyTimeline(name);
  };

  window.fhempyTimeline = function (name) {
    device = name;
    css();
    try {
      filter.categories = JSON.parse(storageGet("categories") || "{}") || {};
    } catch (e) {
      filter.categories = {};
    }
    days = [];
    bind();
    bindTips();
    var today = dayIso(new Date());
    load(addDays(today, -6), today, false);
  };
})();
