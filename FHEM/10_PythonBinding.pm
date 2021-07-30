
# $Id: 10_PythonBinding.pm 18283 2019-01-16 16:58:23Z dominikkarall $

package main;

use strict;
use warnings;

sub Log($$);
sub Log3($$$);

sub PythonBinding_Initialize($)
{
  my ($hash) = @_;

  $hash->{parseParams} = 1;

  $hash->{DefFn}    = 'PythonBinding_Define';
  $hash->{UndefFn}  = 'PythonBinding_Undefine';
  $hash->{NotifyFn} = "PythonBinding_Notify";
  $hash->{GetFn}    = 'PythonBinding_Get';
  $hash->{SetFn}    = 'PythonBinding_Set';
  $hash->{AttrFn}   = 'PythonBinding_Attr';
  $hash->{ReadFn}   = 'PythonBinding_Read';
  $hash->{AttrList} = 'nrarchive logfile '.$readingFnAttributes;
  $hash->{FW_detailFn} = "PythonBinding_detailFn";
  $hash->{FW_deviceOverview} = 1;

  return undef;
}

sub PythonBinding_detailFn($$$$)
{
  my ($FW_wname, $d, $room, $pageHash) = @_; # pageHash is set for summaryFn.
  my $hash = $defs{$d};
  my $name = $hash->{NAME};

  my $ret;

  my $logfile = AttrVal($name, 'logfile', 'FHEM' );
  if( $logfile && $logfile ne "FHEM" ) {
    my $name = 'PythonBindingLog';
    $ret .= "<a href=\"$FW_ME?detail=$name\">fhempy Logfile Viewer</a><br>";
  }

  return $ret;
}

sub PythonBinding_getCmd($)
{
  my ($hash) = @_;
  return "FHEM/bindings/python/bin/fhempy --local";
}

sub PythonBinding_Define($$$)
{
  my ($hash, $a, $h) = @_;
  my $name = $hash->{NAME};

  Log3 $hash, 3, "PythonBinding v1.0.0";

  $hash->{logfile} = "./log/fhempy-%Y-%m-%d.log";
  $hash->{CoProcess} = {  name => 'fhempy',
                          cmdFn => 'PythonBinding_getCmd',
                       };

  chmod(0744, "FHEM/bindings/python/bin/fhempy");

  readingsSingleUpdate($hash, "state", "active", 1);
  if ($init_done) {
    CoProcess::start($hash);
  }

  # put in fhempy room
  CommandAttr(undef, "$name room fhempy");
  CommandAttr(undef, "$name nrarchive 10") if( !AttrVal($name, 'nrarchive', undef ) );

  if( $attr{global}{logdir} ) {
    CommandAttr(undef, "$name logfile %L/fhempy-%Y-%m-%d.log") if( !AttrVal($name, 'logfile', undef ) );
  } else {
    CommandAttr(undef, "$name logfile ./log/fhempy-%Y-%m-%d.log") if( !AttrVal($name, 'logfile', undef ) );
  }

  return undef;
}

sub PythonBinding_Notify($$)
{
  my ($hash,$dev) = @_;
   
  return if($dev->{NAME} ne "global");
   
  if( grep(m/^INITIALIZED|REREADCFG$/, @{$dev->{CHANGED}}) ) {
    CoProcess::start($hash);
    return undef;
  }
   
  return undef;
}

sub PythonBinding_Read($)
{
  my ($hash) = @_;
  my $name = $hash->{NAME};

  CoProcess::readFn($hash);
  return undef;
}

sub PythonBinding_Undefine($$)
{
  my ($hash, $name) = @_;

  if( $hash->{PID} ) {
    $hash->{undefine} = 1;
    $hash->{undefine} = $hash->{CL} if( $hash->{CL} );
      
    $hash->{reason} = 'delete';
    CoProcess::stop($hash);
      
    return "$name will be deleted after pythonbinding.py has stopped or after 5 seconds. whatever comes first.";
  }   
      
  delete $modules{$hash->{TYPE}}{defptr};

  return undef;
}

sub PythonBinding_Get($$$)
{
  my ($hash, $a, $h) = @_;

  return undef;
}

sub PythonBinding_Set($$$)
{
  my ($hash, $a, $h) = @_;

  return CoProcess::setCommands($hash, "", @$a[1], @$a);
}

sub PythonBinding_Attr($$$)
{
  my ($cmd, $name, $attrName, $attrVal) = @_;
  my $hash = $defs{$name};

  if( $attrName eq 'logfile' ) {
    if( $cmd eq "set" && $attrVal && $attrVal ne 'FHEM' ) {
      fhem( "defmod -temporary PythonBindingLog FileLog $attrVal fakelog" );
      CommandAttr( undef, 'PythonBindingLog room fhempy' );
      $hash->{logfile} = $attrVal;
    } else {
      fhem( "delete PythonBindingLog" );
    }

    $attr{$name}{$attrName} = $attrVal;

    CoProcess::start($hash);
  }

  return undef;
}

sub PythonBinding_DelayedShutdownFn($)
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

sub PythonBinding_Shutdown($)
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

<a name="PythonBinding"></a>
<h3>PythonBinding</h3>
<ul>
  PythonBinding runs the fhempy server.<br><br>

  <a name="PythonBinding_Set"></a>
  <b>Set</b>
  <ul>
  -
  </ul>

  <a name="PythonBinding_Get"></a>
  <b>Get</b>
  <ul>
  -
  </ul>

  <a name="PythonBinding_Attr"></a>
  <b>Attr</b>
  <ul>
  -
  </ul>
</ul><br>

=end html
=cut
