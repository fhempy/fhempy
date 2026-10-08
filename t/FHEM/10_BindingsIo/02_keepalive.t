#!/usr/bin/env perl
use strict;
use warnings;
use Test2::V0;
use Test2::Tools::Compare qw{is like};
use Protocol::WebSocket::Frame;
use Time::HiRes qw(time);
our %defs;

InternalTimer(time()+0.5, sub {
	plan(2);

	my $deviceName = q[fhempy_keepalive];
	CommandDefine(undef, qq[$deviceName BindingsIo 10.33.11.26:15733 fhempy]);
	my $hash = $defs{$deviceName};
	RemoveInternalTimer($hash);

	# fake an open websocket connection, the "socket" is a pipe
	my ($reader, $writer);
	pipe($reader, $writer);
	$hash->{TCPDev} = $writer;
	$hash->{FD} = fileno($writer);
	$hash->{STATE} = q[opened];

	subtest 'peer answered recently: send a ping' => sub {
		plan(3);

		$hash->{".lastReceived"} = time - 10;
		BindingsIo_keepAlive($hash);

		my $buf = q[];
		sysread($reader, $buf, 100);
		my $frame = Protocol::WebSocket::Frame->new;
		$frame->append($buf);
		ok (defined($frame->next), q[a websocket frame was written]);
		ok ($frame->is_ping, q[the frame is a ping]);
		is ($hash->{STATE}, q[opened], q[connection stays open]);
	};

	subtest 'peer silent for too long: disconnect' => sub {
		plan(3);

		$hash->{".lastReceived"} = time - 100;
		BindingsIo_keepAlive($hash);

		is ($hash->{STATE}, q[disconnected], q[state is disconnected]);
		is ($hash->{TCPDev}, U(), q[connection closed]);
		is (ReadingsVal($deviceName, q[state], q[]), q[disconnected], q[state reading is disconnected]);
	};

	RemoveInternalTimer($hash);
	CommandDelete(undef, $deviceName);

	done_testing();
	exit(0);

},'' );

1;
