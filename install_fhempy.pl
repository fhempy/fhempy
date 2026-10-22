# Installs fhempy in FHEM, enter this line in the FHEM command field:
# {eval GetFileFromURL("https://raw.githubusercontent.com/fhempy/fhempy/master/install_fhempy.pl")}
#
# Downloads the fhempy FHEM modules, loads them without restart and defines
# fhempy_local, which installs Python (if needed) and fhempy on its own.
# In FHEMWEB a dialog shows the progress. Running it again is harmless.

my $controls = "https://raw.githubusercontent.com/fhempy/fhempy/master/controls_pythonbinding.txt";

my $ret = fhem("update add $controls", 1);
{
  # wait for the download, the modules are loaded right afterwards
  local $attr{global}{updateInBackground} = 0;
  $ret = fhem("update all pythonbinding", 1);
}

my $error;
my $msg = "fhempy is being installed, watch the progress of fhempy_local in the room fhempy";
if (!-r "$attr{global}{modpath}/FHEM/10_BindingsIo.pm") {
  $error = "Downloading the fhempy files didn't work. Please check the internet connection of FHEM.";
  $msg = "fhempy installation failed, downloading the fhempy files didn't work:\n$ret";
} elsif (my $err = CommandReload(undef, "10_BindingsIo")) {
  $error = "Loading 10_BindingsIo.pm failed: $err";
  $msg = "fhempy installation failed: $err";
} elsif (defined($defs{fhempy_local})) {
  $msg = "fhempy files updated, fhempy_local exists already (room fhempy)";
} elsif (my $def = CommandDefine(undef, "fhempy_local BindingsIo fhempy")) {
  $error = "define fhempy_local failed: $def";
  $msg = $error;
}

