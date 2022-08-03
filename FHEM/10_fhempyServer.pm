
# $Id: 10_fhempyServer.pm 18283 2019-01-16 16:58:23Z fhempy $

package main;

use strict;
use warnings;
use version;

use CoProcess;

sub Log($$);
sub Log3($$$);

sub fhempyServer_Initialize($)
{
  my ($hash) = @_;

  $hash->{parseParams} = 1;

  $hash->{DefFn}    = 'fhempyServer_Define';
  $hash->{UndefFn}  = 'fhempyServer_Undefine';
  $hash->{NotifyFn} = "fhempyServer_Notify";
  $hash->{GetFn}    = 'fhempyServer_Get';
  $hash->{SetFn}    = 'fhempyServer_Set';
  $hash->{AttrFn}   = 'fhempyServer_Attr';
  $hash->{ReadFn}   = 'fhempyServer_Read';
  $hash->{AttrList} = 'nrarchive logfile '.$readingFnAttributes;
  $hash->{FW_detailFn} = "fhempyServer_detailFn";
  $hash->{FW_deviceOverview} = 1;

  return undef;
}

sub fhempyServer_detailFn($$$$)
{
  my ($FW_wname, $d, $room, $pageHash) = @_; # pageHash is set for summaryFn.
  my $hash = $defs{$d};
  my $name = $hash->{NAME};

  my $ret;

  my $logfile = AttrVal($name, 'logfile', 'FHEM' );
  if( $logfile && $logfile ne "FHEM" ) {
    my $name = 'fhempy_log';
    $ret .= "<a href=\"$FW_ME?detail=$name\">fhempy Logfile Viewer</a><br>";
  }

  return $ret;
}

sub fhempyServer_getCmd($)
{
  my ($hash) = @_;
  return "FHEM/bindings/python/bin/fhempy --local";
}

sub fhempyServer_checkPythonVersion($)
{
  my ($hash) = @_;
  my $ver = qx(python3 -V|sed "s/.*\ //");
  chomp($ver);
  my $ver_obj = version->declare($ver);
  if ($ver eq "" || $ver_obj < version->declare("3.7.2")) {
    readingsSingleUpdate($hash, "python", "Python 3.7.2 or higher required", 1);
    return 0;
  }
  readingsSingleUpdate($hash, "python", $ver_obj->normal, 1);
  return 1;
}

sub fhempyServer_Define($$$)
{
  my ($hash, $a, $h) = @_;
  my $name = $hash->{NAME};

  Log3 $hash, 3, "fhempyServer v1.0.0";

  $hash->{logfile} = "./log/fhempy-%Y-%m-%d.log";
  $hash->{CoProcess} = {  name => 'fhempy',
                          cmdFn => 'fhempyServer_getCmd',
                       };

  chmod(0744, "FHEM/bindings/python/bin/fhempy");

  if ($init_done && fhempyServer_checkPythonVersion($hash)) {
    CoProcess::start($hash);
  }

  # put in fhempy room
  if (AttrVal($name, "room", "") eq "") {
    CommandAttr(undef, "$name room fhempy") if( !AttrVal($name, 'room', undef ) );
  }
  if (AttrVal($name, "nrarchive", "") eq "") {
    CommandAttr(undef, "$name nrarchive 10") if( !AttrVal($name, 'nrarchive', undef ) );
  }
  # set icon
  if (AttrVal($name, "icon", "") eq "") {
    CommandAttr(undef, "$name icon python");
  }
  # set group
  if (AttrVal($name, "group", "") eq "") {
    CommandAttr(undef, "$name group fhempy");
  }
  # set devStateIcon
  if (AttrVal($name, "devStateIcon", "") eq "") {
    my $devstate_cmd = '{
      my $status_img = "10px-kreis-gruen";;
      my $status_txt = "running";;
      if (substr(ReadingsVal($name, "fhempy", "running"),0,7) ne "running") {
        $status_img = "10px-kreis-rot";;
        $status_txt = "stopped";;
      }
      "<div><a>".FW_makeImage($status_img, $status_txt)."</a><a  href=\"/fhem?cmd.dummy=set $name restart&XHR=1\" title=\"Restart\">".FW_makeImage("audio_repeat")."</a></div>"
      }';
    $devstate_cmd =~ tr/\n//d;
    CommandAttr(undef, "$name devStateIcon $devstate_cmd");
  }

  if( $attr{global}{logdir} ) {
    CommandAttr(undef, "$name logfile %L/fhempy-%Y-%m-%d.log") if( !AttrVal($name, 'logfile', undef ) );
  } else {
    CommandAttr(undef, "$name logfile ./log/fhempy-%Y-%m-%d.log") if( !AttrVal($name, 'logfile', undef ) );
  }

  return undef;
}

