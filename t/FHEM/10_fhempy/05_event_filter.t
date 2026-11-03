#!/usr/bin/env perl
use strict;
use warnings;
use Test2::V0;
use Test2::Tools::Compare qw{is like};
our %defs;
our %modules;

InternalTimer(time()+0.5, sub {
	plan(7);

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

	CommandDefine(undef, q[board fhempy dashboard]);
	CommandDefine(undef, q[lamp dummy]);
	CommandDefine(undef, q[meter dummy]);
	my $hash = $defs{board};

	fhempy_setEventDevices(q[board], q[lamp,meter]);
	like(fhempy_setEventFilter(q[board], q[(]), qr/^Invalid regexp/, q[invalid regexp is rejected]);
	is(fhempy_setEventFilter(q[board], q[^[^:]+:(?:state|power): ]), U(), q[filter set]);

	@written = ();
	CommandSet(undef, q[lamp on]);
	CommandSetReading(undef, q[meter power 100]);
	CommandSetReading(undef, q[meter power 120]);
	CommandSetReading(undef, q[meter voltage 230]);
	is([grep { $_->[1] =~ /^event/ } @written], [], q[events are collected first]);

	fhempy_sendFilteredEvents($hash);
	my @sent = grep { $_->[1] eq q[eventlist] } @written;
	is(scalar(@sent), 1, q[one message for all events]);
	is($sent[0][2], [[q[lamp], q[state: on]], [q[meter], q[power: 120]]],
		q[only matching events, newest value per reading]);

	is(fhempy_setEventFilter(q[board], q[]), U(), q[filter removed]);
	@written = ();
	CommandSet(undef, q[lamp off]);
	is([map { $_->[1] } @written], [q[event]], q[without filter every event is sent at once]);

	exit(0);
}, 0);

1;
