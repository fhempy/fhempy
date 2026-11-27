#!/usr/bin/env perl
use strict;
use warnings;
use Test2::V0;
use Test2::Tools::Compare qw{is like};
our %defs;

InternalTimer(time()+0.5, sub {
	plan(3);

	my $deviceName = q[fhempy_offline];
	CommandDefine(undef, qq[$deviceName BindingsIo 10.33.11.28:15733 fhempy]);
	my $hash = $defs{$deviceName};
	RemoveInternalTimer($hash);
	$hash->{STATE} = q[disconnected];

	CommandDefine(undef, q[offline_dev dummy]);
	my $devhash = $defs{offline_dev};
	$devhash->{FHEMPYTYPE} = q[helloworld];
	$devhash->{args} = [qw(offline_dev fhempy helloworld)];
	$devhash->{argsh} = {};
	$devhash->{".AttrList"} = q[IODev];

	subtest 'set and get tell that they were not executed' => sub {
		plan(3);

		my $ret = BindingsIo_Write($hash, $devhash, q[Set], [qw(offline_dev on)], {});
		is ($ret, q[fhempy server offline, command not executed], q[set returns a message]);
		$ret = BindingsIo_Write($hash, $devhash, q[Get], [qw(offline_dev status)], {});
		is ($ret, q[fhempy server offline, command not executed], q[get returns a message]);
		is (ReadingsVal(q[offline_dev], q[state], q[]), q[fhempy server offline], q[device shows offline]);
	};

	subtest 'set and get lists of FHEMWEB stay empty' => sub {
		plan(2);

		is (BindingsIo_Write($hash, $devhash, q[Set], [qw(offline_dev ?)], {}), U(), q[set ?]);
		is (BindingsIo_Write($hash, $devhash, q[Get], [qw(offline_dev)], {}), U(), q[get without command]);
	};

	subtest 'attributes can still be set' => sub {
		plan(1);

		is (BindingsIo_Write($hash, $devhash, q[Attr], [qw(set offline_dev verbose 5)], {}), U(), q[attr is accepted]);
	};

	CommandDelete(undef, q[offline_dev]);
	CommandDelete(undef, $deviceName);

	done_testing();
	exit(0);

},'' );

1;
