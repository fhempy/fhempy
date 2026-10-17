#!/usr/bin/env perl
use strict;
use warnings;
use Test::More;
use File::Basename qw(dirname);
use File::Spec;

use vars qw(%defs %ntfyHash $init_done $readingFnAttributes);

# These imports are unused by Define; allow this test to run without FHEM too.
BEGIN {
    $INC{'JSON.pm'} //= 1;
    $INC{'Color.pm'} //= 1;
    *Log3 = sub {} unless defined &Log3;
    # Match FHEM's helper when running standalone. Inside FHEM use the real one.
    *setDisableNotifyFn = sub {
        my ($hash, $doit) = @_;
        if ($doit) {
            delete $hash->{NOTIFYDEV};
            $hash->{disableNotifyFn} = 1;
        } else {
            delete $hash->{disableNotifyFn};
        }
        %ntfyHash = ();
    } unless defined &setDisableNotifyFn;
}

my $module = File::Spec->rel2abs(File::Spec->catfile(
    dirname(__FILE__), '..', '..', '..', 'FHEM', '10_fhempy.pm'
));
require $module unless defined &fhempy_Define;

{
    no warnings qw(redefine once);
    local $init_done = 1;
    local %defs;
    local %ntfyHash;
    my $reply;
    my @writes;
    local *Log3 = sub {};
    local *devspec2array = sub { return ('fhempy_local'); };
    local *IsDevice = sub { return 1; };
    local *setDevAttrList = sub { $defs{$_[0]}{'.AttrList'} = $_[1]; };
    local *AssignIoPort = sub { $_[0]{IODev} = { NAME => 'assigned_io' }; };
    local *IOWrite = sub {
        push @writes, [@_];
        # Readings/events processed while waiting may rebuild this cache.
        $ntfyHash{sensor} = [];
        return $reply;
    };

    subtest 'rejected modification preserves the complete old definition' => sub {
        my $hash = {
            NAME => 'validation_test',
            args => ['validation_test', 'fhempy', 'example', 'old'],
            argsh => { option => 'old' },
            FHEMPYTYPE => 'example', PYTHONTYPE => 'example',
            '.AttrList' => 'interval verbose',
            IODev => { NAME => 'original_io' },
            NOTIFYDEV => 'sensor,other_sensor',
            READINGS => { state => { VAL => 'working' } },
        };
        $defs{$hash->{NAME}} = $hash;
        my %previous = %$hash;
        $reply = 'Usage supplied by the Python module';

        is(fhempy_Define($hash, ['validation_test', 'fhempy', 'example'], {}),
            $reply, 'module error is returned unchanged');
        is_deeply($hash, \%previous, 'arguments, types, attributes, IODev and readings survive');
        is(scalar @writes, 1, 'one Define request');
        is_deeply(\%ntfyHash, {}, 'rebuilt notification cache invalidated after rejection');
    };

    subtest 'accepted definition stores arbitrary module arguments' => sub {
        my $hash = { NAME => 'validation_test' };
        $defs{$hash->{NAME}} = $hash;
        my $args = ['validation_test', 'fhempy', 'another_module', 'A', 'B', 'C'];
        my $argsh = { optional => 'value' };
        $reply = undef;

        is(fhempy_Define($hash, $args, $argsh), undef, 'accepted');
        is_deeply($hash->{args}, $args, 'positional arguments stored');
        is_deeply($hash->{argsh}, $argsh, 'keyword arguments stored');
        is($hash->{FHEMPYTYPE}, 'another_module', 'module type stored');
        is($hash->{disableNotifyFn}, 1, 'accepted definition starts without event subscriptions');
    };

    subtest 'rejected modification preserves disabled notifications' => sub {
        my $hash = { NAME => 'validation_test', disableNotifyFn => 1 };
        $defs{$hash->{NAME}} = $hash;
        $reply = 'Definition rejected';

        is(fhempy_Define($hash, ['validation_test', 'fhempy', 'example'], {}),
            $reply, 'error returned');
        is_deeply($hash, { NAME => 'validation_test', disableNotifyFn => 1 },
            'disabled notification status is preserved');
        is_deeply(\%ntfyHash, {}, 'notification cache invalidated');
    };

    subtest 'rejected new definition does not retain temporary metadata' => sub {
        my $hash = { NAME => 'validation_test' };
        $defs{$hash->{NAME}} = $hash;
        $reply = 'Definition rejected';

        is(fhempy_Define($hash, ['validation_test', 'fhempy', 'example'], {}),
            $reply, 'error returned');
        is_deeply($hash, { NAME => 'validation_test' }, 'new metadata removed');
    };
}

done_testing();
exit(0);