sub fhempyServer_Notify($$)
{
  my ($hash,$dev) = @_;
   
  return if($dev->{NAME} ne "global");
   
  if( grep(m/^INITIALIZED|REREADCFG$/, @{$dev->{CHANGED}}) ) {
    if (fhempyServer_checkPythonVersion($hash)) {
      CoProcess::start($hash);
    }
    return undef;
  }
   
  return undef;
}

sub fhempyServer_Read($)
{
  my ($hash) = @_;
  my $name = $hash->{NAME};

  CoProcess::readFn($hash);
  return undef;
}

sub fhempyServer_Undefine($$)
{
  my ($hash, $name) = @_;

  if( $hash->{PID} ) {
    $hash->{undefine} = 1;
    $hash->{undefine} = $hash->{CL} if( $hash->{CL} );
      
    $hash->{reason} = 'delete';
    CoProcess::stop($hash);
      
    return "$name will be deleted after fhempy has stopped or after 5 seconds. whatever comes first.";
  }   
      
  delete $modules{$hash->{TYPE}}{defptr};

  return undef;
}

sub fhempyServer_Get($$$)
{
  my ($hash, $a, $h) = @_;

  return undef;
}

sub fhempyServer_Set($$$)
{
  my ($hash, $a, $h) = @_;

  if (@$a[1] ne "?" && fhempyServer_checkPythonVersion($hash) == 0) {
    return "Python 3.7.2 or higher required (recommended: 3.8)";
  }

  return CoProcess::setCommands($hash, "", @$a[1], @$a);
}

sub fhempyServer_Attr($$$)
{
  my ($cmd, $name, $attrName, $attrVal) = @_;
  my $hash = $defs{$name};

  if( $attrName eq 'logfile' ) {
    if( $cmd eq "set" && $attrVal && $attrVal ne 'FHEM' ) {
      if( exists($defs{"fhempy_log"}) ) {
        fhem( "defmod fhempy_log FileLog $attrVal Logfile" );
        CommandAttr( undef, 'fhempy_log room fhempy' ) if( !AttrVal($name, 'room', undef ) );
      }
      $hash->{logfile} = $attrVal;
    } else {
      fhem( "delete fhempy_log" );
    }

    $attr{$name}{$attrName} = $attrVal;

    if (fhempyServer_checkPythonVersion($hash)) {
      CoProcess::start($hash);
    }
  }

  return undef;
}

sub fhempyServer_DelayedShutdownFn($)
{
  my ($hash) = @_;

  if( $hash->{PID} ) {
    $hash->{shutdown} = 1;
    $hash->{shutdown} = $hash->{CL} if( $hash->{CL} );
  
    $hash->{reason} = 'shutdown';
    CoProcess::stop($hash);
  
    return 1;
  }

  return undef;
}

sub fhempyServer_Shutdown($)
{
  my ($hash) = @_;

  CoProcess::terminate($hash);
  
  delete $modules{$hash->{TYPE}}{defptr};

  return undef;
}

1;

=pod
=item summary    Python Binding to use modules written in python language
=item summary_DE Python Binding zur Nutzung von Python Modulen
=begin html

<a name="fhempyServer"></a>
<h3>fhempyServer</h3>
<ul>
  fhempyServer runs the fhempy server.<br><br>

  <a name="fhempyServer_Set"></a>
  <b>Set</b>
  <ul>
  -
  </ul>

  <a name="fhempyServer_Get"></a>
  <b>Get</b>
  <ul>
  -
  </ul>

  <a name="fhempyServer_Attr"></a>
  <b>Attr</b>
  <ul>
  -
  </ul>
</ul><br>

=end html
=cut
