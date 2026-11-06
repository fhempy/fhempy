#!/usr/bin/env perl
use strict;
use warnings;
use Test2::V0;
our %defs;

InternalTimer(time()+0.5, sub {
	plan(5);

	my $deviceName = q[fhempy_ops];
	CommandDefine(undef, qq[$deviceName BindingsIo 10.33.11.29:15733 fhempy]);
	my $hash = $defs{$deviceName};
	RemoveInternalTimer($hash);
	CommandDefine(undef, q[ops_dev dummy]);

	my @replies;
	{
		no warnings 'redefine';
		*main::DevIo_SimpleWrite = sub($$$;$) { push @replies, $_[1] };
	}
	my $run = sub {
		my ($raw) = @_;
		BindingsIo_processCommand($hash, BindingsIo_decodeJson($raw));
		return BindingsIo_decodeJson($replies[-1]);
	};

	subtest 'fhempy can detect protocol 2' => sub {
		plan(1);
		is (BindingsIo_protocol(), 2, q[protocol 2]);
	};

	subtest 'values are data, not Perl code' => sub {
		plan(4);
		my $reply = $run->(q[{"msgtype":"command","awaitId":1,"NAME":"ops_dev","op":"attr","args":{"def":"ops_dev comment it's $x @y \";die"}}]);
		is ($reply->{error}, 0, q[attr without error]);
		is (AttrVal("ops_dev", "comment", ""), q[it's $x @y ";die], q[value unchanged]);
		$reply = $run->(q[{"msgtype":"command","awaitId":2,"NAME":"ops_dev","op":"attr_val","args":{"name":"ops_dev","attr":"comment","default":""}}]);
		is ($reply->{result}, q[it's $x @y ";die], q[attr_val]);
		is ($reply->{awaitId}, 2, q[reply to the command]);
	};

	subtest 'readings and device info' => sub {
		plan(4);
		readingsSingleUpdate($defs{ops_dev}, "temperature", "21.5", 0);
		my $reply = $run->(q[{"msgtype":"command","awaitId":3,"NAME":"ops_dev","op":"readings_val","args":{"name":"ops_dev","reading":"temperature","default":"none"}}]);
		is ($reply->{result}, q[21.5], q[readings_val]);
		$reply = $run->(q[{"msgtype":"command","awaitId":4,"NAME":"ops_dev","op":"readings_val","args":{"name":"ops_dev","reading":"missing","default":"none"}}]);
		is ($reply->{result}, q[none], q[default]);
		$reply = $run->(q[{"msgtype":"command","awaitId":5,"NAME":"ops_dev","op":"device_info","args":{"name":"ops_dev","attrs":{"comment":"","room":"none"}}}]);
		is ($reply->{result}{attr}{room}, q[none], q[device_info default]);
		ok (exists $reply->{result}{init_done}, q[device_info init_done]);
	};

	subtest 'delete operations' => sub {
		plan(2);
		$run->(q[{"msgtype":"command","awaitId":6,"NAME":"ops_dev","op":"delete_attr","args":{"def":"ops_dev comment"}}]);
		is (AttrVal("ops_dev", "comment", "gone"), q[gone], q[attribute deleted]);
		$run->(q[{"msgtype":"command","awaitId":7,"NAME":"ops_dev","op":"delete_reading","args":{"def":"ops_dev temperature"}}]);
		is (ReadingsVal("ops_dev", "temperature", "gone"), q[gone], q[reading deleted]);
	};

	subtest 'unknown operation is an error' => sub {
		plan(2);
		my $reply = $run->(q[{"msgtype":"command","awaitId":8,"NAME":"ops_dev","op":"no_such_op","args":{}}]);
		is ($reply->{error}, 1, q[error]);
		like ($reply->{errorText}, qr/unknown operation/, q[error text]);
	};

	RemoveInternalTimer($hash);
	CommandDelete(undef, $deviceName);
	CommandDelete(undef, q[ops_dev]);

	done_testing();
	exit(0);

},'');

1;
