#!/usr/bin/env perl
use strict;
use warnings;
use Test2::V0;
use Test2::Tools::Compare qw{is like};
our %defs;
our $init_done;

InternalTimer(time()+0.5, sub {
	plan(3);

	# devStateIcon is a FHEMWEB attribute
	LoadModule(q[FHEMWEB]);
	my $def = q[BindingsIo 10.33.11.29:15733 fhempy];
	my $deviceName = q[fhempy_defaults];

	subtest 'a new device gets the default attributes' => sub {
		plan(4);
		CommandDefine(undef, qq[$deviceName $def]);
		RemoveInternalTimer($defs{$deviceName});
		is (AttrVal($deviceName, q[room], q[]), q[fhempy], q[room]);
		is (AttrVal($deviceName, q[icon], q[]), q[file_json-ld2], q[icon]);
		is (AttrVal($deviceName, q[group], q[]), q[fhempy], q[group]);
		like (AttrVal($deviceName, q[devStateIcon], q[]), qr/attr_ver/, q[devStateIcon]);
	};

	subtest 'changed and deleted attributes are kept by defmod' => sub {
		plan(4);
		CommandAttr(undef, qq[$deviceName icon my_icon]);
		CommandDeleteAttr(undef, qq[$deviceName group]);
		CommandDeleteAttr(undef, qq[$deviceName devStateIcon]);
		CommandDefMod(undef, qq[$deviceName $def]);
		RemoveInternalTimer($defs{$deviceName});
		is (AttrVal($deviceName, q[icon], q[]), q[my_icon], q[changed icon kept]);
		is (AttrVal($deviceName, q[group], q[]), q[], q[deleted group stays deleted]);
		is (AttrVal($deviceName, q[devStateIcon], q[]), q[], q[deleted devStateIcon stays deleted]);
		is (AttrVal($deviceName, q[room], q[]), q[fhempy], q[room kept]);
	};

	subtest 'no defaults while FHEM starts (attr lines of fhem.cfg follow)' => sub {
		plan(3);
		CommandDelete(undef, $deviceName);
		$init_done = 0;
		CommandDefine(undef, qq[$deviceName $def]);
		$init_done = 1;
		RemoveInternalTimer($defs{$deviceName});
		is (AttrVal($deviceName, q[icon], q[]), q[], q[no icon]);
		is (AttrVal($deviceName, q[group], q[]), q[], q[no group]);
		is (AttrVal($deviceName, q[devStateIcon], q[]), q[], q[no devStateIcon]);
		CommandDelete(undef, $deviceName);
	};

	done_testing();
	exit(0);

},'' );

1;
