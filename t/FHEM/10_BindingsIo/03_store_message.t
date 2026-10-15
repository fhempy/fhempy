#!/usr/bin/env perl
use strict;
use warnings;
use utf8;
use Encode;
use Test2::V0;
use Test2::Tools::Compare qw{is like};
our %defs;

InternalTimer(time()+0.5, sub {
	plan(5);

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

	RemoveInternalTimer($hash);
	CommandDelete(undef, $deviceName);

	done_testing();
	exit(0);

},'');

1;
