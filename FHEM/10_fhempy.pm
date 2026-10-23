
# $Id: 10_fhempy.pm 18283 2019-01-16 16:58:23Z fhempy $

package main;

use strict;
use warnings;

use JSON;
use Time::HiRes qw(time);

use Color;

our $init_done;


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
  $hash->{NotifyFn} = 'fhempy_Notify';
  $hash->{AttrList} = 'IODev disable:0,1 '.$readingFnAttributes;
  $hash->{FW_detailFn} = "fhempy_detailFn";
  $hash->{FW_deviceOverview} = 1;

  return undef;
}

sub
fhempy_Define($$$)
{
  my ($hash, $a, $h) = @_;
  # FHEM restores DEF after a rejected modify. Keep its matching metadata too.
  my @definition_keys = qw(
    args argsh FHEMPYTYPE PYTHONTYPE .AttrList IODev NOTIFYDEV disableNotifyFn
  );
  my %previous = map { exists($hash->{$_}) ? ($_ => $hash->{$_}) : () }
    @definition_keys;
  $hash->{args} = $a;
  $hash->{argsh} = $h;
  $hash->{FHEMPYTYPE} = @$a[2];

  # keep this for 1 year to avoid upgrade issues (written on 11.10.2021)
  $hash->{PYTHONTYPE} = @$a[2];

  setDevAttrList($hash->{NAME}, ".*");
  # only modules which call fhempy_setEventDevices get events
  setDisableNotifyFn($hash, 1);
  
  # check if BindingsIo exists
  if ($init_done) {
    my $foundServer = 0;
    my @fhempyDevices = ::devspec2array(qq[i:TYPE=BindingsIo]);
    $foundServer = ::IsDevice($fhempyDevices[0]);

    if ($foundServer == 0) {
      return "Before you use fhempy please define BindingsIo once:\ndefine fhempy_local BindingsIo fhempy";
    }
  }

  Log3 $hash, 3, "fhempy v1.0.0 (".$hash->{FHEMPYTYPE}.": ".$hash->{NAME}.")";

  AssignIoPort($hash, fhempy_defaultIODev($hash));

  my $ret = IOWrite($hash, $hash, "Define", $a, $h);
  if (defined($ret) && $ret ne "") {
    # Waiting for the reply may have rebuilt FHEM's notification cache.
    setDisableNotifyFn($hash, $previous{disableNotifyFn} // 0);
    for my $key (@definition_keys) {
      if (exists($previous{$key})) {
        $hash->{$key} = $previous{$key};
      } else {
        delete $hash->{$key};
      }
    }
  }
  return $ret;
}

# IODev for a new device: the attribute, the IODev a modified device already
# uses or the BindingsIo of the fhempy server running on this FHEM host.
# Without any of them AssignIoPort picks the last defined BindingsIo.
sub
fhempy_defaultIODev($)
{
  my ($hash) = @_;
  my $name = $hash->{NAME};

  my $attrIo = AttrVal($name, "IODev", "");
  return $attrIo if ($attrIo ne "");

  my $currentIo = ref($hash->{IODev}) eq "HASH" ? $hash->{IODev}{NAME} : undef;
  return $currentIo if (defined($currentIo) && defined($defs{$currentIo}));

  my @local = grep { $defs{$_}{TYPE} eq "BindingsIo" && $defs{$_}{localBinding} }
    sort keys %defs;
  return "fhempy_local" if (grep { $_ eq "fhempy_local" } @local);
  return $local[0] if (@local);
  return "fhempy_local" if (defined($defs{fhempy_local}));
  return undef;
}

sub
fhempy_IODevList()
{
  return join(",", sort grep { $defs{$_}{TYPE} eq "BindingsIo" } keys %defs);
}

# Attributes offered as long as fhempy didn't send the module's attributes,
# e.g. the server is offline or the module failed to load
sub
fhempy_setBaseAttrList($)
{
  my ($hash) = @_;
  setDevAttrList($hash->{NAME}, "IODev:".fhempy_IODevList()." disable:0,1 ".$readingFnAttributes);
}

# after attr IODev: start the device on the new fhempy server
sub
fhempy_changedIODev($)
{
  my ($hash) = @_;
  my $name = $hash->{NAME};
  return if (!defined($defs{$name}) || $defs{$name} != $hash);

  if (AttrVal($name, "IODev", "") eq "") {
    delete $hash->{IODev};
    AssignIoPort($hash, fhempy_defaultIODev($hash));
  }
  return if (!defined($hash->{IODev}) || IsDisabled($name));
  IOWrite($hash, $hash, "Define", $hash->{args}, $hash->{argsh});
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
    my $hash = $defs{$name};
    # devices are defined on their fhempy server after it connected
    return undef if (!$init_done);
    if ($cmd eq "set" && (!defined($defs{$attrVal}) || $defs{$attrVal}{TYPE} ne "BindingsIo")) {
      return "$attrVal is not a BindingsIo device, use one of: ".fhempy_IODevList();
    }
    my $ret = IOWrite($hash, $hash, "Undefine", [], {});
    return $ret if (defined($ret) && $ret ne "");
    InternalTimer(gettimeofday(), "fhempy_changedIODev", $hash, 0);
    return undef;
  }

  return IOWrite($defs{$name}, $defs{$name}, "Attr", [$cmd, $name, $attrName, $attrVal], {});
}

