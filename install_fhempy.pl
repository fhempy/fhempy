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
        $("#fhempyInstallInfo").html('Pick a module from the <a href="https://github.com/fhempy/fhempy#-modules" target="_blank">module list</a> '+
          'and define it like any other FHEM device, e.g. <code>define upnp fhempy discover_upnp</code>');
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
