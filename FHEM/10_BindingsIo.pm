# $Id: 10_BindingsIo.pm 18283 2019-01-16 16:58:23Z fhempy $

package main;

use strict;
use warnings;

use Encode;

use Protocol::WebSocket::Frame;

use DevIo;
use CoProcess;

use JSON;
use Time::HiRes qw(time);

our $init_done;
our $modules;

my $timeouts = 0;
my $write_deep_recursion = 0;

sub BindingsIo_Initialize {
  my ($hash) = @_;

  $hash->{parseParams} = 1;

  $hash->{DefFn}    = \&BindingsIo_Define;
  $hash->{UndefFn}  = \&BindingsIo_Undefine;
  $hash->{GetFn}    = \&BindingsIo_Get;
  $hash->{SetFn}    = \&BindingsIo_Set;
  $hash->{AttrFn}   = \&BindingsIo_Attr;
  $hash->{AttrList} = $readingFnAttributes;
  $hash->{NotifyFn}   = \&BindingsIo_Notify;

  $hash->{ReadFn}   = \&BindingsIo_Read;
  $hash->{ReadyFn}  = \&BindingsIo_Ready;
  $hash->{WriteFn}  = \&BindingsIo_Write;

  $hash->{Clients} = "PythonModule:fhempy"; # NodeModule

  return ;
}

