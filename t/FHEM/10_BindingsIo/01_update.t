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
    local *Log3 = sub {};
    local *DevIo_IsOpen = sub { 1 };
    local *DevIo_SimpleWrite = sub { push @sent, JSON::PP::decode_json($_[1]) };
    local *BindingsIo_readWebsocketMessage = sub { die 'Update commands must not wait for a reply' };
    local *ReadingsVal = sub { $defs{$_[0]}{READINGS}{$_[1]}{VAL} // $_[2] };
    local *readingsSingleUpdate = sub { $_[0]{READINGS}{$_[1]}{VAL} = $_[2] };
    local *RemoveInternalTimer = sub {};
    local *BindingsIo_initFrame = sub {};
    local *BindingsIo_scheduleKeepAlive = sub {};
    my $hash = { NAME => 'binding', STATE => 'connected', BindingType => 'fhempy',
                 TYPE => 'BindingsIo', READINGS => {version => {VAL => '2.1.3'}} };
    $defs{binding} = $hash;

    like(BindingsIo_Set($hash, ['binding', 'update', '2.1.4'], {}),
         qr/does not support version selection/, 'old backend cannot silently install latest');
    is(scalar @sent, 0, 'rejected pin sends no command');
    like(BindingsIo_Set($hash, ['binding', 'checkUpdate'], {}),
         qr/does not support checkUpdate/, 'old backend gets an actionable error');
    BindingsIo_Set($hash, ['binding', 'update'], {});
    is_deeply($sent[-1]{args}, [], 'default update remains compatible with old backend');

    BindingsIo_processCommand($hash, {msgtype => 'version', version => '2.1.3',
                                     update_version_supported => 1});
    like(BindingsIo_Set($hash, ['binding', '?'], {}), qr/update:latest,2\.1\.3 /,
         'startup offers installed version before any successful check');
    BindingsIo_processCommand($hash, {msgtype => 'version', version => '2.1.4',
                                     update_version_supported => 1});
    is($hash->{helper}{version_options}, '2.1.4', 'version change discards old choices');
    ok(!exists $hash->{READINGS}{version_options}, 'installed choice creates no reading');
    ok(!exists $hash->{READINGS}{update_version_supported}, 'capability is internal');
    BindingsIo_processCommand($hash, {msgtype => 'version', version_available => '2.1.10',
                                     version_options => '2.1.10,2.1.9,2.1.4', update_check => 'ok'});
    ok(!exists $hash->{READINGS}{version_options}, 'catalog creates no reading');
    is(ReadingsVal('binding', 'version_available', ''), '2.1.10', 'available version remains a reading');
    like(BindingsIo_Set($hash, ['binding', '?'], {}),
         qr/update:latest,2\.1\.10,2\.1\.9,2\.1\.4 checkUpdate:noArg restart:noArg/,
         'set list uses backend choices in supplied order');
    BindingsIo_processCommand($hash, {msgtype => 'version', version => '2.1.4',
                                     update_version_supported => 1});
    is($hash->{helper}{version_options}, '2.1.10,2.1.9,2.1.4',
       'repeated version reply preserves fresh choices');

    for my $args ([], ['latest'], ['2.1.4'], ['2.1.10']) {
        ok(!defined BindingsIo_Set($hash, ['binding', 'update', @$args], {}), 'update returns immediately');
        is($sent[-1]{msgtype}, 'update', 'update has its own wire type');
        is_deeply($sent[-1]{args}, @$args && $args->[0] ne 'latest' ? $args : [],
                  'wire preserves pin or leaves latest unpinned');
    }
    ok(!defined BindingsIo_Set($hash, ['binding', 'checkUpdate'], {}), 'manual check returns immediately');
    is($sent[-1]{msgtype}, 'checkUpdate', 'manual check has its own wire type');
    is_deeply($sent[-1]{args}, [], 'manual check needs no parameters');
    my $count = scalar @sent;
    like(BindingsIo_Set($hash, ['binding', 'update', '2.1.4', 'extra'], {}), qr/Usage:/, 'extra update argument rejected');
    like(BindingsIo_Set($hash, ['binding', 'checkUpdate', 'extra'], {}), qr/Usage:/, 'extra check argument rejected');
    like(BindingsIo_Set($hash, ['binding', 'update'], {version => '2.1.4'}), qr/Usage:/, 'unknown named argument rejected');
    is(scalar @sent, $count, 'bad syntax never reaches backend');
    BindingsIo_processCommand($hash, {msgtype => 'version', update_check => 'failed: timeout'});
    is($hash->{helper}{version_options}, '2.1.10,2.1.9,2.1.4', 'failed check preserves choices');

    BindingsIo_doInit($hash);
    ok(!$hash->{'.updateVersionSupported'}, 'reconnect resets capability until backend answers');
    BindingsIo_processCommand($hash, {msgtype => 'version', version => '2.1.4'});
    like(BindingsIo_Set($hash, ['binding', '?'], {}), qr/update:latest checkUpdate:noArg/,
         'old backend never offers stale version choices');
}

done_testing();
exit(0);
