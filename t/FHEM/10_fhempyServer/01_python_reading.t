#!/usr/bin/env perl
use strict;
use warnings;

use Test2::V0;
use Test2::Tools::Compare qw{ is like };
use File::Temp qw(tempdir);
use File::Path qw(make_path);
use Cwd qw(getcwd);

is(CommandReload(undef, "10_fhempyServer"), U(), "10_fhempyServer loaded");

# device hash without define, define would start fhempy
my $hash = { NAME => "fhempyPythonTest", TYPE => "fhempyServer" };
$defs{fhempyPythonTest} = $hash;

my $cwd = getcwd();
my $dir = tempdir(CLEANUP => 1);
chdir($dir);

sub fake_python {
  my ($path, $version) = @_;
  open(my $fh, ">", $path) or die "$path: $!";
  print $fh "#!/bin/sh\necho Python $version\n";
  close($fh);
  chmod(0755, $path);
}

# venv with a Python installed by bin/fhempy with uv (UV_PYTHON_INSTALL_DIR=.fhempy/python)
make_path(".fhempy/python/cpython-3.13.16/bin", ".fhempy/fhempy_venv/bin");
fake_python(".fhempy/python/cpython-3.13.16/bin/python3.13", "3.13.16");
symlink("../../python/cpython-3.13.16/bin/python3.13", ".fhempy/fhempy_venv/bin/python");
is(fhempyServer_checkPythonVersion($hash), 1, "version check ok");
is(ReadingsVal("fhempyPythonTest", "python", ""), "v3.13.16 (installed by fhempy via uv)", "uv Python of the venv");

# venv created with another Python (e.g. a manually installed 3.12)
unlink(".fhempy/fhempy_venv/bin/python");
make_path("other/bin");
fake_python("other/bin/python3.12", "3.12.15");
symlink("$dir/other/bin/python3.12", ".fhempy/fhempy_venv/bin/python");
fhempyServer_checkPythonVersion($hash);
is(ReadingsVal("fhempyPythonTest", "python", ""), "v3.12.15", "Python of the venv without uv note");

# old venv
unlink(".fhempy/fhempy_venv/bin/python");
fake_python("other/bin/python3.11", "3.11.2");
symlink("$dir/other/bin/python3.11", ".fhempy/fhempy_venv/bin/python");
fhempyServer_checkPythonVersion($hash);
like(ReadingsVal("fhempyPythonTest", "python", ""), qr/^v3\.11\.2 \(Python 3\.12 or higher required/, "old venv");

chdir($cwd);
delete $defs{fhempyPythonTest};

done_testing();

exit(0);  # necessary

1;
