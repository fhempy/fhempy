#!/usr/bin/env perl
use strict;
use warnings;
use Test2::V0;
use Test2::Tools::Compare qw{is like};
our %defs;

InternalTimer(time()+0.5, sub {
	plan(3);

	# a real local define would start fhempy, only the flag matters here
	my $local = q[fhempy_detail_local];
	my $remote = q[fhempy_detail_remote];
	CommandDefine(undef, qq[$local BindingsIo 10.33.11.29:15733 fhempy]);
	CommandDefine(undef, qq[$remote BindingsIo 10.33.11.30:15733 fhempy]);
	RemoveInternalTimer($defs{$local});
	RemoveInternalTimer($defs{$remote});
	$defs{$local}{localBinding} = 1;

	like (BindingsIo_detailFn(q[WEB], $local, q[], undef), qr/fhempyModules\(\).*Install modules/, q[local fhempy shows Install modules]);
	is (BindingsIo_detailFn(q[WEB], $remote, q[], undef), U(), q[no button on a remote peer]);
	is (BindingsIo_detailFn(q[WEB], $local, q[], {}), U(), q[no button in room overview]);

	done_testing();
	exit(0);
}, 0);

1;