sub BindingsIo_Define {
  my ( $hash, $a ) = @_;
 
  my $name = $hash->{NAME};
  Log3 $name, 3, q[BindingsIo v1.0.1];

  my $bindingType = $a->[3] // $a->[2];

  $hash->{args} = $a;
  # $hash->{argsh} = $h; // Todo: Delete other code references

  my $port = 0;
  my $localServer = 1;
  
  # Support legacy define via Python instead of fhempy statement
  $bindingType = ($bindingType eq q[Python]) ? q[fhempy] : $bindingType;

  if ($#{$a} == 3 && $bindingType eq q[fhempy])  {
    $hash->{DeviceName} = qq{ws:$a->[2]};
    $localServer = 0;
    $hash->{localBinding} = 0;
  } elsif ($#{$a} == 2 && ($bindingType eq q[fhempy]) )   {
    $hash->{DeviceName} = q[ws:127.0.0.1:15733];
    $hash->{localBinding} = 1;
  } elsif ($#{$a} < 2) {  
    return q[to few parameters given for define];
  } else {  
    return q[unsupported parameters given for define];
  }

  ( undef, $hash->{IP},$hash->{PORT} ) = split ':', $hash->{DeviceName};


  if ( $hash->{IP} !~ m/^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/ )
  {
     my $ip= gethostbyname($hash->{IP});
     if (defined $ip ) { $hash->{IP} =  inet_ntoa($ip) };
     Log3 $name, 3, qq[found IP $hash->{IP}];
  }
  my @BindingsIoDevices = devspec2array(qq[i:TYPE=BindingsIo:FILTER=i:IP=$hash->{IP}:FILTER=i:PORT=$hash->{PORT}]); 
  if ( IsDevice($BindingsIoDevices[1]) )  
  {
    Log3 $name, 5, qq[found hostname $BindingsIoDevices[0] defined];
    return qq[Device $BindingsIoDevices[0] with IP=$hash->{IP} is already defined and using the same port, aborting define];
  }
  
  
  $hash->{devioLoglevel} = 0;
  $hash->{nextOpenDelay} = 10;
  $hash->{BindingType} = $bindingType;
  $hash->{messages} = ();
  @{$hash->{messages}{0}} = ();
  # send binary data via websocket
  $hash->{binary} = 1;

  if ($init_done && $localServer == 1) {
    my $foundServer = 0;
    
    # use devspec2array to find existing fhempy server device
    my @fhempyDevices;
    @fhempyDevices = ::devspec2array(qq[i:TYPE=$bindingType(Binding|Server)]);
    $foundServer = ::IsDevice($fhempyDevices[0]);

    if ($foundServer == 0) 
    {
      CommandDefine(undef, $bindingType.'server_'.$hash->{PORT}.' '.$bindingType.qq[Server $port]);
      InternalTimer(gettimeofday()+3, 'BindingsIo_connectDev', $hash, 0);
    }
  } elsif ($init_done && $localServer == 0)  {
    InternalTimer(gettimeofday()+3, 'BindingsIo_connectDev', $hash, 0);
  }

  if ($init_done == 0 && $localServer == 1) {
    readingsSingleUpdate($hash, 'state', 'Installing fhempy (15min)...', 1);
    $hash->{installing} = 0;
    InternalTimer(gettimeofday()+2, 'BindingsIo_installing', $hash, 0);
  }

  if ($init_done)
  {
    # put in fhempy room
    if (AttrVal($name, q[room], q[]) eq q[]) {
      CommandAttr(undef, qq[$name room fhempy]);
    }
    # set icon
    if (AttrVal($name, q[icon], q[]) eq q[]) {
      CommandAttr(undef, qq[$name icon file_json-ld2]);
    }
    # set group
    if (AttrVal($name, q[group], q[]) eq q[]) {
      CommandAttr(undef, qq[$name group fhempy]);
    }
  }

  # set devStateIcon
  my $devstateicon_val = AttrVal($name, q[devStateIcon], q[]);
  if ($devstateicon_val eq q[] or index($devstateicon_val, "1.1.0") == -1) {
    my $devstate_cmd = '{
      my $attr_ver = "1.1.0";;
      my $status_img = "10px-kreis-gruen";;
      my $status_txt = "connected";;
      my $ver = ReadingsVal($name, "version", "-");;
      my $ver_available = ReadingsVal($name, "version_available", $ver);;
      my $update_icon = "";;
      my $refresh_img = "refresh";;
      my $refresh_txt = "Update fhempy";;
      if ($ver_available ne $ver) {
        $refresh_img = "refresh\@orange";;
        $refresh_txt = "Version ".$ver_available." available for update";;
      }
      if (ReadingsVal($name, "state", "disconnected") eq "disconnected") {
        $status_img = "10px-kreis-rot";;
        $status_txt = "disconnected";;
      }
      $update_icon = "<a  href=\"/fhem?cmd.dummy=set $name update&XHR=1\" title=\"Start ".$ver_available." update\">".FW_makeImage($refresh_img, $refresh_txt)."</a>";;
      my $restart_icon = "<a  href=\"/fhem?cmd.dummy=set $name restart&XHR=1\" title=\"Restart fhempy\">".FW_makeImage("control_reboot")."</a>";;
      "<div><a>".FW_makeImage($status_img, $status_txt)."</a><a> ".$ver." </a>".$update_icon.$restart_icon."</div>"
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
  $hash->{frame}->{max_fragments_amount} = 1000;
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
  $hash->{messages} = ();
  @{$hash->{messages}{0}} = ();
  $write_deep_recursion = 0;

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

  BindingsIo_readWebsocketMessage($hash, undef, 0);
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
  } elsif ($function eq "Set") {
    if (@$a[1] eq "?" && defined($devhash) && defined($devhash->{".set_default_response"}) && DevIo_IsOpen($hash)) {
      return $devhash->{".set_default_response"};
    }
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

  $write_deep_recursion = $write_deep_recursion + 1;
  Log3 $hash, 4, "BindingsIo ($hash->{NAME}): $write_deep_recursion - start ".$hash->{BindingType}."Function: ".$devhash->{NAME}." => $function ($waitingForId)";

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
    }
    
    $returnval = BindingsIo_readWebsocketMessage($hash, $devhash, $waitingForId);
    if ($returnval ne "empty" && $returnval ne "continue") {
      $timeouts = 0;
      last;
    } else {
      $returnval = "";
    }
  }
  Log3 $hash, 4, "BindingsIo ($hash->{NAME}): $write_deep_recursion - end ".$hash->{BindingType}."Function: ".$devhash->{NAME}." => $function ($waitingForId) - result: ".$returnval;

  if ($returnval eq "" || $returnval eq "continue") {
    $returnval = undef;
  }

  # do not wait for others to finish within function reply
  if ($write_deep_recursion == 1) {
    InternalTimer(gettimeofday()+0.1, 'BindingsIo_handleOtherResponses', $hash, 0);
  }

  $write_deep_recursion = $write_deep_recursion - 1;
  
  return $returnval;
}

