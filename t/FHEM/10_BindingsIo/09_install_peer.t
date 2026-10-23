#!/usr/bin/env perl
use strict;
use warnings;
use Test::More;
use File::Basename qw(dirname);
use File::Spec;
use JSON::PP ();

our (%defs, $init_done);
BEGIN {
    *Log3 = sub {} unless defined &Log3;
    # These transport imports aren't needed for the in-memory wire tests.
    for my $module (qw(Protocol/WebSocket/Frame.pm DevIo.pm CoProcess.pm)) {
        $INC{$module} //= 1;
    }
    unless (eval { require JSON; 1 }) {
        $INC{'JSON.pm'} = 1;
        *JSON::new = sub { JSON::PP->new };
        *JSON::backend = sub { 'JSON::PP' };
    }
}

my $module = File::Spec->rel2abs(File::Spec->catfile(
    dirname(__FILE__), '..', '..', '..', 'FHEM', '10_BindingsIo.pm'
));
require $module unless defined &BindingsIo_Set;

{
    no warnings qw(redefine once);
    local $init_done = 1;
    local %defs;
    my @sent;
    local *DevIo_IsOpen = sub { 1 };
    local *DevIo_SimpleWrite = sub { push @sent, JSON::PP::decode_json($_[1]) };
    local *BindingsIo_readWebsocketMessage = sub { die 'Update commands must not wait for a reply' };
    local *ReadingsVal = sub { $defs{$_[0]}{READINGS}{$_[1]}{VAL} // $_[2] };
    local *readingsSingleUpdate = sub { $_[0]{READINGS}{$_[1]}{VAL} = $_[2] };
    local *RemoveInternalTimer = sub {};
    local *BindingsIo_initFrame = sub {};
    local *BindingsIo_scheduleKeepAlive = sub {};
    my @logged;
    local *Log3 = sub { push @logged, $_[2] };
    my $hash = { NAME => 'fhempy_local', STATE => 'connected', BindingType => 'fhempy',
                 TYPE => 'BindingsIo', localBinding => 1, READINGS => {version => {VAL => '2.5.1'}} };
    $defs{fhempy_local} = $hash;

    unlike(BindingsIo_Set($hash, ['fhempy_local', '?'], {}), qr/installPeer/, 'old fhempy offers no installPeer');
    like(BindingsIo_Set($hash, ['fhempy_local', 'installPeer', 'pi.local', 'pi', 'pw'], {}),
         qr/Unknown argument/, 'old fhempy rejects installPeer');

    BindingsIo_processCommand($hash, {msgtype => 'version', version => '2.6.0',
                                     update_version_supported => 1, install_peer_supported => 1});
    like(BindingsIo_Set($hash, ['fhempy_local', '?'], {}), qr/ installPeer( |$)/, 'installPeer offered');
    like(BindingsIo_Set($hash, ['fhempy_local', 'installPeer', 'pi.local'], {}), qr/Usage:/, 'missing user and password');
    is(scalar @sent, 0, 'bad syntax never reaches fhempy');

    ok(!defined BindingsIo_Set($hash, ['fhempy_local', 'installPeer', 'pi.local', 'pi', 'secret'], {}),
       'installPeer returns immediately');
    is($sent[-1]{msgtype}, 'installPeer', 'installPeer has its own wire type');
    is_deeply($sent[-1]{args}, ['pi.local', 'pi', 'secret'], 'host, user and password are sent');
    is(ReadingsVal('fhempy_local', 'peer_install', ''), 'pi.local: starting', 'progress starts at once');
    ok(!grep({ defined && /secret/ } @logged), 'password is not logged');

    ok(!defined BindingsIo_Set($hash, ['fhempy_local', 'installPeer', 'pi@pi.local', 'secret'], {}),
       'user@host form works too');

    my $peer = { NAME => 'fhempy_peer', STATE => 'connected', BindingType => 'fhempy',
                 TYPE => 'BindingsIo', READINGS => {} };
    $defs{fhempy_peer} = $peer;
    BindingsIo_processCommand($peer, {msgtype => 'version', version => '2.6.0', install_peer_supported => 1});
    unlike(BindingsIo_Set($peer, ['fhempy_peer', '?'], {}), qr/installPeer/, 'peers install no peers');

    my $icon = BindingsIo_defaultDevStateIcon();
    $icon =~ s/;;/;/g;
    my $render = sub {
        local *FW_makeImage = sub { "<img $_[0]>" };
        my $name = 'fhempy_local';
        return eval $icon;
    };
    $hash->{READINGS}{state}{VAL} = 'Installing fhempy: 3/4 installing fhempy';
    like($render->(), qr/kreis-gelb.*3\/4 installing fhempy/, 'devStateIcon shows the installation step');
    $hash->{READINGS}{state}{VAL} = 'Installing fhempy failed: no internet';
    like($render->(), qr/kreis-rot.*no internet/, 'devStateIcon shows a failed installation in red');
}

done_testing();
exit(0);
