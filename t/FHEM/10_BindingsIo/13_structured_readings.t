#!/usr/bin/env perl
use strict;
use warnings;
use Encode;
use Test2::V0;
our %defs;

InternalTimer(time()+0.5, sub {
	plan(4);

	my $deviceName = q[fhempy_readings];
	CommandDefine(undef, qq[$deviceName BindingsIo 10.33.11.29:15733 fhempy]);
	my $hash = $defs{$deviceName};
	RemoveInternalTimer($hash);
	CommandDefine(undef, q[readings_dev dummy]);
	my $dev = $defs{readings_dev};

	my @replies;
	{
		no warnings 'redefine';
		*main::DevIo_SimpleWrite = sub { push @replies, $_[1] };
	}

	subtest 'fhempy can detect structured readings' => sub {
		plan(1);
		ok (defined(&BindingsIo_readings), q[BindingsIo_readings exists]);
	};

	subtest 'readings from a list without Perl code' => sub {
		plan(5);
		my $raw = Encode::encode("utf8", qq[{"msgtype":"command","awaitId":7,"NAME":"readings_dev","trigger":1,"readings":[["temperature","21.5",null,0],["city","M\xc3\xbcnchen",null,0],["quote","it's \\\\ \$x \@y",null,0]]}]);
		BindingsIo_processCommand($hash, BindingsIo_decodeJson($raw));
		is (ReadingsVal("readings_dev", "temperature", ""), q[21.5], q[reading set]);
		is (ReadingsVal("readings_dev", "city", ""), qq[M\xc3\xbcnchen], q[UTF-8 bytes unchanged]);
		is (ReadingsVal("readings_dev", "quote", ""), q[it's \\ $x @y], q[no Perl interpolation]);
		my $reply = BindingsIo_decodeJson($replies[-1]);
		is ($reply->{awaitId}, 7, q[reply to the command]);
		is ($reply->{error}, 0, q[no error]);
	};

	subtest 'ifchanged and changed flags' => sub {
		plan(2);
		my $time = ReadingsTimestamp("readings_dev", "temperature", "");
		$dev->{READINGS}{temperature}{TIME} = "2000-01-01 00:00:00";
		my $raw = q[{"msgtype":"command","awaitId":8,"NAME":"readings_dev","trigger":0,"readings":[["temperature","21.5",null,1],["state","on",0,0]]}];
		BindingsIo_processCommand($hash, BindingsIo_decodeJson($raw));
		is (ReadingsTimestamp("readings_dev", "temperature", ""), q[2000-01-01 00:00:00], q[unchanged reading not updated]);
		is (ReadingsVal("readings_dev", "state", ""), q[on], q[reading with changed flag set]);
	};

	subtest 'unknown device is no error' => sub {
		plan(1);
		my $raw = q[{"msgtype":"command","awaitId":9,"NAME":"no_such_dev","trigger":1,"readings":[["a","1",null,0]]}];
		BindingsIo_processCommand($hash, BindingsIo_decodeJson($raw));
		is (BindingsIo_decodeJson($replies[-1])->{error}, 0, q[no error]);
	};

	RemoveInternalTimer($hash);
	CommandDelete(undef, $deviceName);
	CommandDelete(undef, q[readings_dev]);

	done_testing();
	exit(0);

},'');

1;
