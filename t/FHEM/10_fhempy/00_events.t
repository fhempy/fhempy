#!/usr/bin/env perl
use strict;
use warnings;
use Test2::V0;
use Test2::Tools::Compare qw{is};
our %defs;
our %modules;

InternalTimer(time()+0.5, sub {
	plan(5);

	CommandDefine(undef, q[fhempy_local BindingsIo 10.33.11.27:15733 fhempy]);
	RemoveInternalTimer($defs{fhempy_local});

	my @written;
	$modules{BindingsIo}{WriteFn} = sub {
		my ($io, $dev, $function, $a, $h) = @_;
		push @written, [$dev->{NAME}, $function, @$a];
		return undef;
	};
	{
		no warnings 'redefine';
		*main::DevIo_IsOpen = sub { return 1; };
	}

	CommandDefine(undef, q[bridge fhempy matter_bridge]);
	CommandDefine(undef, q[lamp dummy]);
	is($defs{bridge}{disableNotifyFn}, 1, q[fhempy devices get no events by default]);

	@written = ();
	CommandSet(undef, q[lamp on]);
	is([grep { $_->[1] eq q[event] } @written], [], q[events are not forwarded by default]);

	is(fhempy_setEventDevices(q[bridge], q[lamp]), U(), q[setEventDevices succeeds]);
	@written = ();
	CommandSet(undef, q[lamp off]);
	is([grep { $_->[1] eq q[event] } @written], [[q[lamp], q[event], q[state: off]]], q[event of lamp is sent to fhempy]);

	fhempy_setEventDevices(q[bridge], q[]);
	@written = ();
	CommandSet(undef, q[lamp on]);
	is([grep { $_->[1] eq q[event] } @written], [], q[no events after empty device list]);

	exit(0);
}, 0);

1;
