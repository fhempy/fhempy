
# $Id: 10_PythonModule.pm 18283 2019-01-16 16:58:23Z dominikkarall $

package main;

use strict;
use warnings;

use JSON;
use Time::HiRes qw(time);
use Protocol::WebSocket::Handshake::Client;
use Protocol::WebSocket::Frame;

sub Log($$);
sub Log3($$$);

sub
PythonModule_Initialize($)
{
  my ($hash) = @_;

  $hash->{parseParams} = 1;

  $hash->{DefFn}    = 'PythonModule_Define';
  $hash->{UndefFn}  = 'PythonModule_Undefine';
  $hash->{GetFn}    = 'PythonModule_Get';
  $hash->{SetFn}    = 'PythonModule_Set';
  $hash->{AttrFn}   = 'PythonModule_Attr';

  return undef;
}

sub
PythonModule_Define($$$)
{
  my ($hash, $a, $h) = @_;
  $hash->{PYTHONTYPE} = @$a[2];
  
  # check if PythonServer is running
  my $foundServer = 0;
  foreach my $fhem_dev (sort keys %main::defs) {
    if($main::defs{$fhem_dev}{TYPE} eq 'PythonBinding') {
      $foundServer = 1;
    }
  }
  if ($foundServer == 0) {
    return "Before you use PythonModule please define BindingsIo once:\ndefine pyBinding BindingsIo Python";
  }

  Log3 $hash, 3, "PythonModule v1.0.0 (".$hash->{PYTHONTYPE}.")";

  AssignIoPort($hash, "pyBinding");

  return IOWrite($hash, $hash, "Define", $a, $h);
}

sub
PythonModule_Undefine($$)
{
  my ($hash, $name) = @_;

  IOWrite($hash, $hash, "Undefine", [], {});

  return undef;
}

sub
PythonModule_Get($$$)
{
  my ($hash, $a, $h) = @_;

  return IOWrite($hash, $hash, "Get", $a, $h);
}

sub
PythonModule_Set($$$)
{
  my ($hash, $a, $h) = @_;

  return IOWrite($hash, $hash, "Set", $a, $h);
}

sub
PythonModule_Attr($$$)
{
  my ($cmd, $name, $attrName, $attrVal) = @_;

  return IOWrite($defs{$name}, $defs{$name}, "Attr", [$cmd, $name, $attrName, $attrVal], {});
}

sub
PythonModule_DelayedShutdownFn($)
{
  my ($hash) = @_;

  return IOWrite($hash, $hash, "DelayedShutdown", [], {});
}

sub
PythonModule_Shutdown($)
{
  my ($hash) = @_;

  return IOWrite($hash, $hash, "Shutdown", [], {});
}

1;

=pod
=item summary    Interface for Python modules
=item summary_DE Schnittstelle fuer Python Module
=begin html

<a name="PythonModule"></a>
<h3>PythonModule</h3>
<ul>
  This module provides the interface for python modules.<br><br>

  <a name="PythonModule_Set"></a>
  <b>Set</b>
  <ul>
  Commandref for Python modules not yet supported.
  </ul>

  <a name="PythonModule_Get"></a>
  <b>Get</b>
  <ul>
  Commandref for Python modules not yet supported.
  </ul>

  <a name="PythonModule_Attr"></a>
  <b>Attr</b>
  <ul>
  Commandref for Python modules not yet supported.
  </ul>
</ul><br>

=end html
=cut