sub
BindingsIo_handleOtherResponses($) {
  my ($hash) = @_;
  
  BindingsIo_checkResponse($hash, undef, 0);

  # check if there are still commands on the queue
  if (@{$hash->{messages}{0}} > 0) {
    InternalTimer(gettimeofday()+0.1, 'BindingsIo_handleOtherResponses', $hash, 0);
  }
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

  if ($attrName eq "devStateIcon") {
    if (index($attrVal, "1.1.0") == -1) {
      return "devStateIcon updated"
    }
  }

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

sub BindingsIo_storeMessage($$) {
  my ($hash, $response) = @_;
  $response = Encode::encode("utf8", $response);
  Log3 $hash, 5, "BindingsIo_storeMessage: ".$response;
  my $json = eval {from_json($response)};
  if ($@) {
    Log3 $hash, 1, "BindingsIo ($hash->{NAME}): ERROR JSON: ".$@;
    Log3 $hash, 1, "BindingsIo ($hash->{NAME}): received JSON was: ".$response;
    return "error";
  }

  if (defined($json->{id})) {
    # messages from functions
    $hash->{messages}{$json->{NAME}}{$json->{id}} = $json;
  } else {
    # messages without hash NAME
    push (@{$hash->{messages}{0}}, $json);
  }
  return undef;
}

sub BindingsIo_checkResponseByAllNames($) {
  my ($hash) = @_;

  Log3 $hash, 5, "BindingsIo_checkResponseByAllNames size ".@{$hash->{messages}{0}};
  # run maximum 300ms
  my $start_time = time * 1000;
  while (my $msg = shift @{$hash->{messages}{0}}) {
    BindingsIo_processCommand($hash, $msg);
    if ((time * 1000 - $start_time) > 300) {
      return;
    }
  }  
  Log3 $hash, 5, "BindingsIo_checkResponseByAllNames size ".@{$hash->{messages}{0}};
}

sub BindingsIo_checkResponseByName($$) {
  my ($hash, $devhash) = @_;
  
  my @temp = ();
  while (my $msg = shift @{$hash->{messages}{0}}) {
    if ($msg->{NAME} eq $devhash->{NAME}) {
      BindingsIo_processCommand($hash, $msg);
    } else {
      push @temp, $msg;
    }
  }
  @{$hash->{messages}{0}} = @temp;
}

sub BindingsIo_checkResponse($$$) {
  # check if waitingForId is in the hash
  # if it is not in the hash, check if there is a message with the same NAME
  # hash strcuture:
  #   messages
  #     NAME
  #       ID
  # TODO CHECK STRUCTURE AGAIN, KEEP ORDER AS RECEIVED FOR ALL MSGS
  #   messages[0] for all other messages like version, hash_update
  my ($hash, $devhash, $waitingForId) = @_;

  if ($waitingForId != 0) {
    # check if there is a message with this id
    if (defined($hash->{messages}{$devhash->{NAME}}) && defined($hash->{messages}{$devhash->{NAME}}{$waitingForId})) {
      my $json = $hash->{messages}{$devhash->{NAME}}{$waitingForId};
      delete $hash->{messages}{$devhash->{NAME}}{$waitingForId};
      if ($json->{error}) {
        return $json->{error};
      }
      foreach my $key (keys %$json) {
        next if ($key eq "msgtype" or $key eq "finished" or $key eq "ws" or $key eq "returnval" or $key 
          eq "function" or $key eq "defargs" or $key eq "defargsh" or $key eq "args" or $key eq "argsh" or $key eq "id");
        $devhash->{$key} = $json->{$key};
      }
      return $json->{returnval};
    }
    BindingsIo_checkResponseByName($hash, $devhash);
  } else {
    BindingsIo_checkResponseByAllNames($hash);
  }
  
  return "continue";
}

sub BindingsIo_processCommand($$) {
  my ($hash, $json) = @_;

  if (!defined($json)) {
    Log3 $hash, 3, "BindingsIo($hash->{NAME}): ERROR processCommand got empty message to process";
    return;
  }

  if ($json->{msgtype} eq "update_hash") {
    my $devname = $json->{NAME};
    my $devhash = $defs{$devname};
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
  } elsif ($json->{msgtype} eq "set_update") {
    my $devname = $json->{NAME};
    my $devhash = $defs{$devname};
    $devhash->{".set_default_response"} = $json->{set_default_response};
  } elsif ($json->{msgtype} eq "command") {
    my $ret = 0;
    my %res;
    # set proper IODev list for easier handling
    if ($json->{command} =~ /^setDevAttrList/) {
        my $liststr = BindingsIo_getIODevList($hash);
        $json->{command} =~ s/IODev/IODev:$liststr/;
    }
    local $SIG{__WARN__} = sub {
        my $message = shift;
        Log3 $hash, 1, "BindingsIo ($hash->{NAME}): ".$message." => COMMAND: ".$json->{command};
        foreach my $key (keys %$json) {
          Log3 $hash, 1, "BindingsIo ($hash->{NAME}):    ".$key." = ".$json->{$key};
        }
    };
    Log3 $hash, 4, "BindingsIo($hash->{NAME}): processCommand ($json->{awaitId}): ".$json->{command};
    $ret = eval $json->{command};
    if ($@) {
      Log3 $hash, 1, "BindingsIo ($hash->{NAME}): ERROR failed (".$json->{command}."): ".$@;
      %res = (
        awaitId => int($json->{awaitId}),
        error => 1,
        errorText => $@,
        result => $ret
      );
    } else {
      %res = (
        awaitId => int($json->{awaitId}),
        error => 0,
        result => $ret
      );
    }
    my $utf8msg = Encode::encode("utf-8", Encode::decode("utf-8", to_json(\%res)));
    Log3 $hash, 4, "BindingsIo ($hash->{NAME}): <<< WS: ".$utf8msg;
    if (length $utf8msg > 0) {
      DevIo_SimpleWrite($hash, $utf8msg, 0);
    }
  }
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
    delete $hash->{WEBSOCKET};
    my $buf = DevIo_SimpleRead($hash);
    $hash->{WEBSOCKET} = 1;
    if (!defined($buf)) {
      # connection closed
      return "connectionclosed";
    } else {
      return $buf;
    }
  }
  return undef;
}

