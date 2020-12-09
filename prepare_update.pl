#!/usr/bin/perl

use File::Basename;
use File::Find;
use POSIX qw(strftime);
use strict;

my $location = "FHEM";

my @dirs = split(/\n/,`find $location -type d`);
foreach(@dirs) {
  my $dir = substr($_,5);
  if (substr($dir,0,4) eq ".git") {
    next;
  }
  if ($dir eq "") {
    next;
  }
  if (substr($dir,-11) eq "__pycache__") {
    next;
  }
  if (substr($dir,-8) eq "egg-info") {
    next;
  }
  print "DIR $location/$dir\n";
}

sub find_files {
  my $F = $File::Find::name;
  if ($F =~ /pm$\|json$\|\.py|bin\/fhempy$/ ) {
    my $filename = $F;
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

