#!/usr/bin/env perl
use strict;
use warnings;
use Encode;
use Test2::V0;
our %defs;

InternalTimer(time()+0.5, sub {
	plan(1);

	my $deviceName = q[fhempy_nested_resp];
	CommandDefine(undef, qq[$deviceName BindingsIo 10.33.11.28:15733 fhempy]);
	my $hash = $defs{$deviceName};
	RemoveInternalTimer($hash);

	subtest 'nested call during processCommand causes no warning' => sub {
		plan(4);
		$hash->{messages}{0} = [];
		$hash->{messages_count} = {};
		for my $i (1..2) {
			BindingsIo_storeMessage($hash, Encode::encode("utf8",
				qq[{"msgtype":"update_hash","NAME":"dev_A","test":$i}]));
		}

		my @warnings;
		my $processed = 0;
		my $nested = 0;
		{
			no warnings 'redefine';
			local $SIG{__WARN__} = sub { push @warnings, $_[0] };
			local *main::BindingsIo_processCommand = sub {
				$processed++;
				# e.g. a notify sets another fhempy device while the
				# first message is processed
				if (!$nested++) {
					BindingsIo_checkResponseByAllNames($hash);
				}
			};
			BindingsIo_checkResponseByName($hash, { NAME => "dev_A" });
		}

		is (\@warnings, [], q[no Perl warnings]);
		is ($processed, 2, q[both messages processed once]);
		is (scalar(@{$hash->{messages}{0}}), 0, q[queue is empty]);
		is ($hash->{messages_count}, {}, q[messages_count is empty]);
	};

	CommandDelete(undef, $deviceName);
	done_testing();
	exit(0);
},'');

1;
