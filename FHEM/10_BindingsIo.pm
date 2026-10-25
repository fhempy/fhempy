# $Id: 10_BindingsIo.pm 18283 2019-01-16 16:58:23Z fhempy $

package main;

use strict;
use warnings;

use Encode;

use DevIo;
use CoProcess;

use JSON;
use Digest::MD5 qw(md5_hex);

# JSON codec in non-utf8 mode, same semantics as JSON::to_json/from_json:
# FHEM works with UTF-8 byte strings, they are passed through unchanged.
# Prefer the XS implementations, JSON::PP needs ~1ms per fhempy message.
our $json_backend;
our $json_codec;
BEGIN {
  foreach my $backend (qw(Cpanel::JSON::XS JSON::XS)) {
    if (eval "require $backend; 1") {
      $json_codec = $backend->new->allow_nonref;
      $json_backend = $backend;
      last;
    }
  }
  if (!defined($json_codec)) {
    $json_codec = JSON->new->allow_nonref;
    $json_backend = JSON->backend;
  }
}

sub BindingsIo_encodeJson($) {
  my ($data) = @_;
  my $json = $json_codec->encode($data);
  # websocket text frames have to be valid UTF-8, invalid bytes from FHEM
  # (e.g. Latin-1 readings) would make fhempy close the connection
  my $octets = eval { Encode::encode("UTF-8", Encode::decode("UTF-8", $json)) };
  return $octets // Encode::encode("UTF-8", $json);
}

sub BindingsIo_decodeJson($) {
  my ($str) = @_;
  # FHEM expects UTF-8 bytes
  $str = Encode::encode("UTF-8", $str) if utf8::is_utf8($str);
  return $json_codec->decode($str);
}

use Time::HiRes qw(time);

our $init_done;
our $modules;
our ($readingFnAttributes, %defs);

my $timeouts = 0;
my $write_deep_recursion = 0;

# A peer that disappears without closing the connection (power loss, cable
# unplugged) is never noticed by TCP alone, so ping fhempy regularly and
# reconnect if nothing was received for a while.
my $keepalive_interval = 30;
my $keepalive_timeout = 90;
# After a function timeout the peer gets this long to answer a ping,
# otherwise the connection is closed and further commands return at once
# instead of freezing FHEM for the full timeout each.
my $alive_check_timeout = 5;
# function timeout while an alive check is running
my $suspect_timeout = 500;

my $BindingsIo_devStateIconVersion = "1.6.0";
# default devStateIcon 1.3.0 of fhempy 2.x, set before the default was remembered
my $BindingsIo_legacyDevStateIconChecksum = "574c39f1d7ab6776eeab79bb53d6e853";

