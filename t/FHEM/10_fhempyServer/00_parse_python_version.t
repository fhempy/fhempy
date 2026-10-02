#!/usr/bin/env perl
use strict;
use warnings;

use Test2::V0;
use Test2::Tools::Compare qw{ is };

is(CommandReload(undef, "10_fhempyServer"), U(), "10_fhempyServer loaded");

is(fhempyServer_parsePythonVersion("Python 3.11.2\n")->normal, "v3.11.2", "regular output");
is(fhempyServer_parsePythonVersion("Python 3.14.3")->normal, "v3.14.3", "windows output without newline");
is(fhempyServer_parsePythonVersion("Python 3.13.0rc1\n")->normal, "v3.13.0", "release candidate");
is(fhempyServer_parsePythonVersion("Python 3.12")->normal, "v3.12.0", "two-part version");
is(fhempyServer_parsePythonVersion(""), U(), "empty output");
is(fhempyServer_parsePythonVersion(undef), U(), "undef output");
is(fhempyServer_parsePythonVersion("'python3' is not recognized as an internal or external command"), U(), "python3 missing on windows");
is(fhempyServer_parsePythonVersion("sh: 1: python3: not found"), U(), "python3 missing on linux");

done_testing();

exit(0);  # necessary

1;
