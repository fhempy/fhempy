#!/usr/bin/perl

use File::Basename;
use File::Find;
use POSIX qw(strftime);
use strict;

my $location = "FHEM";

# keep this till 03/2021 (written on 22.12.2020)
print "MOV FHEM/bindings/python/fhempy FHEM/bindings/python/delete_fhempy\n";

print "DIR FHEM/bindings\n";
print "DIR FHEM/bindings/python\n";
print "DIR FHEM/bindings/python/bin\n";

sub find_files {
  my $F = $File::Find::name;
  if ($F =~ /pm$|bin\/fhempy$/ ) {
    my $filename = $F;
    if (index($filename, "__pycache__") != -1) {
      next;
    }
    my @statOutput = stat($filename);
    my $mtime = $statOutput[9];
    my $date = POSIX::strftime("%Y-%m-%d", localtime($mtime));
    my $time = POSIX::strftime("%H:%M:%S", localtime($mtime));
    my $filetime = $date."_".$time;

    my $filesize = $statOutput[7];

    printf("UPD ".$filetime." ".$filesize." ".$filename."\n");
  }
}

find({ wanted => \&find_files, no_chdir=>1}, $location);

