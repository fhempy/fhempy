
# $Id: 10_BindingsIo.pm 18283 2019-01-16 16:58:23Z dominikkarall $

package main;

use strict;
use warnings;

use threads;
use Thread::Queue;
use Encode;

use Protocol::WebSocket::Frame;

use DevIo;
use CoProcess;

use JSON;
use Time::HiRes qw(time);

sub Log($$);
sub Log3($$$);

my $USE_DEVIO_DECODEWS = 0;
my $timeouts = 0;

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
  $hash->{AttrList} = $readingFnAttributes;
  $hash->{NotifyFn}   = 'BindingsIo_Notify';

  $hash->{ReadFn}   = 'BindingsIo_Read';
  $hash->{ReadyFn}  = 'BindingsIo_Ready';
  $hash->{WriteFn}  = 'BindingsIo_Write';

  $hash->{Clients} = "PythonModule"; # NodeModule

  return undef;
}

sub
BindingsIo_Define($$$)
{
  my ($hash, $a, $h) = @_;
  my $name = $hash->{NAME};

  Log3 $hash, 3, "BindingsIo v1.0.0";

  readingsSingleUpdate($hash, "info", "Please wait till connection is established, might take a few minutes", 1);

  my $bindingType = ucfirst(@$a[2]);

  $hash->{args} = $a;
  $hash->{argsh} = $h;

  my $port = 0;
  my $localServer = 1;
  if ($bindingType eq "Python") {
    $hash->{DeviceName} = "ws:127.0.0.1:15733";
    $hash->{IP} = "127.0.0.1";
    $hash->{PORT} = "15733";
    $hash->{localBinding} = 1;
  } else {
    $hash->{DeviceName} = "ws:".@$a[2];
    $hash->{IP} = substr($hash->{DeviceName}, 0, index($hash->{DeviceName}, ":"));
    $hash->{PORT} = substr($hash->{DeviceName}, index($hash->{DeviceName}, ":")+1);
    $bindingType = ucfirst(@$a[3]);
    $localServer = 0;
    $hash->{localBinding} = 0;
  }
  $hash->{nextOpenDelay} = 10;
  $hash->{BindingType} = $bindingType;
  $hash->{ReceiverQueue} = Thread::Queue->new();
  $hash->{frame} = Protocol::WebSocket::Frame->new;

  if ($init_done && $localServer == 1) {
    my $foundServer = 0;
    foreach my $fhem_dev (sort keys %main::defs) {
      $foundServer = 1 if($main::defs{$fhem_dev}{TYPE} eq $bindingType."Binding");
    }
    if ($foundServer == 0) {
      CommandDefine(undef, $bindingType."binding_".$hash->{PORT}." ".$bindingType."Binding ".$port);
      InternalTimer(gettimeofday()+3, "BindingsIo_connectDev", $hash, 0);
    }
  }
  if ($init_done && $localServer == 0) {
    InternalTimer(gettimeofday()+3, "BindingsIo_connectDev", $hash, 0);
  }

  # put in hidden room
  CommandAttr(undef, "$name room hidden");
  #CommandAttr(undef, "$name verbose 5");

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
  my $bindingType = uc($hash->{BindingType})."TYPE";
  foreach my $fhem_dev (sort keys %main::defs) {
    my $devhash = $main::defs{$fhem_dev};
    if(defined($devhash->{$bindingType}) && $devhash->{IODev}{NAME} eq $hash->{NAME}) {
      BindingsIo_Write($hash, $devhash, "InitDefine", $devhash->{args}, $devhash->{argsh});
    }
  }

  return undef;
}

sub
BindingsIo_Notify($)
{
  my ($hash, $dev) = @_;
  return if($dev->{NAME} ne "global");

  return "" if(IsDisabled($hash->{NAME})); # Return without any further action if the module is disabled

  my $devName = $dev->{NAME}; # Device that created the events

  my $events = deviceEvents($dev,1);
  return if( !$events );

  foreach my $event (@{$events}) {
    $event = "" if(!defined($event));

    if ($event eq "INITIALIZED") {
      InternalTimer(gettimeofday()+5, "BindingsIo_connectDev", $hash, 0);
    } elsif ($event eq "UPDATE") {
      BindingsIo_Write($hash, $hash, "update", [], {});
    }
  }

  return undef;
}

