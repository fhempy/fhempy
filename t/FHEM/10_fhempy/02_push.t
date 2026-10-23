#!/usr/bin/env perl
use strict;
use warnings;
use Test2::V0;
use Test2::Tools::Compare qw{is like};
our %defs;
our %modules;

InternalTimer(time()+0.5, sub {
	plan(4);
	LoadModule(q[fhempy]);

	like(fhempy_push(q[Hello]), qr/define push fhempy push/, q[hint without push device]);

	CommandDefine(undef, q[master BindingsIo fhempy]);
	RemoveInternalTimer($defs{master});
	delete $defs{fhempyserver_15733};
	my @written;
	$modules{BindingsIo}{WriteFn} = sub {
		my ($io, $dev, $function, $a, $h) = @_;
		push @written, [$dev->{NAME}, $function, [@$a], {%$h}];
		return undef;
	};
	CommandDefine(undef, q[mypush fhempy push]);
	@written = ();

	fhempy_push(qq[Washing machine\nis done]);
	is($written[0], [q[mypush], q[Set], [q[mypush], q[message], q[Washing], q[machine], q[is], q[done]], {}],
		q[text is sent with set message]);

	@written = ();
	fhempy_push(q[Door], q[Front "door"], q[Dom]);
	is($written[0][3], {title => q[Front 'door'], to => q[Dom]}, q[title and phone as options]);
	is($written[0][2], [q[mypush], q[message], q[Door]], q[text without options]);

	exit(0);
}, 0);

1;
