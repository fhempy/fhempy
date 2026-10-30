#!/usr/bin/env perl
use strict;
use warnings;

use Test2::V0;
use Test2::Tools::Compare qw{ is like };
our $init_done;

is(CommandReload(undef, "10_fhempyServer"), U(), "10_fhempyServer loaded");
# devStateIcon is a FHEMWEB attribute
LoadModule("FHEMWEB");

# while FHEM starts, Define runs before the attr lines of fhem.cfg and must
# not create attributes the user deleted (fhempy isn't started without init_done)
my $saved_init_done = $init_done;
$init_done = 0;
is(CommandDefine(undef, "fhempyDefaultsTest fhempyServer 15799"), U(), "defined while FHEM starts");
$init_done = $saved_init_done;
my $hash = $defs{fhempyDefaultsTest};
is(AttrVal("fhempyDefaultsTest", "icon", ""), "", "no icon while FHEM starts");
is(AttrVal("fhempyDefaultsTest", "devStateIcon", ""), "", "no devStateIcon while FHEM starts");
is(AttrVal("fhempyDefaultsTest", "logfile", ""), "", "no logfile while FHEM starts");

# a new device at runtime gets the defaults, values of the user are kept
CommandAttr(undef, "fhempyDefaultsTest icon my_icon");
fhempyServer_setDefaultAttrs($hash);
is(AttrVal("fhempyDefaultsTest", "icon", ""), "my_icon", "icon of the user kept");
is(AttrVal("fhempyDefaultsTest", "room", ""), "fhempy", "room");
is(AttrVal("fhempyDefaultsTest", "group", ""), "fhempy", "group");
is(AttrVal("fhempyDefaultsTest", "nrarchive", ""), "10", "nrarchive");
like(AttrVal("fhempyDefaultsTest", "devStateIcon", ""), qr/Kill and restart/, "devStateIcon");
like(AttrVal("fhempyDefaultsTest", "logfile", ""), qr/fhempy-%Y-%m-%d\.log$/, "logfile");

CommandDelete(undef, "fhempyDefaultsTest");

done_testing();

exit(0);  # necessary

1;
