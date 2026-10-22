#!/usr/bin/env perl
use strict;
use warnings;
use Test2::V0;
use Test2::Tools::Compare qw{is};
use Time::HiRes qw(time);
our %defs;

InternalTimer(time()+0.5, sub {
	plan(2);

	my $deviceName = q[fhempy_reconnect];
	CommandDefine(undef, qq[$deviceName BindingsIo 10.33.11.28:15733 fhempy]);
	my $hash = $defs{$deviceName};
	RemoveInternalTimer($hash);

	my $opened = 0;
	no warnings 'redefine';
	local *main::DevIo_OpenDev = sub { $opened++; return undef; };
	use warnings 'redefine';

	subtest 'retries while the state shows the installation' => sub {
		plan(2);

		# FHEM started with a BindingsIo without version reading: the first
		# connect failed and BindingsIo_installing replaced "disconnected"
		BindingsIo_installing($hash);
		RemoveInternalTimer($hash, 'BindingsIo_installing');
		is ($hash->{STATE}, q[Installing fhempy...], q[state shows the installation]);

		BindingsIo_Ready($hash);
		is ($opened, 1, q[connection is retried]);
	};

	subtest 'no reconnect while the connection is open' => sub {
		plan(1);

		my ($reader, $writer);
		pipe($reader, $writer);
		$hash->{TCPDev} = $writer;
		$opened = 0;
		BindingsIo_Ready($hash);
		is ($opened, 0, q[open connection is kept]);
		delete $hash->{TCPDev};
	};

	RemoveInternalTimer($hash);
	CommandDelete(undef, $deviceName);

	done_testing();
	exit(0);

},'' );

1;