# plain text for telnet and other clients
return $msg if (!defined($cl) || ($cl->{TYPE} // "") ne "FHEMWEB");

# FHEMWEB shows answers starting with <html> as HTML in a dialog
my $html = <<'HTML';
<html><div id="fhempyInstall" style="font-family:'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif;line-height:1.4">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 440 128" style="width:260px;height:auto;display:block;margin:4px auto 14px">
<defs><linearGradient id="fhempyInstallBg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#4B8BBE"/><stop offset="1" stop-color="#2B5B84"/></linearGradient></defs>
<rect width="128" height="128" rx="28" fill="url(#fhempyInstallBg)"/>
<path d="M64 22 L108 58 L98 58 L98 104 L30 104 L30 58 L20 58 Z" fill="#fff" stroke="#fff" stroke-width="6" stroke-linejoin="round"/>
<path d="M40 86 C46 72 54 72 58 84 C62 96 72 96 76 84 L80 74" fill="none" stroke="#FFD43B" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>
<ellipse cx="84" cy="70" rx="9" ry="7.5" fill="#FFD43B"/><circle cx="86" cy="68" r="2" fill="#2B5B84"/>
<text x="152" y="84" font-family="'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif" font-size="68" font-weight="700" fill="currentColor">fhem<tspan fill="#4B8BBE">py</tspan></text>
<text x="155" y="114" font-family="'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif" font-size="19" fill="currentColor" opacity="0.75">Python modules for FHEM</text>
</svg>
<div id="fhempyInstallTitle" style="font-size:16px;font-weight:600;margin-bottom:10px">Installing fhempy</div>
<div style="height:8px;border-radius:4px;background:rgba(128,128,128,0.25);overflow:hidden;margin-bottom:14px">
<div id="fhempyInstallBar" style="height:100%;width:20%;background:linear-gradient(90deg,#4B8BBE,#2B5B84);border-radius:4px;transition:width 0.6s"></div></div>
<div id="fhempyInstallSteps"></div>
<div id="fhempyInstallInfo" style="margin-top:12px;font-size:13px;opacity:0.8">This takes a few minutes, up to 15 minutes on a Raspberry Pi. You can close this window, the installation continues.</div>
</div>
<style>@keyframes fhempyInstallSpin{to{transform:rotate(360deg)}}</style>
<script>
(function(){
  var steps = ["Downloading the fhempy files", "Installing uv", "Setting up Python",
               "Installing fhempy", "Starting fhempy"];
  var error = __ERROR__;
  function icon(kind) {
    var base = "display:inline-block;width:16px;height:16px;border-radius:50%;margin-right:10px;vertical-align:-3px;box-sizing:border-box;";
    if (kind == "done") return '<span style="'+base+'background:#3fa34d;color:#fff;font-size:11px;line-height:16px;text-align:center">&#10003;</span>';
    if (kind == "fail") return '<span style="'+base+'background:#d64545;color:#fff;font-size:11px;line-height:16px;text-align:center">&#10005;</span>';
    if (kind == "run") return '<span style="'+base+'border:2px solid #4B8BBE;border-top-color:transparent;animation:fhempyInstallSpin 1s linear infinite"></span>';
    return '<span style="'+base+'border:2px solid rgba(128,128,128,0.5)"></span>';
  }
  function esc(t) { return $("<div>").text(t).html(); }
  var bar = "linear-gradient(90deg,#4B8BBE,#2B5B84)";
  function show(current, failed, info) {
    var html = "";
    for (var i = 0; i < steps.length; i++) {
      var kind = i < current ? "done" : (i == current ? (failed ? "fail" : "run") : "todo");
      html += '<div style="margin:6px 0;'+(kind == "todo" ? "opacity:0.55" : "")+'">'+icon(kind)+esc(steps[i])+'</div>';
    }
    $("#fhempyInstallSteps").html(html);
    $("#fhempyInstallBar").css("width", Math.round(100*Math.min(current, steps.length)/steps.length)+"%")
      .css("background", failed ? "#d64545" : (current >= steps.length ? "#3fa34d" : bar));
    if (info !== undefined) $("#fhempyInstallInfo").html(info);
  }
  /* what to set up next, a click defines the device */
  var setups = [
    {type:"matter", name:"matter", title:"Matter", logo:'<img src="data:image/png;base64,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" width="48" height="48">',
     text:"Control Matter devices: lights, plugs, sensors..."},
    {type:"matter_bridge", name:"matterbridge", title:"Matter Bridge",
     logo:'<span style="position:relative;display:inline-block"><img src="data:image/png;base64,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" width="48" height="48"><span style="position:absolute;right:-6px;bottom:-4px;background:#4B8BBE;color:#fff;border-radius:50%;width:22px;height:22px;font-size:13px;line-height:22px;text-align:center;border:2px solid #fff">&#8644;</span></span>',
     text:"Your FHEM devices in Apple Home, Google Home and Alexa"},
    {type:"zigbee2mqtt", name:"z2m", title:"Zigbee2MQTT", logo:'<img src="data:image/png;base64,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" width="48" height="48">',
     text:"Zigbee devices without a vendor hub"},
    {type:"mcp_server", name:"AI", title:"AI (MCP server)", logo:'<svg xmlns="http://www.w3.org/2000/svg" viewBox="10 10 175 175" width="48" height="48" fill="none"><path d="M25 97.8528L92.8823 29.9706C102.255 20.598 117.451 20.598 126.823 29.9706V29.9706C136.196 39.3431 136.196 54.5391 126.823 63.9117L75.5581 115.177" stroke="currentColor" stroke-width="12" stroke-linecap="round"/><path d="M76.2653 114.47L126.823 63.9117C136.196 54.5391 151.392 54.5391 160.765 63.9117L161.118 64.2652C170.491 73.6378 170.491 88.8338 161.118 98.2063L99.7248 159.6C96.6006 162.724 96.6006 167.789 99.7248 170.913L112.331 183.52" stroke="currentColor" stroke-width="12" stroke-linecap="round"/><path d="M109.853 46.9411L59.6482 97.1457C50.2757 106.518 50.2757 121.714 59.6482 131.087V131.087C69.0208 140.459 84.2168 140.459 93.5894 131.087L143.794 80.8822" stroke="currentColor" stroke-width="12" stroke-linecap="round"/></svg>',
     text:"Control FHEM in plain language with AI apps"}
  ];
  function tileState(i, html) { $("#fhempySetup"+i+" .fhempySetupAction").html(html); }
  function openLink(name) {
    return '<a href="'+FW_root+'?detail='+encodeURIComponent(name)+'" style="font-weight:600">Open '+esc(name)+'</a>';
  }
  function setupTiles() {
    var html = '<div style="font-weight:600;margin:4px 0 8px">What would you like to set up?</div>'+
      '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">';
    for (var i = 0; i < setups.length; i++) {
      var t = setups[i];
      html += '<div id="fhempySetup'+i+'" class="fhempySetupTile" data-i="'+i+'" style="border:1px solid rgba(128,128,128,0.35);'+
        'border-radius:12px;padding:12px;cursor:pointer;text-align:center;transition:transform 0.15s,box-shadow 0.15s">'+
        '<div style="height:52px;display:flex;align-items:center;justify-content:center">'+t.logo+'</div>'+
        '<div style="font-weight:600;margin-top:6px">'+t.title+'</div>'+
        '<div style="font-size:12px;opacity:0.75;min-height:32px">'+t.text+'</div>'+
        '<div class="fhempySetupAction" style="margin-top:6px"><span style="display:inline-block;padding:3px 14px;border-radius:12px;'+
        'background:#4B8BBE;color:#fff;font-size:13px">Set up</span></div></div>';
    }
    $("#fhempyInstallSteps").html(html + '</div>');
    $("#fhempyInstallInfo").html('More modules: <a href="https://github.com/fhempy/fhempy#-modules" target="_blank">module list</a>');
    $(".fhempySetupTile").hover(
      function(){ $(this).css({transform:"translateY(-2px)", "box-shadow":"0 4px 12px rgba(0,0,0,0.15)"}); },
      function(){ $(this).css({transform:"", "box-shadow":""}); });
    /* tiles of modules which are defined already */
    var cmd = '{join(",", map {InternalVal($_,"FHEMPYTYPE","").":".$_} devspec2array("TYPE=fhempy"))}';
    FW_cmd(FW_root+"?cmd="+encodeURIComponent(cmd)+"&XHR=1", function(r) {
      var defined = {};
      (r || "").replace(/[\r\n]+$/, "").split(",").forEach(function(d) {
        var p = d.split(":"); if (p[1]) defined[p[0]] = p[1];
      });
      setups.forEach(function(t, i) {
        if (defined[t.type]) { t.done = defined[t.type]; tileState(i, '&#10003; set up &middot; '+openLink(t.done)); }
      });
    });
    $(".fhempySetupTile").click(function(e) {
      var i = $(this).data("i"), t = setups[i];
      if (t.done || t.busy || $(e.target).is("a")) return;
      t.busy = true;
      tileState(i, icon("run")+"setting up...");
      FW_cmd(FW_root+"?cmd="+encodeURIComponent("define "+t.name+" fhempy "+t.type)+"&XHR=1", function(r) {
        t.busy = false;
        r = (r || "").replace(/[\r\n]+$/, "");
        if (r != "") { tileState(i, '<span style="color:#d64545;font-size:12px">'+esc(r)+'</span>'); return; }
        t.done = t.name;
        tileState(i, icon("done")+openLink(t.name));
      });
    });
  }
  function poll() {
    if (!document.getElementById("fhempyInstall")) return;
    var cmd = '{ReadingsVal("fhempy_local","state","")."|".ReadingsVal("fhempy_local","version","")}';
    FW_cmd(FW_root+"?cmd="+encodeURIComponent(cmd)+"&XHR=1", function(r) {
      var p = (r || "").replace(/[\r\n]+$/, "").split("|");
      var state = p[0] || "", version = p[1] || "";
      var m = state.match(/: (\d)\/\d /);
      if (version != "" && !/^Installing/.test(state)) {
        show(steps.length, false, '');
        $("#fhempyInstallTitle").text("fhempy "+version+" is ready");
        setupTiles();
        $("#fhempyInstall").dialog && $("#fhempyInstall").dialog("option", "buttons", [
          {text:"Open the room fhempy", click:function(){ location.href = FW_root+"?room=fhempy"; }},
          {text:"Close", click:function(){ $(this).dialog("close"); }}]);
        return;
      }
      if (/failed/.test(state)) {
        show(m ? parseInt(m[1]) : 1, true, esc(state.replace(/^Installing fhempy (failed: )?/, ""))+
          '<br>Details are in the fhempy log (log/fhempy-*.log).');
        $("#fhempyInstallTitle").text("fhempy installation failed");
        return;
      }
      show(m ? parseInt(m[1]) : 1, false);
      setTimeout(poll, 2000);
    });
  }
  /* show the progress as dialog on top of the page */
  var box = $("#fhempyInstall");
  if (box.dialog) {
    box.dialog({modal:true, width:Math.min(520, $(window).width()*0.95), resizable:false, title:"fhempy installation",
      buttons:[{text:"Close", click:function(){ $(this).dialog("close"); }}],
      close:function(){ $(this).remove(); }});
  }
  if (error) {
    show(0, true, esc(error));
    $("#fhempyInstallTitle").text("fhempy installation failed");
  } else {
    show(1, false);
    poll();
  }
})();
</script></html>
HTML

my $js_error = "null";
if (defined($error)) {
  ($js_error = $error) =~ s/([\\"])/\\$1/g;
  $js_error =~ s/\n/\\n/g;
  $js_error =~ s/<\//<\\\//g;
  $js_error = "\"$js_error\"";
}
$html =~ s/__ERROR__/$js_error/;
$html =~ s/\n//g;
$html;
