
# $Id: 10_BindingsIo.pm 18283 2019-01-16 16:58:23Z dominikkarall $

package main;

use strict;
use warnings;

use threads;
use Thread::Queue;

use JSON;
use Time::HiRes qw(time);

sub Log($$);
sub Log3($$$);

sub
BindingsIo_Initialize($)
{
  my ($hash) = @_;

  $hash->{parseParams} = 1;

  $hash->{DefFn}    = 'BindingsIo_Define';
  $hash->{UndefFn}  = 'BindingsIo_Undefine';
  $hash->{GetFn}    = 'BindingsIo_Get';
  $hash->{SetFn}    = 'BindingsIo_Set';
  $hash->{AttrFn}   = 'BindingsIo_Attr';

  $hash->{ReadFn}   = 'BindingsIo_Read';
  $hash->{ReadyFn}  = 'BindingsIo_Ready';
  $hash->{WriteFn}  = 'BindingsIo_Write';

  $hash->{Clients} = "PythonModule:NodeModule";

  return undef;
}

sub
BindingsIo_Define($$$)
{
  my ($hash, $a, $h) = @_;

  Log3 $hash, 3, "BindingsIo v1.0.0";

  my $bindingType = ucfirst(@$a[2]);

  # TODO handover port as parameter to binding server
  # - define of PythonServer needs to handle it
  # - fhem_pythonbridge needs to handle it
  my $port = 15732;
  if ($bindingType eq "Python") {
    $port = 15733;
  }
  $hash->{DeviceName} = "ws:127.0.0.1:".$port;
  $hash->{BindingType} = $bindingType;
  $hash->{ReceiverQueue} = Thread::Queue->new();

  my $foundServer = 0;
  foreach my $fhem_dev (sort keys %main::defs) {
    $foundServer = 1 if($main::defs{$fhem_dev}{TYPE} eq $bindingType."Server");
  }
  if ($foundServer == 0) {
    CommandDefine(undef, $bindingType."binding ".$bindingType."Binding ".$port);
    InternalTimer(gettimeofday()+3, "BindingsIo_connectDev", $hash, 0);
  } else {
    BindingsIo_connectDev($hash);
  }

  return undef;
}

sub
BindingsIo_connectDev($) {
  my ($hash) = @_;
  DevIo_CloseDev($hash) if(DevIo_IsOpen($hash));
  DevIo_OpenDev($hash, 0, "BindingsIo_doInit", "BindingsIo_Callback");
}

sub
BindingsIo_doInit($) {
  my ($hash) = @_;

  # initialize all devices (send Define)
  foreach my $fhem_dev (sort keys %main::defs) {
    my $devhash = $main::defs{$fhem_dev};
    if(defined($devhash->{PYTHONTYPE})) {
      BindingsIo_Write($hash, $devhash, "Define", $devhash->{args}, $devhash->{argsh});
    }
  }

  return undef;
}

sub
BindingsIo_Callback($$) {
  my ($hash, $error) = @_;
  my $name = $hash->{NAME};
  if (defined($error)) {
    Log3 $name, 3, "BindingsIo ($name) - error while connecting: $error"; 
  }
}

sub
BindingsIo_Read($)
{
  my ($hash) = @_;
  my $name = $hash->{NAME};

  BindingsIo_readWebsocketMessage($hash, undef, 1);
}

sub
BindingsIo_Ready($)
{
  my ($hash) = @_;
  my $name = $hash->{NAME};

  return DevIo_OpenDev($hash, 1, "BindingsIo_doInit", "BindingsIo_Callback");
}

