
# $Id: 10_PythonBinding.pm 18283 2019-01-16 16:58:23Z dominikkarall $

package main;

use strict;
use warnings;

sub Log($$);
sub Log3($$$);

sub
PythonBinding_Initialize($)
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

  return undef;
}

sub
PythonBinding_getCmd($)
{
  my ($hash) = @_;
  return "FHEM/bindings/python/pythonbinding.py";
}

sub
PythonBinding_Define($$$)
{
  my ($hash, $a, $h) = @_;
  my $name = $hash->{NAME};

  Log3 $hash, 3, "PythonBinding v1.0.0";

  $hash->{logfile} = "./log/PythonBinding-%Y-%m-%d.log";
  $hash->{CoProcess} = {  name => 'PythonBinding',
                          cmdFn => 'PythonBinding_getCmd',
                       };

  chmod(744, PythonBinding_getCmd($hash));
  CoProcess::start($hash);

  readingsSingleUpdate($hash, "state", "active", 1);

  # put in hidden room
  CommandAttr(undef, "$name room hidden");

  return undef;
}

sub
PythonBinding_Notify($$)
{
  my ($hash,$dev) = @_;
   
  return if($dev->{NAME} ne "global");
   
  if( grep(m/^INITIALIZED|REREADCFG$/, @{$dev->{CHANGED}}) ) {
    CoProcess::start($hash);
    return undef;
  }
   
  return undef;
}

sub
PythonBinding_Read($)
{
  my ($hash) = @_;
  my $name = $hash->{NAME};

  CoProcess::readFn($hash);
  return undef;
}

sub
PythonBinding_Undefine($$)
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

sub
PythonBinding_Get($$$)
{
  my ($hash, $a, $h) = @_;

  return undef;
}

sub
PythonBinding_Set($$$)
{
  my ($hash, $a, $h) = @_;

  return undef;
}

sub
PythonBinding_Attr($$$)
{
  my ($cmd, $name, $attrName, $attrVal) = @_;

  return undef;
}

sub
PythonBinding_DelayedShutdownFn($)
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

sub
PythonBinding_Shutdown($)
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
  PythonBinding runs the pythonbinding server.<br><br>

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
