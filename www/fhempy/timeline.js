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
      "#fhempyTimeline a.ftlTitle{color:inherit;text-decoration:none}" +
      "#fhempyTimeline .ftlSettings{font-size:13px;font-weight:400;opacity:0.65;margin-left:6px}" +
      "#fhempyTimeline a.ftlTitle:hover .ftlSettings{opacity:1;text-decoration:underline}" +
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
      ".ftlChoice{position:relative;display:inline-flex;flex-wrap:wrap;gap:4px;align-items:center;font-size:11px;" +
      "padding:4px 22px 4px 6px;border-radius:6px;background:rgba(128,128,128,0.13);max-width:100%;box-sizing:border-box}" +
      "#fhempyTimeline .ftlChoice .ftlAction,.ftlChoice .ftlAction{opacity:1;margin-left:0;background:rgba(255,255,255,0.5)}" +
      ".ftlChoice .ftlNo{position:absolute;top:3px;right:5px;cursor:pointer;opacity:0.7}" +
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
      ".ftcChart{position:relative;touch-action:pan-y;transition:opacity .15s}" +
      ".ftcChart.ftcLoading{opacity:0.4}" +
      ".ftcChart svg{display:block;width:100%;overflow:visible;cursor:crosshair}" +
      ".ftcChart svg[data-curve]{cursor:zoom-in}" +
      ".ftcChart text{fill:currentColor;opacity:0.6;font-size:11px}" +
      ".ftcTip{position:absolute;top:0;pointer-events:none;background:rgba(40,40,40,0.92);color:#fff;font-size:12px;" +
      "padding:4px 8px;border-radius:6px;white-space:nowrap;display:none}" +
      ".ftcTip b{font-size:15px}" +
      ".ftcEmpty{display:flex;align-items:center;justify-content:center;opacity:0.6}" +
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
      "#fhempyTimelineDevice .ftlSection{font-weight:600;margin:10px 0 4px}" +
      "#fhempyTimelineDevice .ftlEntry{display:grid;grid-template-columns:44px 10px minmax(0,1fr) auto;gap:8px;padding:3px 0;align-items:start}" +
      "#fhempyTimelineDevice .ftlTime{font-size:13px;opacity:0.7;font-variant-numeric:tabular-nums;padding-top:1px}" +
      "#fhempyTimelineDevice .ftlDot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-top:5px}" +
      "#fhempyTimelineDevice .ftlMeta{font-size:12px;opacity:0.65}" +
      "#fhempyTimelineDevice .ftlBarLine{height:4px;border-radius:2px;margin-top:4px;opacity:0.55;max-width:100%}" +
      "#fhempyTimelineDevice .ftlAlert{background:rgba(208,102,42,0.13);border-radius:6px;padding:5px 6px;margin:0 -6px}" +
      "#fhempyTimelineDevice .ftlAction{font-size:11px;cursor:pointer;border:1px solid rgba(128,128,128,0.4);border-radius:4px;padding:0 5px;white-space:nowrap}" +
      "#fhempyTimelineDevice a.ftlOpen{border:1px solid rgba(128,128,128,0.4);border-radius:14px;padding:2px 11px;font-size:13px;color:inherit;text-decoration:none;white-space:nowrap}" +
      "#fhempyTimelineDevice .ftlDevChart{margin:4px 0 14px}" +
      "#fhempyTimelineDevice .ftaBlock{margin:4px 0 16px}" +
      "#fhempyTimelineDevice .ftaHead{font-size:15px}#fhempyTimelineDevice .ftaHead b{font-weight:600}" +
      "#fhempyTimelineDevice .ftaName{opacity:0.7}" +
      "#fhempyTimelineDevice .ftaStats{font-size:12px;opacity:0.65;margin:1px 0 6px}" +
      "#fhempyTimelineDevice .ftaRow{display:grid;grid-template-columns:76px minmax(0,1fr);align-items:center;gap:6px;height:18px;font-size:11px}" +
      "#fhempyTimelineDevice .ftaRow>span{opacity:0.65;white-space:nowrap;overflow:hidden}" +
      "#fhempyTimelineDevice .ftaRow.ftaCompact{height:11px}" +
      "#fhempyTimelineDevice .ftaBar{position:relative;height:12px}" +
      "#fhempyTimelineDevice .ftaCompact .ftaBar{height:8px}" +
      "#fhempyTimelineDevice .ftaPast{position:absolute;left:0;top:0;bottom:0;background:rgba(128,128,128,0.12);border-radius:2px}" +
      "#fhempyTimelineDevice .ftaSeg{position:absolute;top:0;bottom:0;border-radius:2px;min-width:2px;cursor:default}" +
      "#fhempyTimelineDevice .ftaTick{width:2px;margin-left:-1px;opacity:0.85}" +
      "#fhempyTimelineDevice .ftaAxis{height:14px}" +
      "#fhempyTimelineDevice .ftaAxis div{display:flex;justify-content:space-between;opacity:0.55}" +
      "#fhempyTimelineDevice .ftlValues{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,230px),1fr));column-gap:20px;font-size:13px}" +
      "#fhempyTimelineDevice .ftlValues>div{display:flex;justify-content:space-between;gap:8px;padding:3px 0;border-bottom:1px solid rgba(128,128,128,0.15)}" +
      "#fhempyTimelineDevice .ftlValues span:first-child{opacity:0.7}" +
      ".ftcLegend{display:flex;flex-wrap:wrap;gap:4px 16px;align-items:center;font-size:13px;margin:0 0 4px}" +
      ".ftcKey{white-space:nowrap}.ftcKey b{font-weight:600}" +
      ".ftcKey i{display:inline-block;width:14px;height:3px;border-radius:2px;vertical-align:middle;margin-right:6px}" +
      ".ftcKey i.ftcDash{height:0;border-top:2px dashed;background:none!important;border-radius:0}" +
      "#fhempyTimeline .ftlTarget{opacity:0.75;color:#d0662a}" +
      "#fhempyTimelineDevice .ftlEmpty{opacity:0.75;margin:8px 0}" +
      "#fhempyTimelineDetails .ftlDetail{display:grid;grid-template-columns:70px 1fr auto;gap:8px;padding:3px 0;border-bottom:1px solid rgba(128,128,128,0.2);font-size:13px}" +
      "#fhempyTimelineDetails .ftlAction{font-size:11px;cursor:pointer;margin-left:4px;border:1px solid rgba(128,128,128,0.4);border-radius:4px;padding:0 5px;white-space:nowrap}" +
      "#fhempyTimelineDetails .ftlDetail>span:last-child{display:flex;flex-wrap:wrap;gap:4px;justify-content:flex-end;align-items:center}" +
      "@media (max-width:600px){#fhempyTimelineDetails .ftlDetail{grid-template-columns:48px 1fr}#fhempyTimelineDetails .ftlDetail>span:last-child{grid-column:2;justify-content:flex-start}#fhempyTimelineDetails .ftlAction{margin-left:0}}" +
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

  // regexp of exactly this value for hidden and skip_events, without spaces
  // and ";" which would end the FHEM command
  function valueRule(value) {
    return String(value).trim().replace(/[.*+?^${}()|[\]\\\/]/g, "\\$&").replace(/\s/g, "\\s").replace(/;/g, "\\x3b");
  }

  function shortValue(value) {
    var text = String(value).trim();
    return text.length > 24 ? text.substring(0, 23) + "…" : text;
  }

  // "Hide from story" and "Stop recording" ask: the whole reading or only this value
  function choiceHtml(attr, verb, item) {
    var target = item.device + ":" + item.reading;
    var html = '<span class="ftlChoice">' + verb + ' <span class="ftlAction" ' + attr + '="' + esc(target) +
      '" title="' + esc(target) + '">every ' + esc(item.reading) + "</span>";
    html += '<span class="ftlAction" ' + attr + '="' + esc(target + ":" + valueRule(item.value)) + '" title="' +
      esc(target) + " only with the value " + esc(String(item.value).trim()) + '">only “' + esc(shortValue(item.value)) + "”</span>";
    return html + '<span class="ftlNo" title="Cancel">✕</span></span>';
  }

  function hasValue(item) {
    return item.value !== undefined && item.value !== null && String(item.value).trim() !== "";
  }

  // does device:reading or device:reading:value of the button match the item
  function ruleMatches(target, item) {
    var parts = target.split(":");
    if (parts[0] !== item.device || parts[1] !== item.reading) return false;
    if (parts.length < 3) return true;
    try {
      return new RegExp("^(?:" + parts.slice(2).join(":") + ")$", "i").test(String(item.value).trim());
    } catch (e) {
      return false;
    }
  }

  function onChangeAction(item) {
    if (!item.device || item.on_change) return "";
    // the same button pressed twice are two presses, not a repeat
    if (/^(action|click|button|key|press(ed)?|event|scene)$/i.test(item.reading)) return "";
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
      html += '<span class="ftlActions">' + onChangeAction(entry) + '<span class="ftlAction" data-hideask="' + esc(entry.device + ":" + entry.reading) +
        '" data-ts="' + esc(entry.ts) + '" title="Don\'t show ' + esc(entry.device + ":" + entry.reading) + ' in the story anymore, it stays in the hidden events">Hide from story</span></span>';
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

  function withUnit(v, unit) {
    return v === null || v === undefined ? "–" : fmt(v) + (unit ? (unit === "%" ? "" : " ") + unit : "");
  }

  function rangeText(min, max, unit) {
    return min === max ? withUnit(min, unit) : fmt(min) + " – " + withUnit(max, unit);
  }

  function readingName(t) {
    var name = t.name || t.reading;
    return name.charAt(0).toUpperCase() + name.slice(1);
  }

  var TARGET_COLOR = "#d0662a";

  function sparkline(trend, dayStart) {
    var pts = [], tips = [], target = trend.target ? trend.target.points : [];
    var low = trend.min, high = trend.max;
    if (trend.target) { low = Math.min(low, trend.target.min); high = Math.max(high, trend.target.max); }
    var span = high - low || 1;
    var y = function (v) { return (24 - (v - low) / span * 20).toFixed(1); };
    trend.points.forEach(function (v, i) {
      if (v === null) return;
      var x = i * 100 / 23;
      pts.push(x.toFixed(1) + "," + y(v));
      tips.push([+x.toFixed(2), dayStart + i * 3600, v, target[i] === undefined ? null : target[i]]);
    });
    var info = categoryInfo[trend.category] || categoryInfo.devices;
    if (!pts.length) return "";
    var line = "";
    if (trend.target) {
      // target temperature as dashed steps behind the measured one
      var steps = [], last = null;
      target.forEach(function (v, i) {
        if (v === null) return;
        var x = (i * 100 / 23).toFixed(1);
        if (last !== null) steps.push(x + "," + y(last));
        steps.push(x + "," + y(v));
        last = v;
      });
      if (steps.length > 1) {
        line += '<polyline fill="none" stroke="' + TARGET_COLOR + '" stroke-width="1.2" stroke-dasharray="3 2" vector-effect="non-scaling-stroke" points="' + steps.join(" ") + '"/>';
      }
    }
    line += pts.length > 1 ? '<polyline fill="none" stroke="' + info.color + '" stroke-width="1.5" vector-effect="non-scaling-stroke" points="' + pts.join(" ") + '"/>' : "";
    return '<svg viewBox="0 0 100 26" preserveAspectRatio="none" style="' + svgSize("26px") + '"' + tipAttr(tips) + ' data-unit="' + esc(trend.unit || "") + '"' +
      curveAttr(trend, dayIso(new Date(dayStart * 1000)), 1) + ">" + line + "</svg>";
  }

  function targetText(t) {
    if (!t.target) return "";
    return ' <span class="ftlTarget" title="' + esc(readingName(t.target)) + '">target ' + rangeText(t.target.min, t.target.max, t.unit) + "</span>";
  }

  function trendHtml(t, dayStart) {
    return '<div class="ftlTrend"><span class="ftlReading">' + esc(readingName(t)) + '</span> <span style="opacity:0.7">' +
      (t.changed ? rangeText(t.min, t.max, t.unit) : withUnit(t.min, t.unit)) + "</span>" + targetText(t) + " " +
      onChangeAction(t) + sparkline(t, dayStart) + "</div>";
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

  function dayTrends(day, changed) {
    return day.trends.filter(function (t) { return visible(t) && !t.changed === !changed; });
  }

  // the curves are only drawn when they are opened and scrolled into view,
  // hundreds of hidden charts made loading the timeline slow
  function trendsHtml(day) {
    var changed = dayTrends(day, true).length, same = dayTrends(day, false).length;
    if (!changed && !same) return "";
    var html = '<div class="ftlHiddenRow"><span class="ftlLink ftlTrendToggle" data-key="t' + day.day + '">Curves (' + changed + " changed" +
      (same ? ", " + same + " unchanged" : "") + ")</span></div>" +
      '<div class="ftlTrendBox" style="display:none"><div class="ftlTrends" data-trends="' + day.day + '" data-changed="1"></div>';
    if (same) {
      html += '<div class="ftlHiddenRow"><span class="ftlLink ftlSameToggle" data-key="s' + day.day + '" data-count="' + same + '">Show ' + same +
        " unchanged curves</span></div>" + '<div class="ftlTrends ftlSame" style="display:none" data-trends="' + day.day + '"></div>';
    }
    return html + "</div>";
  }

  function fillTrends(box) {
    var key = box.attr("data-trends");
    if (!key) return;
    box.removeAttr("data-trends");
    var day = days.filter(function (d) { return d.day === key; })[0];
    if (day) box.html(trendGroupsHtml(dayTrends(day, box.attr("data-changed")), dayDate(day.day).getTime() / 1000));
  }

  var trendObserver = null;
  // days drawn right away, the others when they are scrolled near
  var LAZY_AFTER = 2;
  var lazyDays = 0;

  // fill opened curve boxes once they come near the visible part of the list
  function showTrends(box) {
    if (!box.attr("data-trends")) return;
    if (trendObserver) trendObserver.observe(box[0]);
    else fillTrends(box);
  }

  function observeTrends(list) {
    if (trendObserver) trendObserver.disconnect();
    trendObserver = null;
    if (!window.IntersectionObserver || !list.length) return;
    var observer = new IntersectionObserver(function (seen) {
      seen.forEach(function (e) {
        if (!e.isIntersecting) return;
        observer.unobserve(e.target);
        if (e.target.hasAttribute("data-entries")) fillEntries($(e.target));
        else fillTrends($(e.target));
      });
    }, { root: list[0], rootMargin: "600px 0px" });
    trendObserver = observer;
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
    // newest first, like the days; on wide screens the curves are shown next to the story;
    // the entries of a day are drawn when it comes near the visible part
    html += '<div class="ftlDayMain">';
    if (lazyDays-- > 0) html += entriesHtml(entries);
    else html += '<div class="ftlLazy" data-entries="' + day.day + '" style="min-height:' + Math.min(entries.length * 40, 4000) + 'px"></div>';
    if (day.hidden) {
      html += '<div class="ftlHiddenRow"><span class="ftlLink ftlDetails" data-day="' + day.day + '">+ ' +
        day.hidden.toLocaleString() + " technical events and measurements</span></div>";
    }
    return html + '</div><div class="ftlDaySide">' + trendsHtml(day) + "</div></div>";
  }

  function entriesHtml(entries) {
    var html = "";
    entries.slice().reverse().forEach(function (entry) { html += entryHtml(entry); });
    return html;
  }

  function fillEntries(box) {
    var key = box.attr("data-entries");
    var day = days.filter(function (d) { return d.day === key; })[0];
    var nodes = $($.parseHTML(day ? entriesHtml(day.entries.filter(visible)) : ""));
    box.replaceWith(nodes);
    restoreExpanded(nodes);
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
    // in the room the way to the settings of the timeline device
    var title = $("#fhempyTimeline").hasClass("ftlRoom") ?
      '<a class="ftlTitle" href="' + esc(FW_root + "?detail=" + encodeURIComponent(device)) +
        '" title="Settings of ' + esc(device) + '">Timeline <span class="ftlSettings">&#9881; Settings</span></a>' :
      '<span class="ftlTitle">Timeline</span>';
    var html = '<div class="ftlBar">' + title +
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
    // without IntersectionObserver everything is drawn at once
    lazyDays = window.IntersectionObserver ? LAZY_AFTER : days.length;
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
    observeTrends(root.find(".ftlScroll"));
    root.find("[data-entries]").each(function () { trendObserver.observe(this); });
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

  // "Only on change" once per reading in the history of a device
  function onChangeOnce(item, shown) {
    var key = item.device + ":" + item.reading;
    if (shown[key]) return "";
    shown[key] = true;
    return onChangeAction(item);
  }

  function deviceEntryHtml(entry, shown) {
    // the room is the one of the device, no need to repeat it
    var meta = entryMeta($.extend({}, entry, { room: "" }));
    return '<div class="ftlEntry' + (entry.alert ? " ftlAlert" : "") + '"><span class="ftlTime">' + clock(entry.ts) + "</span>" +
      dot(entry.category) + '<div class="ftlText">' + esc(entry.short || entry.text) + (meta ? '<div class="ftlMeta">' + meta + "</div>" : "") +
      durationBar(entry) + "</div><span>" + onChangeOnce(entry, shown) + "</span></div>";
  }

  function lastValue(points) {
    return points.length ? points[points.length - 1][1] : null;
  }

  // legend of a curve: the latest values, the target temperature dashed
  function legendHtml(name, unit, points, target, color) {
    var html = '<span class="ftcKey"><i style="background:' + color + '"></i>' + esc(name) + " <b>" + withUnit(lastValue(points), unit) + "</b></span>";
    if (target) {
      html += '<span class="ftcKey"><i class="ftcDash" style="border-color:' + TARGET_COLOR + '"></i>' + esc(readingName(target)) +
        " <b>" + withUnit(lastValue(target.points), unit) + "</b></span>";
    }
    return html;
  }

  function sinceText(ts) {
    var day = dayIso(new Date(ts * 1000));
    var when = day === dayIso(new Date()) ? clock(ts) : shortDay(day) + " " + clock(ts);
    return "since " + when + " (" + duration(Date.now() / 1000 - ts) + ")";
  }

  function shortDay(day) {
    var today = dayIso(new Date());
    if (day === today) return "Today";
    if (day === addDays(today, -1)) return "Yesterday";
    return dayDate(day).toLocaleDateString(undefined, { weekday: "short", day: "numeric" });
  }

  // one row per day with the times something was on/open, newest day first
  function activityRows(a, data, days, color) {
    var html = "", now = Date.now() / 1000, compact = days > 7;
    var last = dayIso(new Date((data.to - 1) * 1000));
    for (var i = 0; i < days; i++) {
      var day = addDays(last, -i), start = dayDate(day).getTime() / 1000, end = dayDate(addDays(day, 1)).getTime() / 1000;
      var label = compact && i % 7 && i ? "" : shortDay(day);
      var elapsed = Math.max(0, Math.min(100, (now - start) * 100 / (end - start)));
      html += '<div class="ftaRow' + (compact ? " ftaCompact" : "") + '"><span>' + esc(label) + '</span><div class="ftaBar">' +
        '<i class="ftaPast" style="width:' + elapsed.toFixed(2) + '%"></i>';
      a.segments.forEach(function (seg) {
        var s0 = seg[0], s1 = seg[1] === null ? null : seg[1];
        if (s0 >= end || (s1 === null ? s0 < start : s1 <= start)) return;
        var left = (Math.max(s0, start) - start) * 100 / (end - start);
        var tip;
        if (s1 === null) {
          tip = clock(s0) + " " + seg[2];
          html += '<i class="ftaSeg ftaTick" data-text="' + esc(tip) + '" style="left:' + left.toFixed(2) + "%;background:" + color + '"></i>';
          return;
        }
        var width = Math.max(0.5, (Math.min(s1, end) - Math.max(s0, start)) * 100 / (end - start));
        tip = seg[2] + " " + clock(s0) + "–" + (s1 >= now - 60 ? "now" : clock(s1)) + " · " + duration(s1 - s0);
        html += '<i class="ftaSeg" data-text="' + esc(tip) + '" style="left:' + left.toFixed(2) + "%;width:" + width.toFixed(2) + "%;background:" + color + '"></i>';
      });
      html += "</div></div>";
    }
    return html + '<div class="ftaRow ftaAxis"><span></span><div><span>0</span><span>6</span><span>12</span><span>18</span><span>24</span></div></div>';
  }

  // door, light, motion...: state now, how often and how long, when
  function activityHtml(a, data, days) {
    var color = (categoryInfo[a.category] || categoryInfo.devices).color;
    var durations = a.segments.some(function (seg) { return seg[1] !== null; });
    var current = a.current.text.charAt(0).toUpperCase() + a.current.text.slice(1);
    var stats = durations ?
      esc(a.what) + " " + a.count + "× in " + days + " days · " + duration(a.total) + " in total · longest " + duration(a.longest) :
      a.count + (a.count === 1 ? " time" : " times") + " in " + days + " days";
    // a button has no state, only its last press
    var day = dayIso(new Date(a.current.since * 1000));
    var now = durations ? "<b>" + esc(current) + "</b> " + esc(sinceText(a.current.since)) :
      "last <b>" + esc(current) + "</b> " + (day === dayIso(new Date()) ? "at " : shortDay(day) + " ") + clock(a.current.since);
    return '<div class="ftaBlock"><div class="ftaHead">' + (a.name ? '<span class="ftaName">' + esc(readingName(a)) + " ·</span> " : "") +
      now + "</div>" +
      '<div class="ftaStats">' + stats + "</div>" + activityRows(a, data, days, color) + "</div>";
  }

  function deviceChartModel(t, data, days) {
    return {
      from: data.from, to: data.to, day: dayIso(new Date((data.to - 1) * 1000)), days: days, span: 3600,
      color: (categoryInfo[t.category] || categoryInfo.devices).color, unit: t.unit || "",
      points: t.points.map(function (p) { return [p[0], p[1], p[1], p[1]]; }),
      target: t.target ? t.target.points : null,
      curve: t.device + ":" + t.reading
    };
  }

  function deviceHtml(data, days) {
    var html = '<div class="ftlBar"><span class="ftlMeta" style="margin-right:auto">' +
      esc([data.type, (data.room || "").split(",")[0]].filter(function (x) { return x; }).join(" · ")) + "</span>" +
      '<span class="ftlChip ftlDeviceDays' + (days === 7 ? " ftlOn" : "") + '" data-days="7">7 days</span>' +
      '<span class="ftlChip ftlDeviceDays' + (days === 31 ? " ftlOn" : "") + '" data-days="31">31 days</span>' +
      '<a class="ftlOpen" href="' + esc(FW_root + "?detail=" + encodeURIComponent(data.device)) + '">Open device ›</a></div>';
    var changed = data.trends.filter(function (t) { return t.changed; });
    var same = data.trends.filter(function (t) { return !t.changed; });
    var shown = {};
    changed.forEach(function (t, i) {
      var info = categoryInfo[t.category] || categoryInfo.devices;
      html += '<div class="ftlDevChart"><div class="ftcLegend">' + legendHtml(readingName(t), t.unit, t.points, t.target, info.color) +
        onChangeOnce(t, shown) + "</div>" + '<div class="ftcChart ftcSmall" data-chart="' + i + '"></div></div>';
    });
    (data.activity || []).forEach(function (a) { html += activityHtml(a, data, days); });
    if (same.length) {
      html += '<div class="ftlSection">Values without change</div><div class="ftlValues">';
      same.forEach(function (t) {
        html += "<div><span>" + esc(readingName(t)) + "</span><span>" + withUnit(t.min, t.unit) + "</span></div>";
      });
      html += "</div>";
    }
    html += '<div class="ftlSection">What happened</div>';
    if (!data.entries.length) {
      html += '<div class="ftlEmpty">Nothing happened in the last ' + days + " days.</div>";
    }
    var lastDay = "";
    data.entries.forEach(function (entry) {
      var day = dayIso(new Date(entry.ts * 1000));
      if (day !== lastDay) {
        html += '<div class="ftlDayName" style="margin:8px 0 2px">' + esc(dayTitle(day)) + "</div>";
        lastDay = day;
      }
      html += deviceEntryHtml(entry, shown);
    });
    return html;
  }

  // draws the charts of the device popup once it has its width
  function drawDeviceCharts(d, data, days) {
    var changed = data.trends.filter(function (t) { return t.changed; });
    d.find(".ftcChart[data-chart]").each(function () {
      var chart = $(this), model = deviceChartModel(changed[+chart.attr("data-chart")], data, days);
      drawChart(chart, model, chart.width() < 500 ? 130 : 150);
    });
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

  function pointTime(ts, model) {
    var text = clock(ts) + "–" + clock(ts + model.span);
    if (model.days === 1) return text;
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
    var stat = function (value, text) { return '<div class="ftcStat"><b>' + withUnit(value, data.unit) + "</b><span>" + text + "</span></div>"; };
    return '<div class="ftcStats">' +
      stat(last[1], data.day === data.today ? "Now" : "Last · " + when(last)) +
      stat(data.min, "Lowest · " + when(low)) + stat(data.max, "Highest · " + when(high)) +
      stat(data.avg, "Average") + "</div>";
  }

  // time axis: hours of a day, weekdays or dates
  function timeAxis(m, x, top, h, height) {
    var svg = "", t, days = m.days;
    if (days === 1) {
      for (t = m.from; t <= m.to; t += 3 * 3600) {
        svg += '<text x="' + x(t).toFixed(1) + '" y="' + (height - 6) + '" text-anchor="middle">' + clock(t).slice(0, 2) + "</text>";
      }
      return svg;
    }
    var every = days <= 7 ? 1 : 7;
    for (var i = 0; i < days; i += every) {
      t = dayDate(addDays(m.day, i - days + 1)).getTime() / 1000;
      if (i) svg += '<line x1="' + x(t).toFixed(1) + '" x2="' + x(t).toFixed(1) + '" y1="' + top + '" y2="' + (top + h) + '" stroke="currentColor" stroke-opacity="0.12"/>';
      var label = days <= 7 ? new Date((t + 43200) * 1000).toLocaleDateString(undefined, { weekday: "short" }) : shortDate(addDays(m.day, i - days + 1));
      svg += '<text x="' + x(days <= 7 ? t + 43200 : t).toFixed(1) + '" y="' + (height - 6) + '" text-anchor="' + (days <= 7 ? "middle" : "start") + '">' + esc(label) + "</text>";
    }
    return svg;
  }

  // min-max band and average line, gaps where values are missing for more than 2 hours
  function curveLines(m, x, y) {
    var svg = "";
    var parts = [], part = [], last = null;
    m.points.forEach(function (p) {
      if (last !== null && p[0] - last > m.span + 7200) { parts.push(part); part = []; }
      last = p[0];
      part.push(p);
    });
    parts.push(part);
    parts.forEach(function (pts) {
      var mid = function (p) { return x(p[0] + m.span / 2).toFixed(1); };
      if (pts.length === 1) {
        svg += '<circle cx="' + mid(pts[0]) + '" cy="' + y(pts[0][1]).toFixed(1) + '" r="2.5" fill="' + m.color + '"/>';
        return;
      }
      if (pts.some(function (p) { return p[2] !== p[3]; })) {
        var band = pts.map(function (p) { return mid(p) + "," + y(p[3]).toFixed(1); }).concat(
          pts.slice().reverse().map(function (p) { return mid(p) + "," + y(p[2]).toFixed(1); }));
        svg += '<polygon points="' + band.join(" ") + '" fill="' + m.color + '" fill-opacity="0.15"/>';
      }
      svg += '<polyline fill="none" stroke="' + m.color + '" stroke-width="2" stroke-linejoin="round" points="' +
        pts.map(function (p) { return mid(p) + "," + y(p[1]).toFixed(1); }).join(" ") + '"/>';
    });
    return svg;
  }

  // target temperature: dashed steps, it only changes when somebody sets it
  function targetLine(m, x, y) {
    var steps = [], last = null;
    m.target.forEach(function (p) {
      var px = x(p[0]).toFixed(1);
      if (last !== null) steps.push(px + "," + y(last).toFixed(1));
      steps.push(px + "," + y(p[1]).toFixed(1));
      last = p[1];
    });
    if (last !== null) steps.push(x(m.target[m.target.length - 1][0] + m.span).toFixed(1) + "," + y(last).toFixed(1));
    return '<polyline fill="none" stroke="' + TARGET_COLOR + '" stroke-width="1.8" stroke-dasharray="5 4" points="' + steps.join(" ") + '"/>';
  }

  function targetAt(m, ts) {
    if (!m.target) return null;
    var value = null;
    m.target.forEach(function (p) { if (p[0] <= ts) value = p[1]; });
    return value;
  }

  // FHEMWEB styles (e.g. for phones) size every svg like an icon, the
  // charts always take the full width
  function svgSize(height) {
    return "display:block;width:100% !important;height:" + height + " !important;max-width:none !important;max-height:none !important";
  }

  // chart with axes into container, model: from, to, day, days, span,
  // color, unit, points [[hour, avg, min, max]], target [[hour, value]]
  function drawChart(container, m, height) {
    var width = Math.max(240, Math.floor(container.width()));
    if (!m.points.length) {
      container.html('<div class="ftcEmpty" style="height:' + height + 'px">No values in this period</div>');
      return;
    }
    var left = 46, right = 10, top = 10, bottom = 24;
    var w = width - left - right, h = height - top - bottom;
    var values = [];
    m.points.forEach(function (p) { values.push(p[2], p[3]); });
    (m.target || []).forEach(function (p) { values.push(p[1]); });
    var ticks = niceTicks(Math.min.apply(null, values), Math.max.apply(null, values));
    var low = ticks[0], span = ticks[ticks.length - 1] - low || 1;
    var x = function (ts) { return left + (ts - m.from) * w / (m.to - m.from); };
    var y = function (v) { return top + h - (v - low) * h / span; };
    var svg = '<svg width="' + width + '" height="' + height + '" viewBox="0 0 ' + width + " " + height + '" style="' + svgSize(height + "px") + '"' +
      (m.curve ? ' data-curve="' + esc(m.curve) + '" data-day="' + m.day + '" data-days="' + m.days + '"' : "") + ">";
    ticks.forEach(function (t) {
      svg += '<line x1="' + left + '" x2="' + (left + w) + '" y1="' + y(t).toFixed(1) + '" y2="' + y(t).toFixed(1) +
        '" stroke="currentColor" stroke-opacity="0.12"/>' +
        '<text x="' + (left - 6) + '" y="' + (y(t) + 4).toFixed(1) + '" text-anchor="end">' + fmt(t) + "</text>";
    });
    svg += timeAxis(m, x, top, h, height);
    if (m.target && m.target.length) svg += targetLine(m, x, y);
    svg += curveLines(m, x, y);
    svg += '<line class="ftcCross" y1="' + top + '" y2="' + (top + h) + '" stroke="currentColor" stroke-opacity="0.35" style="display:none"/>' +
      '<circle class="ftcDot" r="4" fill="' + m.color + '" stroke="#fff" stroke-width="1.5" style="display:none"/>';
    m.geometry = { x: x, y: y };
    container.html(svg + '</svg><div class="ftcTip"></div>').data("chart", m);
  }

  function chartHover(e) {
    var chart = $(this), m = chart.data("chart"), svg = chart.find("svg")[0];
    if (!m || !m.geometry || !svg) return;
    var ev = e.originalEvent && e.originalEvent.touches && e.originalEvent.touches.length ? e.originalEvent.touches[0] : e;
    var rect = svg.getBoundingClientRect();
    var px = ev.clientX - rect.left, g = m.geometry, half = m.span / 2, best = null;
    m.points.forEach(function (p) {
      if (!best || Math.abs(g.x(p[0] + half) - px) < Math.abs(g.x(best[0] + half) - px)) best = p;
    });
    var cx = g.x(best[0] + half), cy = g.y(best[1]);
    chart.find(".ftcCross").attr({ x1: cx, x2: cx }).show();
    chart.find(".ftcDot").attr({ cx: cx, cy: cy }).show();
    var target = targetAt(m, best[0] + half);
    var tip = chart.find(".ftcTip");
    tip.html("<b>" + withUnit(best[1], m.unit) + "</b>" +
      (best[2] !== best[3] ? ' <span style="opacity:0.75">' + fmt(best[2]) + " – " + fmt(best[3]) + "</span>" : "") +
      (target !== null ? '<br><span style="color:#f5a66f">Target ' + withUnit(target, m.unit) + "</span>" : "") +
      "<br>" + esc(pointTime(best[0], m))).show();
    var left = Math.max(0, Math.min(cx - tip.outerWidth() / 2, rect.width - tip.outerWidth()));
    var top = cy - tip.outerHeight() - 12;
    tip.css({ left: left, top: top < 0 ? cy + 12 : top });
  }

  function chartLeave() {
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
      (data.target ? '<div class="ftcLegend">' + legendHtml(readingName(data), data.unit, data.raw || data.points, data.target,
        (categoryInfo[data.category] || categoryInfo.devices).color) + "</div>" : "") +
      '<div class="ftcChart"></div><div class="ftcFoot">' +
      '<a href="#" class="ftcHistory">History of ' + esc(data.label) + "</a>" +
      '<a href="' + esc(FW_root + "?detail=" + encodeURIComponent(data.device)) + '">Open device</a>' +
      onChangeAction(data) + "</div>";
    d.html(html);
    var chart = d.find(".ftcChart");
    drawChart(chart, {
      from: data.from, to: data.to, day: data.day, days: days, span: curve.span, unit: data.unit || "",
      color: (categoryInfo[data.category] || categoryInfo.devices).color, points: data.points,
      target: data.target ? data.target.points : null
    }, chart.width() < 500 ? 200 : 260);
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
      if (curve.data.points && curve.span > 3600) {
        curve.data.points = bucketPoints(curve.data.points, curve.span, curve.data.from);
        if (curve.data.target) {
          // last target of each step
          var steps = {};
          curve.data.target.points.forEach(function (p) { steps[p[0] - ((p[0] - curve.data.from) % curve.span)] = p[1]; });
          curve.data.target.points = Object.keys(steps).map(function (t) { return [+t, steps[t]]; });
        }
      }
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
      d.dialog("option", "title", (curve.data.label || curve.target.split(":")[0]) + " · " +
        (curve.data.name ? readingName(curve.data) : curve.target.split(":")[1]));
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
      if (!data.error) drawDeviceCharts(d, data, days);
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
          '<span class="ftlAction" data-ignoreask="' + rows.indexOf(row) + '" title="Don\'t record ' +
          esc(row.device + ":" + row.reading) + ' at all anymore (attribute skip_events)">Stop recording</span></span></div>';
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
      d.on("click", "[data-ignoreask]", function () {
        var row = rows[parseInt($(this).attr("data-ignoreask"), 10)];
        if (!hasValue(row)) {
          ignore($(this), row.device + ":" + row.reading);
          return;
        }
        $(this).replaceWith(choiceHtml("data-ignore", "Stop recording:", row));
      });
      d.on("click", "[data-ignore]", function () {
        ignore($(this).parent(), $(this).attr("data-ignore"));
      });
      d.on("click", ".ftlNo", function () {
        var i = d.find(".ftlDetail").index($(this).closest(".ftlDetail"));
        $(this).parent().replaceWith('<span class="ftlAction" data-ignoreask="' + i + '">Stop recording</span>');
      });
      d.on("click", "[data-prune]", function () {
        var el = $(this);
        el.text("Deleting…").removeAttr("data-prune").removeClass("ftlAction");
        cmd("set " + device + " prune", function (r) { el.text((r || "").trim() || "Deleted"); });
      });

      function ignore(el, target) {
        cmd("set " + device + " ignore " + target, function (r) {
          if (r && r.trim()) {
            el.replaceWith('<span>' + esc(r.trim()) + "</span>");
            return;
          }
          d.find(".ftlDetail").each(function (i) {
            if (!ruleMatches(target, rows[i])) return;
            $(this).children().last().html('Not recorded anymore <span class="ftlAction" data-prune="1" ' +
              'title="Delete the events already recorded which match skip_events">Delete recorded events</span>');
          });
        });
      }
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
      var box = toggle.parent().next(".ftlTrendBox").toggle(open);
      if (open) showTrends(box.children(".ftlTrends").first());
    } else {
      var same = toggle.parent().next(".ftlSame");
      same.css("display", open ? "grid" : "none");
      if (open) showTrends(same);
      toggle.text(open ? "Hide unchanged curves" : "Show " + toggle.attr("data-count") + " unchanged curves");
    }
  }

  // what the user opened stays open when the timeline is drawn again,
  // e.g. after "Hide from story" or a filter
  function restoreExpanded(root) {
    root.find("[data-key]").addBack("[data-key]").each(function () {
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
    root.on("click", "[data-hideask]", function () {
      var target = $(this).attr("data-hideask");
      var ts = $(this).attr("data-ts");
      var entry = null;
      function find(e) {
        if (String(e.ts) === ts && e.device + ":" + e.reading === target) entry = e;
        (e.children || []).forEach(find);
      }
      days.forEach(function (day) { day.entries.forEach(find); });
      if (!entry || !hasValue(entry)) {
        hide(target);
        return;
      }
      $(this).replaceWith(choiceHtml("data-hide", "Hide from story:", entry));
    });
    root.on("click", "[data-hide]", function () {
      hide($(this).attr("data-hide"));
    });
    root.on("click", ".ftlNo", function () {
      render();
    });
  }

  function hide(target) {
    cmd("set " + device + " hide " + target, function (r) {
      if (r && r.trim()) return;
      days.forEach(function (day) {
        day.entries = day.entries.filter(function (e) { return !ruleMatches(target, e); });
      });
      render();
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
    var unit = svg.getAttribute("data-unit") || "";
    var text = clock(best[1]) + "–" + clock(best[1] + 3600) + ": " + withUnit(best[2], unit) +
      (best[3] !== null && best[3] !== undefined ? " · target " + withUnit(best[3], unit) : "");
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
    $(document).on("mousemove touchstart touchmove", ".ftcChart", chartHover);
    $(document).on("mouseenter touchstart", ".ftaSeg", function () {
      var rect = this.getBoundingClientRect();
      var tip = $("#fhempyTimelineTip");
      if (!tip.length) tip = $('<div id="fhempyTimelineTip"></div>').appendTo("body");
      tip.text($(this).attr("data-text")).show();
      var left = Math.max(4, Math.min(rect.left + rect.width / 2 - tip.outerWidth() / 2, $(window).width() - tip.outerWidth() - 4));
      tip.css({ left: left, top: Math.max(4, rect.top - tip.outerHeight() - 6) });
    });
    $(document).on("mouseleave", ".ftaSeg", hideTip);
    $(document).on("mouseleave", ".ftcChart", chartLeave);
    $(document).on("touchstart", function (e) {
      if (!$(e.target).closest("svg[data-tip], .ftaSeg").length) hideTip();
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
