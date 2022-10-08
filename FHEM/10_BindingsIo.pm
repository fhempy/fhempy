
# $Id: 10_BindingsIo.pm 18283 2019-01-16 16:58:23Z fhempy $

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

  $hash->{Clients} = "PythonModule:fhempy"; # NodeModule

  return undef;
}

sub
BindingsIo_Define($$$)
{
  my ($hash, $a, $h) = @_;
  my $name = $hash->{NAME};

  Log3 $hash, 3, "BindingsIo v1.0.0";

  my $bindingType = @$a[2];

  $hash->{args} = $a;
  $hash->{argsh} = $h;

  my $port = 0;
  my $localServer = 1;
  if ($bindingType eq "Python" or $bindingType eq "fhempy") {
    $hash->{DeviceName} = "ws:127.0.0.1:15733";
    $hash->{IP} = "127.0.0.1";
    $hash->{PORT} = "15733";
    $hash->{localBinding} = 1;
  } else {
    $hash->{DeviceName} = "ws:".@$a[2];
    $hash->{IP} = substr($hash->{DeviceName}, 0, index($hash->{DeviceName}, ":"));
    $hash->{PORT} = substr($hash->{DeviceName}, index($hash->{DeviceName}, ":")+1);
    $bindingType = @$a[3];
    $localServer = 0;
    $hash->{localBinding} = 0;
  }
  $hash->{devioLoglevel} = 0;
  $hash->{nextOpenDelay} = 10;
  $hash->{BindingType} = $bindingType;
  $hash->{ReceiverQueue} = Thread::Queue->new();
  # send binary data via websocket
  $hash->{binary} = 1;

  if ($init_done && $localServer == 1) {
    my $foundServer = 0;
    foreach my $fhem_dev (sort keys %main::defs) {
      $foundServer = 1 if($main::defs{$fhem_dev}{TYPE} eq $bindingType."Binding");
      $foundServer = 1 if($main::defs{$fhem_dev}{TYPE} eq $bindingType."Server");
    }
    if ($foundServer == 0) {
      CommandDefine(undef, $bindingType."server_".$hash->{PORT}." ".$bindingType."Server ".$port);
      InternalTimer(gettimeofday()+3, "BindingsIo_connectDev", $hash, 0);
    }
  }
  if ($init_done && $localServer == 0) {
    InternalTimer(gettimeofday()+3, "BindingsIo_connectDev", $hash, 0);
  }

  if ($init_done == 0 && $localServer == 1) {
    readingsSingleUpdate($hash, "state", "Installing fhempy (15min)...", 1);
    $hash->{installing} = 0;
    InternalTimer(gettimeofday()+2, "BindingsIo_installing", $hash, 0);
  }

  # put in fhempy room
  if (AttrVal($name, "room", "") eq "") {
    CommandAttr(undef, "$name room fhempy");
  }
  # set icon
  if (AttrVal($name, "icon", "") eq "") {
    CommandAttr(undef, "$name icon file_json-ld2");
  }
  # set group
  if (AttrVal($name, "group", "") eq "") {
    CommandAttr(undef, "$name group fhempy");
  }
  # set devStateIcon
  my $devstateicon_val = AttrVal($name, "devStateIcon", "");
  if ($devstateicon_val eq "" or index($devstateicon_val, "ver_available") == -1) {
    my $devstate_cmd = '{
      my $status_img = "10px-kreis-gruen";;
      my $status_txt = "connected";;
      my $ver = ReadingsVal($name, "version", "-");;
      my $ver_available = ReadingsVal($name, "version_available", $ver);;
      my $update_icon = "";;
      if ($ver_available ne $ver) {
        $status_img = "10px-kreis-gelb";;
        $status_txt = "Version ".$ver_available." available for update";;
      }
      if (ReadingsVal($name, "state", "disconnected") eq "disconnected") {
        $status_img = "10px-kreis-rot";;
        $status_txt = "disconnected";;
      }
      $update_icon = "<a  href=\"/fhem?cmd.dummy=set $name update&XHR=1\" title=\"Start ".$ver_available." update\">".FW_makeImage("refresh")."</a>";;
      "<div><a>".FW_makeImage($status_img, $status_txt)."</a><a> ".$ver." </a>".$update_icon."</div>"
    }';
    $devstate_cmd =~ tr/\n//d;
    CommandAttr(undef, "$name devStateIcon $devstate_cmd");
  }

  return undef;
}

