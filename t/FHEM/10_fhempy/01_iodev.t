#!/usr/bin/env perl
use strict;
use warnings;
use Test2::V0;
use Test2::Tools::Compare qw{is like};
our %defs;
our %modules;
our %attr;

InternalTimer(time()+0.5, sub {
	plan(9);

	# remote peers are defined before and after the local fhempy server
	CommandDefine(undef, q[peer_a BindingsIo 10.33.11.27:15733 fhempy]);
	CommandDefine(undef, q[master BindingsIo fhempy]);
	CommandDefine(undef, q[peer_b BindingsIo 10.33.11.28:15733 fhempy]);
	RemoveInternalTimer($defs{$_}) for qw(peer_a master peer_b);
	delete $defs{fhempyserver_15733};

	my @written;
	$modules{BindingsIo}{WriteFn} = sub {
		my ($io, $dev, $function, $a, $h) = @_;
		push @written, [$io->{NAME}, $dev->{NAME}, $function];
		return undef;
	};

	CommandDefine(undef, q[dev fhempy helloworld]);
	is($defs{dev}{IODev}{NAME}, q[master], q[new device uses the local fhempy server]);

	CommandDefMod(undef, q[dev fhempy helloworld]);
	is($defs{dev}{IODev}{NAME}, q[master], q[modify keeps the IODev]);

	# FHEMWEB detail page of a device without attributes from fhempy
	$defs{dev}{".AttrList"} = q[.*];
	fhempy_detailFn(q[WEB], q[dev], q[], undef);
	like($defs{dev}{".AttrList"}, qr/^IODev:master,peer_a,peer_b disable:0,1 /, q[detail page offers the IODev list]);

	like(CommandAttr(undef, q[dev IODev nothere]), qr/not a BindingsIo device/, q[unknown IODev is rejected]);

	@written = ();
	is(CommandAttr(undef, q[dev IODev peer_b]), q[], q[IODev changed]);
	is($defs{dev}{IODev}{NAME}, q[peer_b], q[device uses the new IODev]);
	is($written[0], [q[master], q[dev], q[Undefine]], q[device is removed from the old fhempy server]);
	fhempy_changedIODev($defs{dev});
	is($written[1], [q[peer_b], q[dev], q[Define]], q[device is defined on the new fhempy server]);

	CommandDeleteAttr(undef, q[dev IODev]);
	fhempy_changedIODev($defs{dev});
	is($defs{dev}{IODev}{NAME}, q[master], q[deleting IODev returns to the local fhempy server]);

	exit(0);
}, 0);

1;