sub
fhempy_Rename($$$)
{
  my ($oldname, $newname) = @_;

  return IOWrite($defs{$oldname}, $defs{$oldname}, "Rename", [$oldname, $newname], {});
}

# Called by Python modules (e.g. matter_bridge) to receive the events of
# other FHEM devices. $devspec is a comma separated list of device names,
# an empty $devspec stops the events.
sub
fhempy_setEventDevices($$)
{
  my ($name, $devspec) = @_;
  my $hash = $defs{$name};
  return "Unknown device $name" if (!defined($hash));

  if (!defined($devspec) || $devspec eq "") {
    setDisableNotifyFn($hash, 1);
    return undef;
  }
  setDisableNotifyFn($hash, 0);
  setNotifyDev($hash, $devspec);
  return undef;
}

sub
fhempy_Notify($$)
{
  my ($hash, $dev) = @_;

  return undef if (IsDisabled($hash->{NAME}));
  my $iohash = $hash->{IODev};
  return undef if (!defined($iohash) || !DevIo_IsOpen($iohash));

  my $events = deviceEvents($dev, 1);
  return undef if (!$events);

  foreach my $event (@{$events}) {
    next if (!defined($event));
    # NAME of the message is the device which created the event
    IOWrite($hash, $dev, "event", [$event], {});
  }

  return undef;
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
  # without this the attribute list only shows .*
  fhempy_setBaseAttrList($hash) if ($init_done && ($hash->{".AttrList"} // ".*") eq ".*");
  return IOWrite($hash, $hash, "FW_detailFn", [$FW_wname, $d, $room, $pageHash], {});
}

# Notification to the phones of the fhempy module push, for notify/DOIF:
# {fhempy_push("Washing machine is done")}, optional title and phone names
sub
fhempy_push($;$$)
{
  my ($text, $title, $to) = @_;
  my ($dev) = grep { ($defs{$_}{TYPE} // '') eq 'fhempy' &&
                     ($defs{$_}{FHEMPYTYPE} // '') eq 'push' } sort keys %defs;
  if (!$dev) {
    my $msg = "fhempy_push: create the device first: define push fhempy push";
    Log3 undef, 2, $msg;
    return $msg;
  }
  my $options = '';
  foreach my $opt (['title', $title], ['to', $to]) {
    my ($key, $value) = @$opt;
    next if (!defined($value) || $value eq '');
    $value =~ s/"/'/g;
    $value =~ s/[\r\n]+/ /g;
    $options .= " $key=\"$value\"";
  }
  $text //= '';
  $text =~ s/[\r\n]+/ /g;
  return CommandSet(undef, "$dev message$options $text");
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