sub
BindingsIo_Write($$$$$) {
  my ($hash, $devhash, $function, $a, $h) = @_;

  if($hash->{STATE} eq "disconnected") {
    readingsSingleUpdate($devhash, "state", $hash->{BindingType}."Binding offline", 1);
    return undef;
  }

  Log3 $hash, 3, "start ".$hash->{BindingType}."Function: ".$devhash->{NAME}." => ".$function;

  if ($function eq "Define") {
    $devhash->{args} = $a;
    $devhash->{argsh} = $h;
    # FIXME remove Python wording to be language independent
    $devhash->{PYTHONTYPE} = @$a[2];
  }

  # FIXME remove Python wording to be language independent
  my %msg = (
    "id" => int(rand()*100000000),
    "msgtype" => "function",
    "NAME" => $devhash->{NAME},
    "PYTHONTYPE" => $devhash->{PYTHONTYPE},
    "function" => $function,
    "args" => $a,
    "argsh" => $h,
    "defargs" => $devhash->{args},
    "defargsh" => $devhash->{argsh}
  );
  $devhash->{waitingForId} = $msg{id};
  Log3 $hash, 3, "<<< WS: ".encode_json(\%msg);
  DevIo_SimpleWrite($hash, encode_json(\%msg), 0);

  my $returnval = "";
  my $t1 = time * 1000;
  while (1) {
    my $t2 = time * 1000;
    if (($t2 - $t1) > 1000) {
      # stop loop after ... ms
      Log3 $hash, 1, "ERROR: Timeout while waiting for function to finish ($function)";
      $returnval = "Timeout while waiting for reply from $function";
      last;
    }
    
    $returnval = BindingsIo_readWebsocketMessage($hash, $devhash, 0);
    if ($returnval ne "empty" && $returnval ne "continue") {
      last;
    }
  }
  Log3 $hash, 3, "end ".$hash->{BindingType}."Function: ".$devhash->{NAME}." => ".$function." - result: ".$returnval;

  if ($returnval eq "") {
    $returnval = undef;
  } elsif ($returnval eq "offline") {
    # FIXME remove Python wording to be language independent
    #readingsSingleUpdate($devhash, "state", "PythonServer offline", 1);
  }
  
  return $returnval;
}

sub
BindingsIo_Undefine($$)
{
  my ($hash, $name) = @_;

  RemoveInternalTimer($hash);
  DevIo_CloseDev($hash);

  return undef;
}

sub
BindingsIo_Get($$$)
{
  my ($hash, $a, $h) = @_;

  return undef;
}

sub
BindingsIo_Set($$$)
{
  my ($hash, $a, $h) = @_;

  return undef;
}

sub
BindingsIo_Attr($$$)
{
  my ($cmd, $name, $attrName, $attrVal) = @_;

  return undef;
}

sub
BindingsIo_DelayedShutdownFn($)
{
  my ($hash) = @_;

  DevIo_CloseDev($hash);

  return undef;
}

sub
BindingsIo_Shutdown($)
{
  my ($hash) = @_;

  DevIo_CloseDev($hash);

  return undef;
}

sub BindingsIo_processMessage($$$) {
  my ($hash, $devhash, $response) = @_;

  Log3 $hash, 3, "processMessage: ".$response;
  my $json = eval {decode_json($response)};
  if ($@) {
    Log3 $hash, 3, "JSON error: ".$@;
    return "error";
  }

  my $returnval = "continue";
  if ($json->{msgtype} eq "function") {
    if ($json->{finished} == "1" && defined($devhash) && $json->{id} eq $devhash->{waitingForId}) {
      if ($json->{error}) {
        return $json->{error};
      }
      if ($devhash->{NAME} ne $json->{NAME}) {
        Log3 $hash, 1, "ERROR: Received wrong WS message, waiting for ".$devhash->{NAME}.", but received ".$json->{NAME};
        $hash->{TempReceiverQueue}->enqueue($response);
      } else {
        foreach my $key (keys %$json) {
          next if ($key eq "msgtype" or $key eq "finished" or $key eq "ws" or $key eq "returnval" or $key 
            eq "function" or $key eq "defargs" or $key eq "defargsh" or $key eq "args" or $key eq "argsh");
          $devhash->{$key} = $json->{$key};
        }
        $returnval = $json->{returnval};
      }
    } else {
      Log3 $hash, 1, "ERROR: Received finished without devhash, add to queue";
      $hash->{TempReceiverQueue}->enqueue($response);
    }
  } elsif ($json->{msgtype} eq "command") {
    my $ret = 0;
    my %res;
    $ret = eval $json->{command};
    if ($@) {
      Log3 $hash, 3, "Failed (".$json->{command}."): ".$@;
      %res = (
        awaitId => $json->{awaitId},
        error => 1,
        errorText => $@,
        result => $ret
      );
    } else {
      %res = (
        awaitId => $json->{awaitId},
        error => 0,
        result => $ret
      );
    }
    Log3 $hash, 3, "<<< WS: ".encode_json(\%res);
    DevIo_SimpleWrite($hash, encode_json(\%res), 0);
    return "continue";
  }
  return $returnval;
}

