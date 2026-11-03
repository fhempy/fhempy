#!/usr/bin/env perl
use strict;
use warnings;

use Test2::V0;
use Test2::Tools::Compare qw{ is };
our $init_done;

is(CommandReload(undef, "10_fhempyServer"), U(), "10_fhempyServer loaded");

# while FHEM starts, the attr lines of fhem.cfg come after Define and
# before init_done, the logfile attribute must be used anyway
my $saved_init_done = $init_done;
$init_done = 0;
is(CommandDefine(undef, "fhempyLogfileTest fhempyServer 15798"), U(), "defined while FHEM starts");
is($defs{fhempyLogfileTest}{logfile}, "./log/fhempy-%Y-%m-%d.log", "default logfile after Define");
CommandAttr(undef, "fhempyLogfileTest logfile ./log/fhempy-%Y-%m.log");
is($defs{fhempyLogfileTest}{logfile}, "./log/fhempy-%Y-%m.log", "logfile attribute used while FHEM starts");

# without init_done fhempy isn't started by the test
CommandDeleteAttr(undef, "fhempyLogfileTest logfile");
is($defs{fhempyLogfileTest}{logfile}, "./log/fhempy-%Y-%m-%d.log", "default logfile after deleteattr");
$init_done = $saved_init_done;

CommandDelete(undef, "fhempyLogfileTest");

done_testing();

exit(0);  # necessary

1;