sub BindingsIo_readWebsocketMessage($$$) {
  my ($hash, $devhash, $waitingForId) = @_;
  my $ret = "";

  # read message from websocket
  my $response = BindingsIo_SimpleReadWithTimeout($hash, 1);

  if (defined($response) && $response eq "connectionclosed") {
    # handle connection closed
    Log3 $hash, 5, "BindingsIo ($hash->{NAME}): DevIo_SimpleRead WithTimeout - connection seems to be closed";
    return "Websocket connection closed unexpected";
  }

  if (defined($response) && $response ne "") {
    $hash->{frame}->append($response);
    while (my $r = $hash->{frame}->next) {
      if ($hash->{frame}->is_ping or $hash->{frame}->is_pong or $hash->{frame}->is_close) {
        DevIo_DecodeWS($hash, $response);
      } else {
        Log3 $hash, 4, "BindingsIo ($hash->{NAME}): >>> WS: ".$r;
        BindingsIo_storeMessage($hash, $r);
      }
    }
  }

  $ret = BindingsIo_checkResponse($hash, $devhash, $waitingForId);
  if ($ret ne "continue") {
    return $ret;
  }
  
  Log3 $hash, 5, "BindingsIo ($hash->{NAME}): Waiting for id ".$waitingForId;
  
  return "continue";
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
