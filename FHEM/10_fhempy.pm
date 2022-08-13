
# $Id: 10_fhempy.pm 18283 2019-01-16 16:58:23Z fhempy $

package main;

use strict;
use warnings;

use JSON;
use Time::HiRes qw(time);

use Color;

sub Log($$);
sub Log3($$$);

sub
fhempy_Initialize($)
{
  my ($hash) = @_;

  $hash->{parseParams} = 1;

  $hash->{DefFn}    = 'fhempy_Define';
  $hash->{UndefFn}  = 'fhempy_Undefine';
  $hash->{GetFn}    = 'fhempy_Get';
  $hash->{SetFn}    = 'fhempy_Set';
  $hash->{AttrFn}   = 'fhempy_Attr';
  $hash->{RenameFn} = 'fhempy_Rename';
  $hash->{AttrList} = 'IODev '.$readingFnAttributes;
  $hash->{FW_detailFn} = "fhempy_detailFn";
  $hash->{FW_deviceOverview} = 1;

  return undef;
}

sub
fhempy_Define($$$)
{
  my ($hash, $a, $h) = @_;
  $hash->{args} = $a;
  $hash->{argsh} = $h;
  $hash->{FHEMPYTYPE} = @$a[2];

  # keep this for 1 year to avoid upgrade issues (written on 11.10.2021)
  $hash->{PYTHONTYPE} = @$a[2];

  setDevAttrList($hash->{NAME}, ".*");
  
  # check if BindingsIo exists
  if ($init_done) {
    my $foundServer = 0;
    foreach my $fhem_dev (sort keys %main::defs) {
      if($main::defs{$fhem_dev}{TYPE} eq 'BindingsIo') {
        $foundServer = 1;
      }
    }
    if ($foundServer == 0) {
      return "Before you use fhempy please define BindingsIo once:\ndefine pyBinding BindingsIo fhempy";
    }
  }

  Log3 $hash, 3, "fhempy v1.0.0 (".$hash->{FHEMPYTYPE}.")";

  AssignIoPort($hash, "fhempy_local");

  return IOWrite($hash, $hash, "Define", $a, $h);
}

sub
fhempy_Undefine($$)
{
  my ($hash, $name) = @_;

  IOWrite($hash, $hash, "Undefine", [], {});

  return undef;
}

sub
fhempy_Get($$$)
{
  my ($hash, $a, $h) = @_;

  return IOWrite($hash, $hash, "Get", $a, $h);
}

sub
fhempy_Set($$$)
{
  my ($hash, $a, $h) = @_;

  return IOWrite($hash, $hash, "Set", $a, $h);
}

sub
fhempy_Attr($$$)
{
  my ($cmd, $name, $attrName, $attrVal) = @_;

  if ($attrName eq "IODev") {
    return IOWrite($defs{$name}, $defs{$name}, "Undefine", [], {});
  }

  return IOWrite($defs{$name}, $defs{$name}, "Attr", [$cmd, $name, $attrName, $attrVal], {});
}

sub
fhempy_Rename($$$)
{
  my ($oldname, $newname) = @_;

  return IOWrite($defs{$oldname}, $defs{$oldname}, "Rename", [$oldname, $newname], {});
}

sub
fhempy_DelayedShutdownFn($)
{
  my ($hash) = @_;

  return IOWrite($hash, $hash, "DelayedShutdown", [], {});
}

sub
fhempy_Shutdown($)
{
  my ($hash) = @_;

  return IOWrite($hash, $hash, "Shutdown", [], {});
}

sub
fhempy_detailFn($$$)
{
  my ($FW_wname, $d, $room, $pageHash) = @_; # pageHash is set for summaryFn.
  my $hash = $defs{$d};
  return IOWrite($hash, $hash, "FW_detailFn", [$FW_wname, $d, $room, $pageHash], {});
}

1;

=pod
=item summary    Interface for Python modules
=item summary_DE Schnittstelle fuer Python Module
=begin html

<a name="fhempy"></a>
<h3>fhempy</h3>
<ul>
  This module provides the interface for python modules.<br><br>
  <a href="https://github.com/fhempy/fhempy#readme">Click here for online README</a>
</ul><br>

=end html
=cut
