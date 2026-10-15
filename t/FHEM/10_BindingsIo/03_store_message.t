#!/usr/bin/env perl
use strict;
use warnings;
use utf8;
use Encode;
use Test2::V0;
use Test2::Tools::Compare qw{is like};
our %defs;

InternalTimer(time()+0.5, sub {
	plan(8);

	my $deviceName = q[fhempy_store_msg];
	CommandDefine(undef, qq[$deviceName BindingsIo 10.33.11.27:15733 fhempy]);
	my $hash = $defs{$deviceName};
	RemoveInternalTimer($hash);

	subtest 'store command message without id' => sub {
		plan(2);
		my $raw = Encode::encode("utf8", q[{"msgtype":"command","command":"test_cmd"}]);
		my $ret = BindingsIo_storeMessage($hash, $raw);
		is ($ret, U(), q[storeMessage returns undef on success]);
		is ($hash->{messages}{0}[0]{command}, q[test_cmd], q[message queued in messages->{0}]);
	};

	subtest 'store function reply with id and device NAME' => sub {
		plan(2);
		my $raw = Encode::encode("utf8", q[{"id":42,"NAME":"my_device","returnval":"München"}]);
		my $ret = BindingsIo_storeMessage($hash, $raw);
		is ($ret, U(), q[storeMessage returns undef on success]);
		is ($hash->{messages}{"my_device"}{42}{returnval}, q[München], q[message indexed by device and id]);
	};

	subtest 'store wide-character decoded string fallback' => sub {
		plan(2);
		my $wide_str = q[{"id":43,"NAME":"my_device","returnval":"Küche ☺"}];
		my $ret = BindingsIo_storeMessage($hash, $wide_str);
		is ($ret, U(), q[storeMessage handles wide characters via fallback]);
		is ($hash->{messages}{"my_device"}{43}{returnval}, q[Küche ☺], q[wide character string parsed correctly]);
	};

	subtest 'store malformed JSON returns error' => sub {
		plan(1);
		my $ret = BindingsIo_storeMessage($hash, q[{bad_json: missing closing bracket]);
		is ($ret, q[error], q[storeMessage returns "error" on bad JSON]);
	};

	subtest 'JSON backend is detected' => sub {
		plan(1);
		like ($hash->{JSON_BACKEND}, qr/(PP|XS)/, q[check JSON backend detected]);
	};

	subtest 'messages_count tracks messages per device name' => sub {
		plan(3);
		$hash->{messages}{0} = [];
		$hash->{messages_count} = {};

		my $msg1 = Encode::encode("utf8", q[{"msgtype":"update_hash","NAME":"dev_A","test":1}]);
		my $msg2 = Encode::encode("utf8", q[{"msgtype":"update_hash","NAME":"dev_A","test":2}]);
		my $msg3 = Encode::encode("utf8", q[{"msgtype":"update_hash","NAME":"dev_B","test":3}]);

		BindingsIo_storeMessage($hash, $msg1);
		BindingsIo_storeMessage($hash, $msg2);
		BindingsIo_storeMessage($hash, $msg3);

		is ($hash->{messages_count}{dev_A}, 2, q[dev_A has 2 messages queued]);
		is ($hash->{messages_count}{dev_B}, 1, q[dev_B has 1 message queued]);
		is (scalar(@{$hash->{messages}{0}}), 3, q[total 3 messages in messages->{0}]);
	};

	subtest 'checkResponseByName processes matching device and updates messages_count' => sub {
		plan(4);
		my $devA = { NAME => "dev_A" };
		BindingsIo_checkResponseByName($hash, $devA);

		is ($hash->{messages_count}{dev_A}, U(), q[dev_A count deleted when all dev_A messages processed]);
		is ($hash->{messages_count}{dev_B}, 1, q[dev_B count remains 1]);
		is (scalar(@{$hash->{messages}{0}}), 1, q[only dev_B message remains in queue]);

		# Calling again with devA should fast-exit in O(1) without touching dev_B
		BindingsIo_checkResponseByName($hash, $devA);
		is (scalar(@{$hash->{messages}{0}}), 1, q[dev_B message still in queue after fast-exit]);
	};

	subtest 'checkResponseByAllNames processes remaining messages and clears messages_count' => sub {
		plan(2);
		BindingsIo_checkResponseByAllNames($hash);
		is (scalar(@{$hash->{messages}{0}}), 0, q[queue is empty]);
		is ($hash->{messages_count}, {}, q[messages_count is empty hash]);
	};

	RemoveInternalTimer($hash);
	CommandDelete(undef, $deviceName);

	done_testing();
	exit(0);

},'');

1;
