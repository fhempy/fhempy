#!/usr/bin/env perl
use strict;
use warnings;

use Test2::V0;
use Test2::Tools::Compare qw{ is like };

is(CommandReload(undef, "10_fhempyServer"), U(), "10_fhempyServer loaded");

# device hash without define, define would start fhempy
my $hash = { NAME => "fhempyInstallTest", TYPE => "fhempyServer" };
$defs{fhempyInstallTest} = $hash;

fhempyServer_parseInstallSteps($hash, "Installing uv...OK\nfhempy-install: 2/4 installing Python 3.13\nCreating fhempy");
is(ReadingsVal("fhempyInstallTest", "install", ""), "2/4 installing Python 3.13", "last step of the output");

fhempyServer_parseInstallSteps($hash, " virtual environment...OK\nfhempy-ins");
is(ReadingsVal("fhempyInstallTest", "install", ""), "2/4 installing Python 3.13", "other lines keep the step");

fhempyServer_parseInstallSteps($hash, "tall: 3/4 installing fhempy\n");
is(ReadingsVal("fhempyInstallTest", "install", ""), "3/4 installing fhempy", "step split between two reads");

fhempyServer_parseInstallSteps($hash, "2026-10-12 18:00:00,000 - INFO - x: Attempting install\r\nfhempy-install: failed: installing fhempy failed, see fhempy log\r\n");
is(ReadingsVal("fhempyInstallTest", "install", ""), "failed: installing fhempy failed, see fhempy log", "failure");

fhempyServer_parseInstallSteps($hash, undef);
is(ReadingsVal("fhempyInstallTest", "install", ""), "failed: installing fhempy failed, see fhempy log", "nothing read");

delete $defs{fhempyInstallTest};

done_testing();
exit(0);

1;