sub
BindingsIo_Callback($$) {
  my ($hash, $error) = @_;
  my $name = $hash->{NAME};
  if (defined($error)) {
    Log3 $name, 1, "BindingsIo: ERROR $name - error while connecting: $error"; 
  } else {
    readingsSingleUpdate($hash, "info", "ready", 1);
  }
}

sub
BindingsIo_Read($)
{
  my ($hash) = @_;
  my $name = $hash->{NAME};

  BindingsIo_readWebsocketMessage($hash, undef, 0, 1);
}

sub
BindingsIo_Ready($)
{
  my ($hash) = @_;
  my $name = $hash->{NAME};

  return DevIo_OpenDev($hash, 1, "BindingsIo_doInit", "BindingsIo_Callback") if ( $hash->{STATE} eq "disconnected" );
}

sub
BindingsIo_Write($$$$$) {
  my ($hash, $devhash, $function, $a, $h) = @_;
  my $initrun = 0;
  my $waitforresponse = 1;

  if ($function eq "InitDefine") {
    $initrun = 1;
    $function = "Define";
  }

  if($hash->{STATE} eq "disconnected" || !DevIo_IsOpen($hash)) {
    if ($init_done == 1) {
      readingsSingleUpdate($devhash, "state", $hash->{BindingType}."Binding offline", 1);
    }
    return undef;
  }

  my $waitingForId = int(rand()*100000000);
  Log3 $hash, 4, "BindingsIo: start ".$hash->{BindingType}."Function: ".$devhash->{NAME}." => $function ($waitingForId)";

  my $bindingType = uc($hash->{BindingType})."TYPE";

  my %msg = (
    "id" => $waitingForId,
    "msgtype" => "function",
    "NAME" => $devhash->{NAME},
    "function" => $function,
    "args" => $a,
    "argsh" => $h,
    "defargs" => $devhash->{args},
    "defargsh" => $devhash->{argsh}
  );
  $msg{$bindingType} =  $devhash->{$bindingType};

  if ($function eq "update") {
    $msg{"msgtype"} = "update";
    $waitforresponse = 0;
  }

  my $utf8msg = Encode::encode("utf-8", Encode::decode("utf-8", to_json(\%msg)));
  Log3 $hash, 4, "BindingsIo: <<< WS: ".$utf8msg;
  if (length $utf8msg > 0) {
    DevIo_SimpleWrite($hash, $utf8msg, 0);
    if ($waitforresponse == 0) {
      return undef;
    }
  }

  my $py_timeout = 2500;
  if ($function eq "Define" or $init_done == 0 or $initrun == 1) {
    # wait 10s on Define, this might happen on startup
    $py_timeout = 10000;
  }
  my $returnval = "";
  my $t1 = time * 1000;
  while (1) {
    if (!DevIo_IsOpen($hash)) {
      Log3 $hash, 1, "BindingsIo: ERROR: Connection closed while waiting for function to finish (id: $waitingForId)";
      last;
    }
    my $t2 = time * 1000;
    if (($t2 - $t1) > $py_timeout) {
      $timeouts = $timeouts + 1;
      Log3 $hash, 1, "BindingsIo: ERROR: Timeout while waiting for function to finish (id: $waitingForId)";
      readingsSingleUpdate($devhash, "state", $hash->{BindingType}."Binding timeout", 1);
      $returnval = ""; # was before "Timeout while waiting for reply from $function"
      if ($timeouts > 1) {
        # SimpleRead will close the connection and DevIo reconnect starts
        Log3 $hash, 1, "BindingsIo: ERROR: Too many timeouts, disconnect now and try to reconnect";
        DevIo_Disconnected($hash);
      }
      last;
    }
    
    $returnval = BindingsIo_readWebsocketMessage($hash, $devhash, $waitingForId, 0);
    if ($returnval ne "empty" && $returnval ne "continue") {
      $timeouts = 0;
      last;
    }
  }
  Log3 $hash, 4, "BindingsIo: end ".$hash->{BindingType}."Function: ".$devhash->{NAME}." => $function ($waitingForId) - result: ".$returnval;

  if ($returnval eq "") {
    $returnval = undef;
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
  my $cmd = @$a[1];
  my $list = "update:noArg";

  if ($cmd eq 'update') {
    return BindingsIo_Write($hash, $hash, "update", [], {});
  }

  return "Unknown argument $cmd, choose one of $list";
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

sub BindingsIo_processMessage($$$$) {
  my ($hash, $devhash, $waitingForId, $response) = @_;
  $response = Encode::encode("UTF-8", $response);
  Log3 $hash, 5, "processMessage: ".$response;
  my $json = eval {from_json($response)};
  if ($@) {
    Log3 $hash, 1, "BindingsIo: ERROR JSON: ".$@;
    Log3 $hash, 1, "BindingsIo: received JSON was: ".$response;
    return "error";
  }

  if ($waitingForId != 0) {
    # function running
    # skip messages which aren't part of the function
    if (defined($devhash) && defined($json->{NAME}) && $devhash->{NAME} ne $json->{NAME}) {
      return "nothandled";
    }
  }

  my $returnval = "continue";
  if ($json->{msgtype} eq "function") {
    if ($json->{finished} == 1 && defined($devhash) && $json->{id} eq $waitingForId) {
      if ($json->{error}) {
        return $json->{error};
      }
      if ($devhash->{NAME} ne $json->{NAME}) {
        Log3 $hash, 1, "BindingsIo: ERROR: Received wrong WS message, waiting for ".$devhash->{NAME}.", but received ".$json->{NAME};
        return "nothandled";
      } else {
        foreach my $key (keys %$json) {
          next if ($key eq "msgtype" or $key eq "finished" or $key eq "ws" or $key eq "returnval" or $key 
            eq "function" or $key eq "defargs" or $key eq "defargsh" or $key eq "args" or $key eq "argsh" or $key eq "id");
          $devhash->{$key} = $json->{$key};
        }
        $returnval = $json->{returnval};
      }
    } else {
      Log3 $hash, 4, "BindingsIo: Received message doesn't match, continue waiting...";
      Log3 $hash, 4, "BindingsIo:   received id (".$json->{id}.") = waiting for id (".$waitingForId.")";
      return "nothandled";
    }
  } elsif ($json->{msgtype} eq "update_hash") {
    my $devname = $json->{NAME};
    $devhash = $defs{$devname};
    foreach my $key (keys %$json) {
      next if ($key eq "msgtype" or $key eq "update_hash" or $key eq "ws" or $key eq "returnval" or $key 
        eq "function" or $key eq "defargs" or $key eq "defargsh" or $key eq "args" or $key eq "argsh" or $key eq "id");
      $devhash->{$key} = $json->{$key};
    }
  } elsif ($json->{msgtype} eq "version") {
    readingsSingleUpdate($hash, "version", $json->{version}, 1);
  } elsif ($json->{msgtype} eq "command") {
    my $ret = 0;
    my %res;
    $ret = eval $json->{command};
    if ($@) {
      Log3 $hash, 1, "BindingsIo: ERROR failed (".$json->{command}."): ".$@;
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
    my $utf8msg = Encode::encode("utf-8", Encode::decode("utf-8", to_json(\%res)));
    Log3 $hash, 4, "BindingsIo: <<< WS: ".$utf8msg;
    if (length $utf8msg > 0) {
      DevIo_SimpleWrite($hash, $utf8msg, 0);
    }
    return "continue";
  }
  return $returnval;
}

# will be removed from DevIo, therefore it's copied here
sub BindingsIo_SimpleReadWithTimeout($$) {
  my ($hash, $timeout) = @_;

  if (!defined($hash->{FD})) {
    # connection closed
    return "connectionclosed";
  }
  my $rin = "";
  vec($rin, $hash->{FD}, 1) = 1;
  my $nfound = select($rin, undef, undef, $timeout);
  if ($nfound > 0) {
    my $buf = DevIo_DoSimpleRead($hash);
    if ($buf eq "") {
      # connection closed
      return "connectionclosed";
    } else {
      if ($USE_DEVIO_DECODEWS == 1) {
        my $bufws = DevIo_DecodeWS($hash, $buf) if($hash->{WEBSOCKET});
        return $bufws;
      } else {
        return $buf;
      }
    }
  }
  return undef;
}

sub BindingsIo_readWebsocketMessage($$$$) {
  my ($hash, $devhash, $waitingForId, $socketready) = @_;

  # read message from websocket
  my $returnval = "continue";
  my $response = "";
  if (defined($socketready) && $socketready == 1) {
    Log3 $hash, 5, "BindingsIo: DevIo_SimpleRead";
    if ($USE_DEVIO_DECODEWS == 0) {
      delete $hash->{WEBSOCKET};
    }
    $response = BindingsIo_SimpleReadWithTimeout($hash, 0.00001);
    #$response = DevIo_SimpleRead($hash);
    $hash->{WEBSOCKET} = 1;
    Log3 $hash, 5, "BindingsIo: DevIo_SimpleRead NoTimeout";
  } else {
    Log3 $hash, 5, "BindingsIo: DevIo_SimpleRead";
    $response = BindingsIo_SimpleReadWithTimeout($hash, 0.01);
    Log3 $hash, 5, "BindingsIo: DevIo_SimpleRead WithTimeout";
  }
  if (defined($response) && $response eq "connectionclosed") {
    Log3 $hash, 5, "BindingsIo: DevIo_SimpleRead WithTimeout - connection seems to be closed";
    # connection seems to be closed, call simpleread to disconnect
    # connection will be reopened by ReadyFn
    DevIo_SimpleRead($hash);
    return "Websocket connection closed unexpected";
  }

  if ($USE_DEVIO_DECODEWS == 0) {
    $hash->{frame}->append($response);
    while (my $r = $hash->{frame}->next) {
      Log3 $hash, 4, "BindingsIo: >>> WS: ".$r;
      my $resTemp = {
        "response" => $r,
        "time" => time
      };
      $hash->{ReceiverQueue}->enqueue($resTemp);
    }
  } else {
    if (defined($response) && $response ne "") {
      Log3 $hash, 4, "BindingsIo: >>> WS: ".$response;
      my $resTemp = {
        "response" => $response,
        "time" => time
      };
      $hash->{ReceiverQueue}->enqueue($resTemp);
    }
  }

  # handle messages on the queue
  $hash->{TempReceiverQueue} = Thread::Queue->new();
  Log3 $hash, 5, "BindingsIo: QUEUE: start handling - ".$hash->{ReceiverQueue}->pending();
  while (my $msg = $hash->{ReceiverQueue}->dequeue_nb()) {
    if ((time - $msg->{'time'}) > 10) {
      next;
    }
    $response = $msg->{'response'};
    my $ret = BindingsIo_processMessage($hash, $devhash, $waitingForId, $response);
    if ($ret ne "continue" && $ret ne "nothandled") {
      $returnval = $ret;
    }
    if ($ret eq "nothandled") {
      $hash->{TempReceiverQueue}->enqueue($msg);
    }
  }
  Log3 $hash, 5, "BindingsIo: QUEUE: finished handling - ".$hash->{ReceiverQueue}->pending();

  # add not matching messages to the queue
  while (my $msg = $hash->{TempReceiverQueue}->dequeue_nb()) {
    $hash->{ReceiverQueue}->enqueue($msg);
  }
  return $returnval;
}

1;

=pod
=item summary    BindingsIo provides language neutral module interface
=item summary_DE BindingsIo stellt eine sprachneutrale Modulschnittstelle zur Verfuegung
=begin html

<a name="BindingsIo"></a>
<h3>BindingsIo</h3>
<ul>
  BindingsIo is used to provide language neutral module interface.<br><br>

  <a name="BindingsIo_Define"></a>
  <b>Define</b>
  <ul>
  define pybinding BindingsIo Python
  </ul>

</ul><br>

=end html
=cut