sub
BindingsIo_initFrame($) {
  my ($hash) = @_;
  $hash->{frame} = Protocol::WebSocket::Frame->new;
  #$hash->{frame}->{max_fragments_amount} = 1000;
  $hash->{frame}->{max_payload_size} = 0;
}

sub
BindingsIo_installing($) {
  my ($hash) = @_;
  my $state_reading = ReadingsVal($hash->{NAME}, "version", "");
  if ($state_reading ne "") {
    return undef;
  }
  if ($hash->{installing} == 0) {
    readingsSingleUpdate($hash, "state", "Installing fhempy (15min).", 1);
  } elsif ($hash->{installing} == 1) {
    readingsSingleUpdate($hash, "state", "Installing fhempy (15min)..", 1);
  } elsif ($hash->{installing} == 2) {
    readingsSingleUpdate($hash, "state", "Installing fhempy (15min)...", 1);
  }
  $hash->{installing} = ($hash->{installing} + 1) % 3;
  InternalTimer(gettimeofday()+2, "BindingsIo_installing", $hash, 0);
}

sub
BindingsIo_connectDev($) {
  my ($hash) = @_;
  BindingsIo_setIODevAttr($hash);
  DevIo_CloseDev($hash) if(DevIo_IsOpen($hash));
  DevIo_OpenDev($hash, 0, "BindingsIo_doInit", "BindingsIo_Callback");
}

sub
BindingsIo_setIODevAttr($) {
  my ($hash) = @_;

  my $fhempydev_str = BindingsIo_getIODevList($hash);

  foreach my $fhem_dev (sort keys %main::defs) {
    my $devhash = $main::defs{$fhem_dev};
    if(defined($devhash->{"FHEMPYTYPE"})) {
      my $attr_list = $devhash->{".AttrList"};
      $attr_list =~ s/IODev/IODev:$fhempydev_str/;
      setDevAttrList($devhash->{NAME}, $attr_list);
    }
  }
}

sub
BindingsIo_getIODevList($) {
  my @fhempydev_list = ();
  foreach my $fhem_dev (sort keys %main::defs) {
    push(@fhempydev_list, $fhem_dev) if ($main::defs{$fhem_dev}->{TYPE} eq "BindingsIo");
  }
  my $fhempydev_str = join(",", @fhempydev_list);
  return $fhempydev_str;
}

sub
BindingsIo_doInit($) {
  my ($hash) = @_;

  $hash->{connecttime} = time;

  BindingsIo_initFrame($hash);

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

  return "" if(IsDisabled($hash->{NAME})); # Return without any further action if the module is disabled

  my $devName = $dev->{NAME}; # Device that created the events

  my $events = deviceEvents($dev,1);
  return if( !$events );

  foreach my $event (@{$events}) {
    $event = "" if(!defined($event));

    if ($dev->{NAME} eq "global" && $event eq "INITIALIZED") {
      InternalTimer(gettimeofday()+5, "BindingsIo_connectDev", $hash, 0);
    } elsif ($dev->{NAME} eq "global" && $event eq "UPDATE") {
      BindingsIo_Write($hash, $hash, "update", [], {});
      Log3 $hash, 1, "BindingsIo ($hash->{NAME}): ==> FHEMPY UPDATE STARTED...CHECK FHEMPY STATE FOR STATUS <==";
    } else {
      #BindingsIo_Write($hash, $dev, "event", [$event], {});
    }
  }

  return undef;
}

