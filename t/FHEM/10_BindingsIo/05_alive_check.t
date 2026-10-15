#!/usr/bin/env perl
use strict;
use warnings;
use Test2::V0;
use Test2::Tools::Compare qw{is like};
use Time::HiRes qw(time);
our %defs;

InternalTimer(time()+0.5, sub {
	plan(4);

	my $deviceName = q[fhempy_alive];
	CommandDefine(undef, qq[$deviceName BindingsIo 10.33.11.27:15733 fhempy]);
	my $hash = $defs{$deviceName};
	RemoveInternalTimer($hash);

	CommandDefine(undef, q[alive_dev dummy]);
	my $devhash = $defs{alive_dev};
	$devhash->{FHEMPYTYPE} = q[helloworld];
	$devhash->{args} = [qw(alive_dev fhempy helloworld)];
	$devhash->{argsh} = {};
	$devhash->{".AttrList"} = q[IODev];

	# fake an open websocket connection to a peer that never answers,
	# the "socket" is a pipe
	my ($reader, $writer);
	pipe($reader, $writer);
	$hash->{TCPDev} = $writer;
	$hash->{FD} = fileno($writer);
	$hash->{STATE} = q[opened];
	$hash->{connecttime} = time;
	$hash->{".lastReceived"} = time;

	subtest 'first timeout: 3s, no 60s after connect, alive check started' => sub {
		plan(3);

		my $start = time;
		my $ret = BindingsIo_Write($hash, $devhash, q[Set], [qw(alive_dev on)], {});
		my $duration = time - $start;
		is ($ret, U(), q[no result]);
		ok ($duration > 2.5 && $duration < 5, qq[returned after the 3s timeout ($duration)]);
		ok (defined($hash->{".aliveCheckSent"}), q[alive check started]);
	};

	subtest 'while the alive check runs: short timeout' => sub {
		plan(1);

		my $start = time;
		BindingsIo_Write($hash, $devhash, q[Set], [qw(alive_dev on)], {});
		my $duration = time - $start;
		ok ($duration < 1.5, qq[returned after the short timeout ($duration)]);
	};

	subtest 'peer answered the ping: connection stays open' => sub {
		plan(2);

		$hash->{".lastReceived"} = time + 1;
		BindingsIo_aliveCheckTimeout($hash);
		is ($hash->{STATE}, q[opened], q[connection stays open]);
		is ($hash->{".aliveCheckSent"}, U(), q[alive check finished]);
	};

	subtest 'peer didn\'t answer the ping: disconnect, commands return at once' => sub {
		plan(4);

		$hash->{".lastReceived"} = time - 10;
		BindingsIo_checkAlive($hash);
		BindingsIo_aliveCheckTimeout($hash);
		is ($hash->{STATE}, q[disconnected], q[state is disconnected]);
		is ($hash->{TCPDev}, U(), q[connection closed]);

		my $start = time;
		BindingsIo_Write($hash, $devhash, q[Set], [qw(alive_dev on)], {});
		my $duration = time - $start;
		ok ($duration < 0.1, qq[returned at once ($duration)]);
		is (ReadingsVal(q[alive_dev], q[state], q[]), q[fhempy server offline], q[device shows offline]);
	};

	RemoveInternalTimer($hash);
	CommandDelete(undef, q[alive_dev]);
	CommandDelete(undef, $deviceName);

	done_testing();
	exit(0);

},'' );

1;
