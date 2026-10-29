#!/usr/bin/env perl
use strict;
use warnings;
use Test2::V0;
use Test2::Tools::Compare qw{is like};
our %defs;
our %modules;

InternalTimer(time()+0.5, sub {
	plan(7);

	CommandDefine(undef, q[fhempy_local BindingsIo 10.33.11.27:15733 fhempy]);
	RemoveInternalTimer($defs{fhempy_local});
	$modules{BindingsIo}{WriteFn} = sub { return undef; };
	{
		no warnings 'redefine';
		*main::DevIo_IsOpen = sub { return 1; };
	}

	CommandDefine(undef, q[tl fhempy timeline]);
	CommandDefine(undef, q[other fhempy wienernetze_smartmeter]);
	CommandAttr(undef, q[tl room fhempy,Timeline]);
	CommandAttr(undef, q[other room fhempy]);

	is($modules{fhempy}{FW_summaryFn}, q[fhempy_summaryFn], q[summary function registered]);
	like(fhempy_summaryFn(q[WEB], q[tl], q[Timeline], {}), qr/fhempyTimelineRoom\("tl"\)/,
		q[timeline is drawn in a room of its own]);
	is(fhempy_summaryFn(q[WEB], q[tl], q[fhempy], {}), U(), q[row in a room with other devices]);
	is(fhempy_summaryFn(q[WEB], q[tl], q[all], {}), U(), q[row in Everything]);
	is(fhempy_summaryFn(q[WEB], q[tl], q[], {}), U(), q[no timeline outside of a room]);
	is(fhempy_summaryFn(q[WEB], q[other], q[Timeline], {}), U(), q[other devices keep their row]);
	is(fhempy_summaryFn(q[WEB], q[missing], q[Timeline], {}), U(), q[unknown device]);

	exit(0);
}, 0);

1;
