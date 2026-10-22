# Installs fhempy in FHEM, enter this line in the FHEM command field:
# {eval GetFileFromURL("https://raw.githubusercontent.com/fhempy/fhempy/master/install_fhempy.pl")}
#
# Downloads the fhempy FHEM modules, loads them without restart and defines
# fhempy_local, which installs Python (if needed) and fhempy on its own.
# Running it again is harmless.

my $controls = "https://raw.githubusercontent.com/fhempy/fhempy/master/controls_pythonbinding.txt";

my $ret = fhem("update add $controls", 1);
{
  # wait for the download, the modules are loaded right afterwards
  local $attr{global}{updateInBackground} = 0;
  $ret = fhem("update all pythonbinding", 1);
}
if (!-r "$attr{global}{modpath}/FHEM/10_BindingsIo.pm") {
  "fhempy installation failed, downloading the fhempy files didn't work:\n$ret";
} elsif (my $err = CommandReload(undef, "10_BindingsIo")) {
  "fhempy installation failed: $err";
} elsif (defined($defs{fhempy_local})) {
  "fhempy files updated, fhempy_local exists already (room fhempy)";
} else {
  CommandDefine(undef, "fhempy_local BindingsIo fhempy")
    // "fhempy is being installed, watch the progress of fhempy_local in the room fhempy";
}