sub
BindingsIo_Callback($$) {
  my ($hash, $error) = @_;
  my $name = $hash->{NAME};
  if (!defined($hash->{prev_error})) {
    $hash->{prev_error} = "";
  }

  if (defined($error) and $hash->{prev_error} ne $error) {
    Log3 $name, 1, "BindingsIo ($hash->{NAME}): ERROR during connection setup: $error";
    $hash->{prev_error} = $error;
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

  if($function ne "event" && ($hash->{STATE} eq "disconnected" || !DevIo_IsOpen($hash))) {
    if ($init_done == 1 && $hash->{NAME} ne $devhash->{NAME}) {
      readingsSingleUpdate($devhash, "state", $hash->{BindingType}." server offline", 1);

      my $attr_list = $devhash->{".AttrList"};
      if ($attr_list eq ".*") {
        my $fhempydev_str = BindingsIo_getIODevList($hash);
        $attr_list = "IODev:$fhempydev_str";
        setDevAttrList($devhash->{NAME}, $attr_list);
      }
    }
    return undef;
  }

  my $waitingForId = int(rand()*100000000);
  Log3 $hash, 4, "BindingsIo ($hash->{NAME}): start ".$hash->{BindingType}."Function: ".$devhash->{NAME}." => $function ($waitingForId)";

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
  # keep this for one year (written on 11.10.2021)
  if ($bindingType eq "FHEMPYTYPE") {
    $msg{PYTHONTYPE} = $devhash->{$bindingType};
  }

  if ($function eq "update") {
    $msg{"msgtype"} = "update";
    $waitforresponse = 0;
  } elsif ($function eq "restart") {
    $msg{"msgtype"} = "restart";
    $waitforresponse = 0;
  } elsif ($function eq "event") {
    $msg{"msgtype"} = "event";
    $waitforresponse = 0;
  }

  my $utf8msg = to_json(\%msg);
  Log3 $hash, 4, "BindingsIo ($hash->{NAME}): <<< WS: ".$utf8msg;
  if (length $utf8msg > 0) {
    DevIo_SimpleWrite($hash, $utf8msg, 0);
    if ($waitforresponse == 0) {
      return undef;
    }
  }

  my $py_timeout = 3000;
  my $cur_time = time;
  if (($cur_time - $hash->{connecttime}) < 120) {
    $py_timeout = 60000;
  }
  if ($function eq "Define" or $init_done == 0 or $initrun == 1) {
    # wait 10s on Define, this might happen on startup
    $py_timeout = 30000;
  }
  my $returnval = "";
  my $t1 = time * 1000;
  while (1) {
    if (not defined(DevIo_IsOpen($hash))) {
      Log3 $hash, 1, "BindingsIo ($hash->{NAME}): WARNING: Connection closed while waiting for function to finish (id: $waitingForId)";
      last;
    }
    my $t2 = time * 1000;
    if (($t2 - $t1) > $py_timeout) {
      $timeouts = $timeouts + 1;
      Log3 $hash, 1, "BindingsIo ($hash->{NAME}): ERROR: Timeout while waiting for function to finish (id: $waitingForId)";
      while (my ($key, $value) = each (%msg))
      {
        Log3 $hash, 1, "  $key =>  $msg{$key}";
      }
      last;
      readingsSingleUpdate($devhash, "state", $hash->{BindingType}." timeout", 1);
      $returnval = ""; # was before "Timeout while waiting for reply from $function"
      #if ($timeouts > 1) {
        # SimpleRead will close the connection and DevIo reconnect starts
      #  Log3 $hash, 1, "BindingsIo ($hash->{NAME}): ERROR: Too many timeouts, disconnect now and try to reconnect";
      #  DevIo_Disconnected($hash);
      #}
      last;
    }
    
    $returnval = BindingsIo_readWebsocketMessage($hash, $devhash, $waitingForId, 0);
    if ($returnval ne "empty" && $returnval ne "continue") {
      $timeouts = 0;
      last;
    } else {
      $returnval = "";
    }
  }
  Log3 $hash, 4, "BindingsIo ($hash->{NAME}): end ".$hash->{BindingType}."Function: ".$devhash->{NAME}." => $function ($waitingForId) - result: ".$returnval;

  if ($returnval eq "" || $returnval eq "continue") {
    $returnval = undef;
  }

  my $cnt = 0;
  while ($hash->{ReceiverQueue}->pending() > 0 && $cnt < 50) {
    BindingsIo_readWebsocketMessage($hash, undef, 0, 1);
    $cnt = $cnt + 1
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
  my $list = "update:noArg restart:noArg";

  if ($cmd eq 'update') {
    return BindingsIo_Write($hash, $hash, "update", [], {});
  } elsif ($cmd eq 'restart') {
    return BindingsIo_Write($hash, $hash, "restart", [], {});
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
  $response = Encode::encode("utf8", $response);
  Log3 $hash, 5, "processMessage: ".$response;
  my $json = eval {from_json($response)};
  if ($@) {
    Log3 $hash, 1, "BindingsIo ($hash->{NAME}): ERROR JSON: ".$@;
    Log3 $hash, 1, "BindingsIo ($hash->{NAME}): received JSON was: ".$response;
    # reset frames
    BindingsIo_initFrame($hash);
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
        Log3 $hash, 1, "BindingsIo ($hash->{NAME}): ERROR: Received wrong WS message, waiting for ".$devhash->{NAME}.", but received ".$json->{NAME};
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
      Log3 $hash, 4, "BindingsIo ($hash->{NAME}): Received message doesn't match, continue waiting...";
      Log3 $hash, 4, "BindingsIo ($hash->{NAME}):   received id (".$json->{id}.") = waiting for id (".$waitingForId.")";
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
    foreach my $key (keys %$json) {
      if ($key eq "msgtype") {
        next;
      }
      readingsSingleUpdate($hash, $key, $json->{$key}, 1);
    }
  } elsif ($json->{msgtype} eq "command") {
    my $ret = 0;
    my %res;
    # set proper IODev list for easier handling
    if ($json->{command} =~ /^setDevAttrList/) {
        my $liststr = BindingsIo_getIODevList($hash);
        $json->{command} =~ s/IODev/IODev:$liststr/;
    }
    $ret = eval $json->{command};
    if ($@) {
      Log3 $hash, 1, "BindingsIo ($hash->{NAME}): ERROR failed (".$json->{command}."): ".$@;
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
    Log3 $hash, 4, "BindingsIo ($hash->{NAME}): <<< WS: ".$utf8msg;
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
        my $op = (ord(substr($buf,0,1)) & 0x0F);
        if ($op == 8) {
          return undef;
        }
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
    Log3 $hash, 5, "BindingsIo ($hash->{NAME}): DevIo_SimpleRead";
    if ($USE_DEVIO_DECODEWS == 0) {
      delete $hash->{WEBSOCKET};
    }
    $response = BindingsIo_SimpleReadWithTimeout($hash, 0.00001);
    #$response = DevIo_SimpleRead($hash);
    $hash->{WEBSOCKET} = 1;
    Log3 $hash, 5, "BindingsIo ($hash->{NAME}): DevIo_SimpleRead NoTimeout";
  } else {
    Log3 $hash, 5, "BindingsIo ($hash->{NAME}): DevIo_SimpleRead";
    $response = BindingsIo_SimpleReadWithTimeout($hash, 0.01);
    Log3 $hash, 5, "BindingsIo ($hash->{NAME}): DevIo_SimpleRead WithTimeout";
  }
  if (defined($response) && $response eq "connectionclosed") {
    Log3 $hash, 5, "BindingsIo ($hash->{NAME}): DevIo_SimpleRead WithTimeout - connection seems to be closed";
    # connection seems to be closed, call simpleread to disconnect
    # connection will be reopened by ReadyFn
    DevIo_SimpleRead($hash);
    return "Websocket connection closed unexpected";
  }

  if ($USE_DEVIO_DECODEWS == 0) {
    $hash->{frame}->append($response);
    while (my $r = $hash->{frame}->next) {
      Log3 $hash, 4, "BindingsIo ($hash->{NAME}): >>> WS: ".$r;
      my $resTemp = {
        "response" => $r,
        "time" => time
      };
      $hash->{ReceiverQueue}->enqueue($resTemp);
    }
  } else {
    if (defined($response) && $response ne "") {
      Log3 $hash, 4, "BindingsIo ($hash->{NAME}): >>> WS: ".$response;
      my $resTemp = {
        "response" => $response,
        "time" => time
      };
      $hash->{ReceiverQueue}->enqueue($resTemp);
    }
  }

  # handle messages on the queue
  $hash->{TempReceiverQueue} = Thread::Queue->new();
  Log3 $hash, 5, "BindingsIo ($hash->{NAME}): QUEUE: start handling - ".$hash->{ReceiverQueue}->pending();
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
  
  # add not matching messages to the queue
  while (my $msg = $hash->{TempReceiverQueue}->dequeue_nb()) {
    $hash->{ReceiverQueue}->enqueue($msg);
  }

  Log3 $hash, 5, "BindingsIo ($hash->{NAME}): QUEUE: finished handling - ".$hash->{ReceiverQueue}->pending();

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
  define pybinding BindingsIo fhempy
  </ul>

</ul><br>

=end html
=cut