sub BindingsIo_Initialize {
  my ($hash) = @_;

  $hash->{parseParams} = 1;

  $hash->{DefFn}    = \&BindingsIo_Define;
  $hash->{UndefFn}  = \&BindingsIo_Undefine;
  $hash->{GetFn}    = \&BindingsIo_Get;
  $hash->{SetFn}    = \&BindingsIo_Set;
  $hash->{AttrFn}   = \&BindingsIo_Attr;
  $hash->{AttrList} = "autoUpdate:0,1 autoUpdateTime ".$readingFnAttributes;
  $hash->{NotifyFn}   = \&BindingsIo_Notify;

  $hash->{ReadFn}   = \&BindingsIo_Read;
  $hash->{ReadyFn}  = \&BindingsIo_Ready;
  $hash->{WriteFn}  = \&BindingsIo_Write;
  $hash->{FW_detailFn} = \&BindingsIo_detailFn;

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
  # JSON::PP (pure Perl fallback of JSON) needs ~1ms to decode a fhempy message, JSON::XS a few us
  $hash->{JSON_BACKEND} = $json_backend;
  if ($hash->{JSON_BACKEND} =~ m/PP/) {
    Log3 $name, 2, qq[BindingsIo ($name): Neither Cpanel::JSON::XS nor JSON::XS is installed, fhempy messages are decoded much slower. Install it with: sudo apt install libcpanel-json-xs-perl (or libjson-xs-perl)];
  }
  $hash->{messages} = ();
  @{$hash->{messages}{0}} = ();
  $hash->{messages_count} = {};
  # send binary data via websocket
  $hash->{binary} = 1;

  if ($init_done && $localServer == 1) {
    my $foundServer = 0;

    # FHEM only knows modules which existed when it started, load the ones
    # a fresh installation (update without restart) just downloaded
    foreach my $module ($bindingType."Server", $bindingType) {
      CommandReload(undef, "10_$module") if (!$modules{$module} && -r "$attr{global}{modpath}/FHEM/10_$module.pm");
    }

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

  # show the installation progress until fhempy answers the first time
  if ($localServer == 1 && ReadingsVal($name, "version", "") eq "") {
    readingsSingleUpdate($hash, 'state', 'Installing fhempy...', 1);
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

  # the devStateIcon is set once for new devices, users may change or delete it later
  if ($init_done && !defined($hash->{OLDDEF}) && AttrVal($name, q[devStateIcon], q[]) eq q[]) {
    BindingsIo_setDefaultDevStateIcon($hash);
  }

  return undef;
}

sub
BindingsIo_defaultDevStateIcon() {
  my $devstate_cmd = '{
    my $attr_ver = "'.$BindingsIo_devStateIconVersion.'";;
    my $state = ReadingsVal($name, "state", "");;
    if ($state =~ m/^Installing/) {
      my $img = ($state =~ m/failed/) ? "10px-kreis-rot" : "10px-kreis-gelb";;
      return "<div><a>".FW_makeImage($img, "installing")."</a><a> ".$state." </a></div>";;
    }
    my $status_img = "10px-kreis-gruen";;
    my $status_txt = "connected";;
    my $ver = ReadingsVal($name, "version", "-");;
    my $ver_available = ReadingsVal($name, "version_available", $ver);;
    my $update_status = ReadingsVal($name, "update_status", "");;
    my $refresh_img = "refresh";;
    my $refresh_txt = "Update fhempy";;
    my $status_line = "";;
    if ($ver_available ne $ver) {
      $refresh_img = "refresh\@orange";;
      $refresh_txt = "Version ".$ver_available." available for update";;
    }
    if (ReadingsVal($name, "state", "disconnected") eq "disconnected") {
      $status_img = "10px-kreis-rot";;
      $status_txt = "disconnected";;
    }
    my $refresh_icon = FW_makeImage($refresh_img, $refresh_txt);;
    if ($update_status =~ /^(starting|installing)/) {
      $refresh_icon = "<style>\@keyframes fhempy_spin{to{transform:rotate(360deg)}}</style><span style=\"display:inline-block;;animation:fhempy_spin 1.5s linear infinite\">".FW_makeImage("refresh\@orange", $update_status)."</span>";;
      $status_line = "<a> ".$update_status." </a>";;
    }
    my $update_icon = "<a  href=\"/fhem?cmd.dummy=set $name update&XHR=1\" title=\"Start ".$ver_available." update\">".$refresh_icon."</a>";;
    my $restart_icon = "<a  href=\"/fhem?cmd.dummy=set $name restart&XHR=1\" title=\"Restart fhempy\">".FW_makeImage("control_reboot")."</a>";;
    my $modules_button = "";;
    if (InternalVal($name, "localBinding", 0)) {
      $modules_button = "<a href=\"#\" onclick=\"jQuery.getScript(FW_root+&quot;/fhempy/modules.js&quot;,function(){fhempyModules()});;return false;;\" title=\"Install fhempy modules: Matter, Zigbee2MQTT, Tuya, weather, cars...\" style=\"display:inline-block;;margin-left:10px;;padding:2px 12px;;border-radius:12px;;background:#4B8BBE;;text-decoration:none;;white-space:nowrap\"><span style=\"color:#fff;;font-weight:600\">&#43; Install modules</span></a>";;
    }
    "<div><a>".FW_makeImage($status_img, $status_txt)."</a><a> ".$ver." </a>".$update_icon.$restart_icon.$modules_button.$status_line."</div>"
  }';
  $devstate_cmd =~ tr/\n//d;
  return $devstate_cmd;
}

# "Install modules" button on the detail page of the local fhempy, the
# devStateIcon might be changed or deleted by the user
sub
BindingsIo_detailFn($$$$) {
  my ($FW_wname, $d, $room, $pageHash) = @_;
  return undef if ($pageHash || !InternalVal($d, "localBinding", 0));
  return "<div id=\"fhempyModulesButton\" style=\"margin:0 0 10px 0\">"
    ."<a href=\"#\" onclick=\"jQuery.getScript(FW_root+'/fhempy/modules.js',function(){fhempyModules()});return false;\""
    ." title=\"Install fhempy modules: Matter, Zigbee2MQTT, Tuya, weather, cars...\""
    ." style=\"display:inline-block;padding:4px 14px;border-radius:14px;background:#4B8BBE;text-decoration:none;white-space:nowrap\">"
    ."<span style=\"color:#fff;font-weight:600\">&#43; Install modules</span></a></div>";
}

# checksum of a devStateIcon, ignores whitespace and ;; from fhem.cfg
sub
BindingsIo_devStateIconChecksum($) {
  my ($val) = @_;
  $val =~ s/\s+//g;
  $val =~ s/;+/;/g;
  return md5_hex(encode_utf8($val));
}

sub
BindingsIo_setDefaultDevStateIcon($) {
  my ($hash) = @_;
  my $default = BindingsIo_defaultDevStateIcon();
  CommandAttr(undef, "$hash->{NAME} devStateIcon $default");
  # remember the default, so that only an unchanged default gets upgraded
  readingsSingleUpdate($hash, ".devStateIconDefault", BindingsIo_devStateIconChecksum($default), 0);
}

# upgrade the devStateIcon only if it is still the default set by fhempy,
# never touch a devStateIcon the user changed or deleted
sub
BindingsIo_upgradeDevStateIcon($) {
  my ($hash) = @_;
  my $val = AttrVal($hash->{NAME}, q[devStateIcon], q[]);
  return if ($val eq q[]);
  my $checksum = BindingsIo_devStateIconChecksum($val);
  return if ($checksum eq BindingsIo_devStateIconChecksum(BindingsIo_defaultDevStateIcon()));
  return if ($checksum ne ReadingsVal($hash->{NAME}, ".devStateIconDefault", "")
    && $checksum ne $BindingsIo_legacyDevStateIconChecksum);
  BindingsIo_setDefaultDevStateIcon($hash);
}

# Websocket frames (RFC 6455) are handled here instead of with Protocol::WebSocket,
# so fhempy doesn't need an extra Perl package from the system.
sub
BindingsIo_initFrame($) {
  my ($hash) = @_;
  $hash->{".wsBuffer"} = "";
  $hash->{".wsFragments"} = "";
  delete $hash->{".wsFragmentsOpcode"};
}

# returns a masked websocket frame (FHEM is the client) with the given opcode
sub
BindingsIo_wsFrame($$) {
  my ($opcode, $payload) = @_;
  my $len = length($payload);
  my $header = pack("C", 0x80 | $opcode);
  if ($len < 126) {
    $header .= pack("C", 0x80 | $len);
  } elsif ($len < 65536) {
    $header .= pack("Cn", 0x80 | 126, $len);
  } else {
    # 64 bit length as two 32 bit values, works with 32 bit Perl too
    $header .= pack("CNN", 0x80 | 127, int($len / 4294967296), $len % 4294967296);
  }
  my @mask = map { int(rand(256)) } 1..4;
  my $i = 0;
  my $masked = pack("C*", map { $_ ^ $mask[$i++ % 4] } unpack("C*", $payload));
  return $header.pack("C4", @mask).$masked;
}

# returns the next complete frame from the receive buffer as (opcode, payload)
# data frames are returned once all fragments arrived (opcode of the first fragment)
# returns an empty list if more data is needed
sub
BindingsIo_wsNextFrame($) {
  my ($hash) = @_;
  while (1) {
    my $buf = $hash->{".wsBuffer"};
    return () if (length($buf) < 2);
    my ($b0, $b1) = unpack("C2", $buf);
    my $fin = $b0 & 0x80;
    my $opcode = $b0 & 0x0F;
    my $masked = $b1 & 0x80;
    my $len = $b1 & 0x7F;
    my $pos = 2;
    if ($len == 126) {
      return () if (length($buf) < 4);
      $len = unpack("n", substr($buf, 2, 2));
      $pos = 4;
    } elsif ($len == 127) {
      return () if (length($buf) < 10);
      my ($hi, $lo) = unpack("NN", substr($buf, 2, 8));
      $len = $hi * 4294967296 + $lo;
      $pos = 10;
    }
    my @mask;
    if ($masked) {
      return () if (length($buf) < $pos + 4);
      @mask = unpack("C4", substr($buf, $pos, 4));
      $pos += 4;
    }
    return () if (length($buf) < $pos + $len);

    my $payload = substr($buf, $pos, $len);
    $hash->{".wsBuffer"} = substr($buf, $pos + $len);
    if ($masked) {
      my $i = 0;
      $payload = pack("C*", map { $_ ^ $mask[$i++ % 4] } unpack("C*", $payload));
    }

    # control frames (close, ping, pong) can come between fragments
    return ($opcode, $payload) if ($opcode >= 8);

    if ($opcode != 0) {
      $hash->{".wsFragmentsOpcode"} = $opcode;
      $hash->{".wsFragments"} = "";
    }
    $hash->{".wsFragments"} .= $payload;
    next if (!$fin);

    $opcode = delete $hash->{".wsFragmentsOpcode"} // 1;
    $payload = $hash->{".wsFragments"};
    $hash->{".wsFragments"} = "";
    return ($opcode, $payload);
  }
}

# shows the installation step reported by the fhempy server (reading install) as state
sub
BindingsIo_installing($) {
  my ($hash) = @_;
  my $name = $hash->{NAME};

  my @servers = devspec2array("TYPE=".$hash->{BindingType}."Server");
  my $server = IsDevice($servers[0]) ? $servers[0] : undef;

  if (ReadingsVal($name, "version", "") ne "") {
    # fhempy is running, the installation is done
    CommandDeleteReading(undef, "$server install") if (defined($server) && ReadingsVal($server, "install", "") ne "");
    if (ReadingsVal($name, "state", "") =~ m/^Installing/) {
      readingsSingleUpdate($hash, "state", DevIo_IsOpen($hash) ? "opened" : "disconnected", 1);
    }
    return undef;
  }

  my $step = defined($server) ? ReadingsVal($server, "install", "") : "";
  my $state = "Installing fhempy...";
  if ($step =~ m/^failed/) {
    $state = "Installing fhempy $step";
  } elsif ($step ne "") {
    $state = "Installing fhempy: $step";
  }
  readingsSingleUpdate($hash, "state", $state, 1) if (ReadingsVal($name, "state", "") ne $state);
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
BindingsIo_scheduleKeepAlive($) {
  my ($hash) = @_;
  RemoveInternalTimer($hash, 'BindingsIo_keepAlive');
  InternalTimer(gettimeofday()+$keepalive_interval, 'BindingsIo_keepAlive', $hash, 0);
}

sub
BindingsIo_keepAlive($) {
  my ($hash) = @_;

  return if ($hash->{STATE} eq "disconnected" || !DevIo_IsOpen($hash) || !defined($hash->{TCPDev}));

  my $silence = time - ($hash->{".lastReceived"} // $hash->{connecttime} // time);
  if ($silence > $keepalive_timeout) {
    Log3 $hash, 1, "BindingsIo ($hash->{NAME}): no data from ".$hash->{BindingType}." for ".int($silence)."s, closing connection";
    DevIo_Disconnected($hash);
    return;
  }

  # fhempy (websockets) answers with a pong, which updates .lastReceived
  syswrite($hash->{TCPDev}, BindingsIo_wsFrame(0x9, "fhem"));
  BindingsIo_scheduleKeepAlive($hash);
}

sub
BindingsIo_checkAlive($) {
  my ($hash) = @_;

  return if (defined($hash->{".aliveCheckSent"}) || !defined($hash->{TCPDev}));
  $hash->{".aliveCheckSent"} = time;
  RemoveInternalTimer($hash, 'BindingsIo_aliveCheckTimeout');
  # fhempy (websockets) answers with a pong, which updates .lastReceived
  syswrite($hash->{TCPDev}, BindingsIo_wsFrame(0x9, "alive"));
  InternalTimer(gettimeofday()+$alive_check_timeout, 'BindingsIo_aliveCheckTimeout', $hash, 0);
}

sub
BindingsIo_aliveCheckTimeout($) {
  my ($hash) = @_;

  my $sent = delete $hash->{".aliveCheckSent"};
  return if (!defined($sent) || $hash->{STATE} eq "disconnected" || !DevIo_IsOpen($hash));
  if (($hash->{".lastReceived"} // 0) < $sent) {
    Log3 $hash, 1, "BindingsIo ($hash->{NAME}): ".$hash->{BindingType}." didn't answer within ".$alive_check_timeout."s, closing connection";
    DevIo_Disconnected($hash);
  }
}

sub
BindingsIo_setIODevAttr($) {
  my ($hash) = @_;

  my $fhempydev_str = BindingsIo_getIODevList($hash);

  foreach my $fhem_dev (sort keys %main::defs) {
    my $devhash = $main::defs{$fhem_dev};
    if(defined($devhash->{"FHEMPYTYPE"})) {
      my $attr_list = $devhash->{".AttrList"};
      next if (!defined($attr_list));
      # replace an IODev list set before, too
      $attr_list =~ s/(^| )IODev(:\S*)?( |$)/$1IODev:$fhempydev_str$3/;
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
  $hash->{".lastReceived"} = time;
  $hash->{messages} = ();
  @{$hash->{messages}{0}} = ();
  $hash->{messages_count} = {};
  $write_deep_recursion = 0;
  delete $hash->{".aliveCheckSent"};
  delete $hash->{".updateVersionSupported"};
  delete $hash->{".installPeerSupported"};
  RemoveInternalTimer($hash, 'BindingsIo_aliveCheckTimeout');
  $hash->{".waitingIds"} = {};

  BindingsIo_initFrame($hash);
  BindingsIo_scheduleKeepAlive($hash);

  # request the version, fhempy sends it right after the connection setup
  # but HttpUtils drops data received together with the websocket handshake
  BindingsIo_Write($hash, $hash, "version", [], {});

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
      BindingsIo_upgradeDevStateIcon($hash);
      BindingsIo_scheduleAutoUpdate($hash);
      InternalTimer(gettimeofday()+5, "BindingsIo_connectDev", $hash, 0);
    } elsif ($dev->{NAME} eq "global" && $event eq "REREADCFG") {
      BindingsIo_upgradeDevStateIcon($hash);
      BindingsIo_scheduleAutoUpdate($hash);
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
  # commands left over after the 300ms limit must not wait for the next
  # websocket frame, which might only be the next ping
  BindingsIo_scheduleOtherResponses($hash);
}

sub
BindingsIo_Ready($)
{
  my ($hash) = @_;
  my $name = $hash->{NAME};

  # don't check STATE, BindingsIo_installing overwrites "disconnected" with
  # "Installing fhempy..." and the connection would never be retried
  return DevIo_OpenDev($hash, 1, "BindingsIo_doInit", "BindingsIo_Callback") if (!DevIo_IsOpen($hash));
}

sub
BindingsIo_Write($$$$$) {
  my ($hash, $devhash, $function, $a, $h) = @_;
  my $initrun = 0;
  my $waitforresponse = 1;

  if ($function eq "InitDefine") {
    $initrun = 1;
    $function = "Define";
    # sent for all devices after connect, fhempy answers Define before it
    # loads the module and doInit ignores the result, so don't block FHEM
    # with one roundtrip per device
    $waitforresponse = 0;
  } elsif ($function eq "Set") {
    if (@$a[1] eq "?" && defined($devhash) && defined($devhash->{".set_default_response"}) && DevIo_IsOpen($hash)) {
      return $devhash->{".set_default_response"};
    }
  }

  if($function ne "event" && ($hash->{STATE} eq "disconnected" || !DevIo_IsOpen($hash))) {
    if ($init_done == 1 && $hash->{NAME} ne $devhash->{NAME}) {
      readingsSingleUpdate($devhash, "state", $hash->{BindingType}." server offline", 1);

      if (($devhash->{".AttrList"} // ".*") eq ".*" && defined(&fhempy_setBaseAttrList)) {
        fhempy_setBaseAttrList($devhash);
      }
    }
    return undef;
  }

  # FHEM is blocked while waiting, keep this short. fhempy answers Define
  # before it loads the module, so a long timeout isn't needed after connect.
  my $py_timeout = 3000;
  if ($function eq "Define" or $init_done == 0 or $initrun == 1) {
    # defmod runs Undefine of the old instance before fhempy answers
    $py_timeout = 30000;
  }
  if (defined($hash->{".aliveCheckSent"})) {
    # the peer didn't answer the last function, don't freeze FHEM again
    $py_timeout = $suspect_timeout;
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
    "defargsh" => $devhash->{argsh},
    # fhempy stops blocking other devices after this time (ms)
    "timeout" => $py_timeout
  );
  $msg{$bindingType} =  $devhash->{$bindingType};
  # keep this for one year (written on 11.10.2021)
  if ($bindingType eq "FHEMPYTYPE") {
    $msg{PYTHONTYPE} = $devhash->{$bindingType};
  }

  if ($function eq "update") {
    $msg{"msgtype"} = "update";
    $waitforresponse = 0;
  } elsif ($function eq "checkUpdate") {
    $msg{"msgtype"} = "checkUpdate";
    $waitforresponse = 0;
  } elsif ($function eq "restart") {
    $msg{"msgtype"} = "restart";
    $waitforresponse = 0;
  } elsif ($function eq "event") {
    $msg{"msgtype"} = "event";
    $waitforresponse = 0;
  } elsif ($function eq "version") {
    $msg{"msgtype"} = "version";
    $waitforresponse = 0;
  } elsif ($function eq "installPeer") {
    $msg{"msgtype"} = "installPeer";
    $waitforresponse = 0;
  }

  my $utf8msg = BindingsIo_encodeJson(\%msg);
  # installPeer contains the password of the peer
  Log3 $hash, 4, "BindingsIo ($hash->{NAME}): <<< WS: ".($function eq "installPeer" ? "installPeer" : $utf8msg);
  if (length $utf8msg > 0) {
    DevIo_SimpleWrite($hash, $utf8msg, 0);
    if ($waitforresponse == 0) {
      return undef;
    }
  }
  # replies nobody waits for (anymore) are dropped in storeMessage
  $hash->{".waitingIds"}{$waitingForId} = 1;

  $write_deep_recursion = $write_deep_recursion + 1;
  Log3 $hash, 4, "BindingsIo ($hash->{NAME}): $write_deep_recursion - start ".$hash->{BindingType}."Function: ".$devhash->{NAME}." => $function ($waitingForId)";

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
      # args and defargs might contain credentials
      Log3 $hash, 1, "  NAME => $msg{NAME}, function => $msg{function}";
      BindingsIo_checkAlive($hash);
      last;
    }
    
    # don't wait in select longer than the remaining timeout
    my $wait = ($py_timeout - ($t2 - $t1)) / 1000;
    $wait = 1 if ($wait > 1);
    $returnval = BindingsIo_readWebsocketMessage($hash, $devhash, $waitingForId, $wait);
    if ($returnval ne "empty" && $returnval ne "continue") {
      $timeouts = 0;
      last;
    } else {
      $returnval = "";
    }
  }
  delete $hash->{".waitingIds"}{$waitingForId};
  if (defined($hash->{messages}{$devhash->{NAME}})) {
    # a reply which arrived after the timeout
    delete $hash->{messages}{$devhash->{NAME}}{$waitingForId};
  }
  Log3 $hash, 4, "BindingsIo ($hash->{NAME}): $write_deep_recursion - end ".$hash->{BindingType}."Function: ".$devhash->{NAME}." => $function ($waitingForId) - result: ".$returnval;

  if ($returnval eq "" || $returnval eq "continue") {
    $returnval = undef;
  }

  # do not wait for others to finish within function reply
  if ($write_deep_recursion == 1) {
    BindingsIo_scheduleOtherResponses($hash);
  }

  $write_deep_recursion = $write_deep_recursion - 1;
  
  return $returnval;
}

sub
BindingsIo_handleOtherResponses($) {
  my ($hash) = @_;

  delete $hash->{".otherResponsesPending"};
  BindingsIo_checkResponse($hash, undef, 0);

  # check if there are still commands on the queue
  BindingsIo_scheduleOtherResponses($hash);
}

sub
BindingsIo_scheduleOtherResponses($) {
  my ($hash) = @_;

  return if (!defined($hash->{messages}{0}) || @{$hash->{messages}{0}} == 0);
  # one pending timer is enough, don't postpone it
  return if ($hash->{".otherResponsesPending"});
  $hash->{".otherResponsesPending"} = 1;
  InternalTimer(gettimeofday()+0.01, 'BindingsIo_handleOtherResponses', $hash, 0);
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
  my $supported = $hash->{".updateVersionSupported"};
  my $versions = $supported ? ($hash->{helper}{version_options} // "") : "";
  my $list = "update:latest".($versions ne "" ? ",$versions" : "")." checkUpdate:noArg restart:noArg defaultDevStateIcon:noArg";
  # peers are installed from the fhempy running next to FHEM
  my $installPeer = $hash->{localBinding} && $hash->{".installPeerSupported"};
  $list .= " installPeer" if ($installPeer);

  if ($cmd eq 'update') {
    return "Usage: set $hash->{NAME} update [latest|version]" if (@$a > 3 || keys %$h);
    my @args = @$a > 2 && $a->[2] ne "latest" ? ($a->[2]) : ();
    return "The connected fhempy version does not support version selection; update fhempy first."
      if (@args && !$supported);
    # immediate feedback in FHEMWEB, fhempy reports the progress afterwards
    readingsSingleUpdate($hash, "update_status", "starting", 1);
    return BindingsIo_Write($hash, $hash, "update", \@args, {});
  } elsif ($cmd eq 'checkUpdate') {
    return "Usage: set $hash->{NAME} checkUpdate" if (@$a != 2 || keys %$h);
    return "The connected fhempy version does not support checkUpdate; update fhempy first."
      if (!$supported);
    return BindingsIo_Write($hash, $hash, "checkUpdate", [], {});
  } elsif ($cmd eq 'restart') {
    return BindingsIo_Write($hash, $hash, "restart", [], {});
  } elsif ($cmd eq 'defaultDevStateIcon') {
    BindingsIo_setDefaultDevStateIcon($hash);
    return undef;
  } elsif ($cmd eq 'installPeer' && $installPeer) {
    my @args = @$a[2..$#$a];
    return "Usage: set $hash->{NAME} installPeer <host> <user> <password>"
      if (keys %$h || !(@args == 3 || (@args == 2 && $args[0] =~ m/@/)));
    readingsSingleUpdate($hash, "peer_install", "$args[0]: starting", 1);
    return BindingsIo_Write($hash, $hash, "installPeer", \@args, {});
  }

  return "Unknown argument $cmd, choose one of $list";
}

sub
BindingsIo_Attr($$$)
{
  my ($cmd, $name, $attrName, $attrVal) = @_;

  if ($attrName eq "autoUpdateTime" && $cmd eq "set") {
    return "autoUpdateTime must be HH:MM, e.g. 03:00"
      if ($attrVal !~ /^([01]?\d|2[0-3]):[0-5]\d$/);
  }
  if ($attrName eq "autoUpdate" || $attrName eq "autoUpdateTime") {
    # the attribute is set after this function
    InternalTimer(gettimeofday(), "BindingsIo_scheduleAutoUpdate", $defs{$name}, 0) if ($init_done);
  }

  return undef;
}

# next time of the autoUpdate window (attribute autoUpdateTime, default 03:00)
sub BindingsIo_nextAutoUpdateTime {
  my ($hash, $now) = @_;
  my ($hour, $min) = split(/:/, AttrVal($hash->{NAME}, "autoUpdateTime", "03:00"));
  my @lt = localtime($now);
  # on days with a daylight saving change the window might be one hour off
  my $target = $now - ($lt[2] * 3600 + $lt[1] * 60 + $lt[0]) + $hour * 3600 + $min * 60;
  $target += 86400 if ($target <= $now);
  return $target;
}

sub BindingsIo_scheduleAutoUpdate {
  my ($hash) = @_;
  RemoveInternalTimer($hash, "BindingsIo_autoUpdate");
  return if (!AttrVal($hash->{NAME}, "autoUpdate", 0));
  InternalTimer(BindingsIo_nextAutoUpdateTime($hash, time()), "BindingsIo_autoUpdate", $hash, 0);
}

# install a newer fhempy release automatically (attribute autoUpdate)
sub BindingsIo_autoUpdate {
  my ($hash) = @_;
  my $name = $hash->{NAME};

  return if (!AttrVal($name, "autoUpdate", 0));
  # run again tomorrow, fhempy checks for new versions every twelve hours
  BindingsIo_scheduleAutoUpdate($hash);
  return if (!$hash->{".updateVersionSupported"});
  my $available = ReadingsVal($name, "version_available", "");
  return if ($available eq "" || $available eq ReadingsVal($name, "version", ""));
  return if (ReadingsVal($name, "update_status", "") =~ /^(starting|installing)/);
  # every version is tried only once, a failing update must not restart fhempy again and again
  return if (ReadingsVal($name, ".autoUpdateVersion", "") eq $available);
  readingsSingleUpdate($hash, ".autoUpdateVersion", $available, 0);

  Log3 $hash, 3, "BindingsIo ($name): autoUpdate installs fhempy $available";
  readingsSingleUpdate($hash, "update_status", "starting", 1);
  return BindingsIo_Write($hash, $hash, "update", [$available], {});
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
  Log3 $hash, 5, "BindingsIo_storeMessage: ".$response;

  my $json = eval { BindingsIo_decodeJson($response) };
  if ($@ || ref($json) ne "HASH") {
    Log3 $hash, 1, "BindingsIo ($hash->{NAME}): ERROR JSON: " . ($@ || "no JSON object");
    Log3 $hash, 1, "BindingsIo ($hash->{NAME}): received JSON was: " . $response;
    return "error";
  }

  if (defined($json->{id})) {
    # messages from functions, only keep replies BindingsIo_Write waits for
    if (!$hash->{".waitingIds"}{$json->{id}}) {
      Log3 $hash, 5, "BindingsIo ($hash->{NAME}): nobody waits for reply $json->{id}";
      return undef;
    }
    $hash->{messages}{$json->{NAME}}{$json->{id}} = $json;
  } else {
    # messages without hash NAME
    push (@{$hash->{messages}{0}}, $json);
    if (defined($json->{NAME})) {
      $hash->{messages_count}{$json->{NAME}}++;
    }
  }
  return undef;
}

sub BindingsIo_checkResponseByAllNames($) {
  my ($hash) = @_;

  Log3 $hash, 5, "BindingsIo_checkResponseByAllNames size ".@{$hash->{messages}{0}};
  # run maximum 50ms, the rest is handled by a timer after FHEM has served
  # other devices, so a burst of commands doesn't freeze FHEM
  my $start_time = time * 1000;
  while (my $msg = shift @{$hash->{messages}{0}}) {
    if (defined($msg->{NAME}) && defined($hash->{messages_count}{$msg->{NAME}})) {
      $hash->{messages_count}{$msg->{NAME}}--;
      delete $hash->{messages_count}{$msg->{NAME}} if ($hash->{messages_count}{$msg->{NAME}} <= 0);
    }
    BindingsIo_processCommand($hash, $msg);
    if ((time * 1000 - $start_time) > 50) {
      return;
    }
  }
  $hash->{messages_count} = {} if (@{$hash->{messages}{0}} == 0);
  Log3 $hash, 5, "BindingsIo_checkResponseByAllNames size ".@{$hash->{messages}{0}};
}

sub BindingsIo_checkResponseByName($$) {
  my ($hash, $devhash) = @_;
  
  return if (!defined($devhash) || !defined($devhash->{NAME}));
  my $devname = $devhash->{NAME};
  return if (!$hash->{messages_count}{$devname});

  my @temp = ();
  while (my $msg = shift @{$hash->{messages}{0}}) {
    # e.g. version messages have no NAME
    if (defined($msg->{NAME}) && $msg->{NAME} eq $devname) {
      $hash->{messages_count}{$devname}--;
      BindingsIo_processCommand($hash, $msg);
      if ($hash->{messages_count}{$devname} <= 0) {
        delete $hash->{messages_count}{$devname};
        last;
      }
    } else {
      push @temp, $msg;
    }
  }
  if (@temp) {
    unshift @{$hash->{messages}{0}}, @temp;
  }
  $hash->{messages_count} = {} if (@{$hash->{messages}{0}} == 0);
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
    if (exists $json->{version}) {
      $hash->{".updateVersionSupported"} = $json->{update_version_supported} // 0;
      $hash->{".installPeerSupported"} = $json->{install_peer_supported} // 0;
      if ($hash->{".updateVersionSupported"} && (!exists $hash->{helper}{version_options}
          || ReadingsVal($hash->{NAME}, "version", "") ne $json->{version})) {
        $hash->{helper}{version_options} = $json->{version};
      }
    }
    if (exists $json->{version_options}) {
      $hash->{helper}{version_options} = $json->{version_options};
    }
    # a new connection means no update is running (anymore)
    if (exists $json->{version} && ReadingsVal($hash->{NAME}, "update_status", "") =~ /^(starting|installing)/) {
      readingsSingleUpdate($hash, "update_status", "finished, fhempy ".$json->{version}." running", 1);
    }
    # leftover of the release party in fhempy 1.0.x - 2.3.0
    readingsDelete($hash, "release_party") if (exists $hash->{READINGS}{release_party});
    foreach my $key (keys %$json) {
      if ($key eq "msgtype" || $key eq "update_version_supported" || $key eq "version_options") {
        next;
      }
      readingsSingleUpdate($hash, $key, $json->{$key}, 1);
    }
    BindingsIo_installing($hash) if ($hash->{localBinding});
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
    my $utf8msg = BindingsIo_encodeJson(\%res);
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
      $hash->{".lastReceived"} = time;
      # the peer is alive, a pending alive check has been answered
      delete $hash->{".aliveCheckSent"};
      return $buf;
    }
  }
  return undef;
}

sub BindingsIo_readWebsocketMessage {
  my ($hash, $devhash, $waitingForId, $wait) = @_;
  my $ret = "";

  # read message from websocket
  my $response = BindingsIo_SimpleReadWithTimeout($hash, $wait // 1);

  if (defined($response) && $response eq "connectionclosed") {
    # handle connection closed
    Log3 $hash, 5, "BindingsIo ($hash->{NAME}): DevIo_SimpleRead WithTimeout - connection seems to be closed";
    return "Websocket connection closed unexpected";
  }

  if (defined($response) && $response ne "") {
    $hash->{".wsBuffer"} .= $response;
    while (my ($opcode, $r) = BindingsIo_wsNextFrame($hash)) {
      if ($opcode == 0xA) {
        # answer to our keepalive ping, receiving it is all we need
        next;
      } elsif ($opcode == 0x9) {
        syswrite($hash->{TCPDev}, BindingsIo_wsFrame(0xA, $r)) if (defined($hash->{TCPDev}));
      } elsif ($opcode == 0x8) {
        Log3 $hash, 3, "BindingsIo ($hash->{NAME}): ".$hash->{BindingType}." closed the connection";
        syswrite($hash->{TCPDev}, BindingsIo_wsFrame(0x8, substr($r, 0, 2))) if (defined($hash->{TCPDev}));
        DevIo_Disconnected($hash);
        return "Websocket connection closed unexpected";
      } elsif ($r eq "") {
        next;
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

<a id="BindingsIo"></a>
<h3>BindingsIo</h3>
<ul>
  BindingsIo is used to provide language neutral module interface.<br><br>

  <a id="BindingsIo-define"></a>
  <b>Define</b>
  <ul>
  define pybinding BindingsIo fhempy
  </ul>

  <br>

  <a id="BindingsIo-set"></a>
  <b>Set</b>
  <ul>
    <a id="BindingsIo-set-checkUpdate"></a>
    <li><code>checkUpdate</code><br>
      check PyPI (The Python Package Index) now without installing anything.<br>
      Checks also run on connection to FHEM and every twelve hours.<br>
      The reading <code>update_check</code> reports checking, ok or the error;
      its timestamp shows when the last check finished.<br>
      Failed checks preserve the last result.
    </li>

    <br>

    <a id="BindingsIo-set-update"></a>
    <li><code>update [latest|version]</code><br>
      install the newest available package when no version or <code>latest</code>
      is given. The installer resolves this afresh, independently of the last check.<br>
      An explicit version (for example <code>2.1.4</code>) installs only that version,
      with no fallback to a newer one. The installed version is also allowed.<br>
      Older versions are never offered in the dropdown, but can be requested explicitly at
      the command line.<br>
      The reading <code>update_status</code> reports progress and installation errors.
      While the update runs, the update icon of the default devStateIcon spins.<br>
      fhempy restarts after a successful installation.<br>
      fhempy installs the FHEM modules (10_BindingsIo.pm, 10_fhempy.pm, ...) of the new version
      and reloads them in FHEM, FHEM update and shutdown restart are not needed.
      The files are taken from the GitHub release of the version, also when fhempy runs on
      another host. A failure is reported in <code>update_status</code>.
    </li>

    <br>

    <a id="BindingsIo-set-installPeer"></a>
    <li><code>installPeer &lt;host&gt; &lt;user&gt; &lt;password&gt;</code><br>
      install fhempy on another computer (peer) via SSH, e.g. a Raspberry Pi close to your
      Bluetooth devices. Only available on the local fhempy (fhempy_local).<br>
      The peer needs SSH enabled (Raspberry Pi Imager settings) and a user with sudo rights.
      host is the host name (e.g. <code>raspberrypi.local</code>) or the IP address.<br>
      fhempy installs the system packages for the Bluetooth modules, Python, fhempy and a
      systemd service on the peer and creates <code>fhempy_peer_&lt;IP&gt;</code> afterwards.
      The reading <code>peer_install</code> shows the progress.<br>
      The SSH host key of the peer is trusted on first use and checked on later
      installations (.fhempy/peer_installer/known_hosts).<br>
      The password is used for this installation only, it's neither stored nor logged by
      fhempy (FHEM itself logs every command with global verbose 5).
    </li>

    <br>

    <a id="BindingsIo-set-defaultDevStateIcon"></a>
    <li><code>defaultDevStateIcon</code><br>
      reset the devStateIcon attribute to the fhempy default.<br>
      On the local fhempy the default shows the button <b>+ Install modules</b>, it opens a
      window with all fhempy modules. <i>Set up</i> asks for the parameters a module needs
      and defines the device. The same button is shown on the detail page of the local fhempy
      device.<br>
      The default is set once when the device is created and updated together with fhempy
      as long as it is unchanged. A changed or deleted devStateIcon stays as it is.
    </li>

    <br>

    <a id="BindingsIo-set-restart"></a>
    <li><code>restart</code><br>
      restart fhempy
    </li>
  </ul>

  <br>

  <a id="BindingsIo-attr"></a>
  <b>Attributes</b>
  <ul>
    <a id="BindingsIo-attr-autoUpdate"></a>
    <li><code>autoUpdate 0|1</code><br>
      1 installs a newer fhempy release automatically, including the FHEM modules,
      once a day at <code>autoUpdateTime</code>. fhempy checks for updates on connection
      to FHEM and every twelve hours and restarts after the installation.
      Every version is tried only once. Default: 0
    </li>
    <a id="BindingsIo-attr-autoUpdateTime"></a>
    <li><code>autoUpdateTime HH:MM</code><br>
      time of day for <code>autoUpdate</code>, choose a time when a short fhempy restart
      doesn't matter. Default: 03:00
    </li>
  </ul>

  <br>

  The update dropdown offers the installed version
  and newer stable PyPI releases compatible with the running Python version.<br>
  Withdrawn releases are excluded. Refresh the detail page after a check to see
  the new choices. Custom pip/uv indexes still apply to installation.

</ul><br>

=end html
=cut