# will be removed from DevIo, therefore it's copied here
sub
BindingsIo_SimpleReadWithTimeout($$)
{
  my ($hash, $timeout) = @_;

  my $rin = "";
  vec($rin, $hash->{FD}, 1) = 1;
  my $nfound = select($rin, undef, undef, $timeout);
  if ($nfound > 0) {
    my $buf = DevIo_DoSimpleRead($hash);
    $buf = DevIo_DecodeWS($hash, $buf) if($hash->{WEBSOCKET});
    return $buf;
  }
  return undef;
}

sub BindingsIo_readWebsocketMessage($$$) {
  my ($hash, $devhash, $socketready) = @_;

  # read message from websocket
  my $returnval = "continue";
  my $response = "";
  my $buffer = $hash->{PARTIAL};
  if (defined($socketready) && $socketready == 1) {
    Log3 $hash, 3, "DevIo_SimpleRead";
    $response = DevIo_SimpleRead($hash);
    Log3 $hash, 3, "DevIo_SimpleRead NoTimeout";
  } else {
    Log3 $hash, 3, "DevIo_SimpleRead";
    $response = BindingsIo_SimpleReadWithTimeout($hash, 0.001);
    Log3 $hash, 3, "DevIo_SimpleRead WithTimeout";
  }
  Log3 $hash, 3, "RAW RECEIVED: ".$response;

  # add message to buffer
  $buffer .= $response if (defined($response));

  # extract messages and add to queue
  while($buffer =~ m/\n/) {
    my $msg;
    ($msg, $buffer) = split("\n", $buffer, 2);
    Log3 $hash, 3, ">>> WS: ".$msg;
    my $ret = BindingsIo_processMessage($hash, $devhash, $msg);
    if ($ret ne "continue") {
      $returnval = $ret;
    }
  }
  $hash->{PARTIAL} = $buffer;
  
  # handle messages on the queue
  $hash->{TempReceiverQueue} = Thread::Queue->new();
  Log3 $hash, 3, "QUEUE: start handling - ".$hash->{ReceiverQueue}->pending();
  while ($response = $hash->{ReceiverQueue}->dequeue_nb()) {
    my $ret = BindingsIo_processMessage($hash, $devhash, $response);
    if ($ret ne "continue") {
      $returnval = $ret;
    }
  }
  Log3 $hash, 3, "QUEUE: finished handling - ".$hash->{ReceiverQueue}->pending();

  # add not matching messages to the queue
  while ($response = $hash->{TempReceiverQueue}->dequeue_nb()) {
    $hash->{ReceiverQueue}->enqueue($response);
  }
  return $returnval;
}

1;

=pod
=item summary    Module for FHEMSync devices
=item summary_DE Modul zur Nutzung von FHEMSync Devices
=begin html

<a name="BindingsIo"></a>
<h3>BindingsIo</h3>
<ul>
  FHEMSync synced devices are using this module.<br><br>

  <a name="BindingsIo_Set"></a>
  <b>Set</b>
  <ul>
  Please see REMOTETYPE module commandref.
  </ul>

  <a name="BindingsIo_Get"></a>
  <b>Get</b>
  <ul>
  Please see REMOTETYPE module commandref.
  </ul>

  <a name="BindingsIo_Attr"></a>
  <b>Attr</b>
  <ul>
  Please set attributes on the remote device.
  </ul>
</ul><br>

=end html
=cut
