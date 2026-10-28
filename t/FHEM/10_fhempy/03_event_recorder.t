#!/usr/bin/env perl
use strict;
use warnings;
use Test2::V0;
use Test2::Tools::Compare qw{is like};
our %defs;
our %modules;

InternalTimer(time()+0.5, sub {
	plan(8);

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

	CommandDefine(undef, q[tl fhempy timeline]);
	CommandDefine(undef, q[lamp dummy]);
	CommandDefine(undef, q[sensor dummy]);
	my $hash = $defs{tl};

	like(fhempy_setEventRecorder(q[tl], 1, q[(]), qr/^Invalid regexp/, q[invalid regexp is rejected]);
	is(fhempy_setEventRecorder(q[tl], 1, q[^[^:]+:(?i:rssi|linkquality): ]), U(), q[recorder starts]);
	is($hash->{NOTIFYDEV}, U(), q[events of all devices]);

	@written = ();
	CommandSet(undef, q[lamp on]);
	CommandSetReading(undef, q[sensor linkquality 120]);
	CommandSetReading(undef, q[sensor RSSI -70]);
	CommandSetReading(undef, q[sensor temperature 21.5]);
	is([grep { $_->[1] eq q[events] } @written], [], q[events are collected first]);
	my @queued = map { "$_->[1]|$_->[2]" } @{$hash->{".recordedEvents"}};
	is(\@queued, [q[lamp|state: on], q[sensor|temperature: 21.5]], q[skipped events are not queued]);

	fhempy_sendRecordedEvents($hash);
	my @sent = grep { $_->[1] eq q[events] } @written;
	is(scalar(@sent), 1, q[one message for all events]);
	is($sent[0][3], {sensor => 2}, q[skipped events are counted]);

	fhempy_setEventRecorder(q[tl], 0);
	@written = ();
	CommandSet(undef, q[lamp off]);
	fhempy_sendRecordedEvents($hash);
	is([grep { $_->[1] =~ /^events?$/ } @written], [], q[no events after stop]);

	exit(0);
}, 0);

1;
