#!/usr/bin/env perl
use strict;
use warnings;
use Test::More;
use File::Basename qw(dirname);
use File::Spec;
use JSON::PP ();
use POSIX ();

our (%defs, %attr, $init_done);
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
    my (@sent, @timers);
    my %autoattr;
    local *Log3 = sub {};
    local *DevIo_IsOpen = sub { 1 };
    local *DevIo_SimpleWrite = sub { push @sent, JSON::PP::decode_json($_[1]) };
    local *BindingsIo_readWebsocketMessage = sub { die 'Update commands must not wait for a reply' };
    local *AttrVal = sub { $autoattr{$_[0]}{$_[1]} // $_[2] };
    local *ReadingsVal = sub { $defs{$_[0]}{READINGS}{$_[1]}{VAL} // $_[2] };
    local *readingsSingleUpdate = sub { $_[0]{READINGS}{$_[1]}{VAL} = $_[2] };
    local *InternalTimer = sub { push @timers, [$_[0], $_[1], $_[2]] };
    local *RemoveInternalTimer = sub { @timers = grep { $_->[1] ne $_[1] } @timers };
    my $hash = { NAME => 'binding', STATE => 'connected', BindingType => 'fhempy',
                 TYPE => 'BindingsIo', READINGS => {version => {VAL => '2.5.1'}},
                 '.updateVersionSupported' => 1 };
    $defs{binding} = $hash;

    my $noon = POSIX::mktime(0, 0, 12, 21, 9, 126);
    is(BindingsIo_nextAutoUpdateTime($hash, $noon), POSIX::mktime(0, 0, 3, 22, 9, 126),
       'default window is the next night at 03:00');
    $autoattr{binding}{autoUpdateTime} = '23:30';
    is(BindingsIo_nextAutoUpdateTime($hash, $noon), POSIX::mktime(0, 30, 23, 21, 9, 126),
       'autoUpdateTime later today');
    delete $autoattr{binding}{autoUpdateTime};

    BindingsIo_processCommand($hash, {msgtype => 'version', version_available => '2.6.0'});
    BindingsIo_scheduleAutoUpdate($hash);
    is(scalar @timers, 0, 'autoUpdate is off by default');
    BindingsIo_autoUpdate($hash);
    is(scalar @sent, 0, 'no update without autoUpdate');

    $autoattr{binding}{autoUpdate} = 1;
    BindingsIo_scheduleAutoUpdate($hash);
    is($timers[-1][1], 'BindingsIo_autoUpdate', 'autoUpdate is scheduled');
    ok($timers[-1][0] > time(), 'autoUpdate runs in the update window');
    BindingsIo_autoUpdate($hash);
    is($sent[-1]{msgtype}, 'update', 'autoUpdate starts the update');
    is_deeply($sent[-1]{args}, ['2.6.0'], 'autoUpdate installs the available version');
    is(ReadingsVal('binding', 'update_status', ''), 'starting', 'autoUpdate shows the update');
    is(scalar(grep { $_->[1] eq 'BindingsIo_autoUpdate' } @timers), 1, 'next window is scheduled');

    my $count = scalar @sent;
    $hash->{READINGS}{update_status}{VAL} = 'failed: installation failed; see fhempy log';
    BindingsIo_autoUpdate($hash);
    is(scalar @sent, $count, 'a version is tried only once');

    BindingsIo_processCommand($hash, {msgtype => 'version', version_available => '2.6.1'});
    $hash->{READINGS}{update_status}{VAL} = 'installing fhempy';
    BindingsIo_autoUpdate($hash);
    is(scalar @sent, $count, 'no autoUpdate while an update runs');
    $hash->{READINGS}{update_status}{VAL} = '';
    BindingsIo_autoUpdate($hash);
    is_deeply($sent[-1]{args}, ['2.6.1'], 'a newer version is tried again');

    $count = scalar @sent;
    $hash->{READINGS}{version}{VAL} = '2.6.1';
    $hash->{READINGS}{'.autoUpdateVersion'}{VAL} = '';
    BindingsIo_autoUpdate($hash);
    is(scalar @sent, $count, 'no autoUpdate when the newest version is installed');

    like(BindingsIo_Attr('set', 'binding', 'autoUpdateTime', '3 Uhr'), qr/HH:MM/, 'invalid time rejected');
    @timers = ();
    ok(!BindingsIo_Attr('set', 'binding', 'autoUpdateTime', '04:15'), 'valid time accepted');
    is($timers[-1][1], 'BindingsIo_scheduleAutoUpdate', 'changed time reschedules');
}

done_testing();
exit(0);
