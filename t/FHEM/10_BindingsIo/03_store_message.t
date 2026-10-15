#!/usr/bin/env perl
use strict;
use warnings;
use Encode;
use Test2::V0;
use Test2::Tools::Compare qw{is like};
our %defs;

InternalTimer(time()+0.5, sub {
	plan(7);

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

	subtest 'store function reply keeps UTF-8 bytes' => sub {
		plan(3);
		# Protocol::WebSocket::Frame->next returns decoded text
		my $text = Encode::decode("UTF-8", qq[{"id":42,"NAME":"my_device","returnval":"M\xc3\xbcnchen \xe2\x98\xba"}]);
		my $ret = BindingsIo_storeMessage($hash, $text);
		is ($ret, U(), q[storeMessage returns undef on success]);
		is ($hash->{messages}{"my_device"}{42}{returnval}, qq[M\xc3\xbcnchen \xe2\x98\xba], q[FHEM gets UTF-8 bytes]);
		is (length($hash->{messages}{"my_device"}{42}{returnval}), 12, q[no wide characters]);
	};

	subtest 'store raw octets' => sub {
		plan(2);
		my $ret = BindingsIo_storeMessage($hash, qq[{"id":43,"NAME":"my_device","returnval":"K\xc3\xbcche"}]);
		is ($ret, U(), q[storeMessage returns undef on success]);
		is ($hash->{messages}{"my_device"}{43}{returnval}, qq[K\xc3\xbcche], q[bytes unchanged]);
	};

	subtest 'encode FHEM byte strings without double encoding' => sub {
		plan(1);
		my $json = BindingsIo_encodeJson({args => [qq[M\xc3\xbcnchen]]});
		is ($json, qq[{"args":["M\xc3\xbcnchen"]}], q[UTF-8 bytes passed through]);
	};

	subtest 'encode replaces invalid UTF-8' => sub {
		plan(1);
		my $json = BindingsIo_encodeJson({args => [qq[K\xfcche]]});
		is ($json, qq[{"args":["K\xef\xbf\xbdche"]}], q[Latin-1 byte replaced by U+FFFD]);
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
