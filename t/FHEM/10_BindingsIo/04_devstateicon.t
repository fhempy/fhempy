#!/usr/bin/env perl
use strict;
use warnings;
use Test2::V0;
use Test2::Tools::Compare qw{is like unlike};
our %defs;

InternalTimer(time()+0.5, sub {
	plan(6);

	# devStateIcon is a FHEMWEB attribute
	LoadModule(q[FHEMWEB]);
	my $deviceName = q[fhempy_devstateicon];
	CommandDefine(undef, qq[$deviceName BindingsIo 10.33.11.27:15733 fhempy]);
	my $hash = $defs{$deviceName};
	RemoveInternalTimer($hash);

	subtest 'define sets the current devStateIcon' => sub {
		plan(1);
		like (AttrVal($deviceName, q[devStateIcon], q[]), qr/attr_ver = "1\.4\.0"/, q[devStateIcon is current]);
	};

	subtest 'an older default devStateIcon is upgraded' => sub {
		plan(2);
		my $old = BindingsIo_defaultDevStateIcon();
		$old =~ s/1\.4\.0/1.3.0/;
		CommandAttr(undef, qq[$deviceName devStateIcon $old]);
		readingsSingleUpdate($hash, q[.devStateIconDefault], BindingsIo_devStateIconChecksum($old), 0);
		BindingsIo_upgradeDevStateIcon($hash);
		like (AttrVal($deviceName, q[devStateIcon], q[]), qr/attr_ver = "1\.4\.0"/, q[default upgraded]);
		ok (BindingsIo_devStateIconChecksum(qq[{ my \$a = 1;;\n 2 }]) eq BindingsIo_devStateIconChecksum(q[{my $a = 1; 2}]), q[checksum ignores fhem.cfg escaping]);
	};

	subtest 'an edited devStateIcon with attr_ver is kept' => sub {
		plan(1);
		my $custom = q[{ my $attr_ver = "1.3.0";; "custom" }];
		CommandAttr(undef, qq[$deviceName devStateIcon $custom]);
		BindingsIo_upgradeDevStateIcon($hash);
		like (AttrVal($deviceName, q[devStateIcon], q[]), qr/custom/, q[edited devStateIcon kept]);
	};

	subtest 'a custom devStateIcon is kept' => sub {
		plan(2);
		ok (!CommandAttr(undef, qq[$deviceName devStateIcon connected:on]), q[attribute accepted]);
		BindingsIo_upgradeDevStateIcon($hash);
		is (AttrVal($deviceName, q[devStateIcon], q[]), q[connected:on], q[custom devStateIcon kept]);
	};

	subtest 'a deleted devStateIcon stays deleted' => sub {
		plan(1);
		CommandDeleteAttr(undef, qq[$deviceName devStateIcon]);
		BindingsIo_upgradeDevStateIcon($hash);
		is (AttrVal($deviceName, q[devStateIcon], q[]), q[], q[no devStateIcon]);
	};

	subtest 'set defaultDevStateIcon restores the default' => sub {
		plan(2);
		CommandAttr(undef, qq[$deviceName devStateIcon connected:on]);
		ok (!CommandSet(undef, qq[$deviceName defaultDevStateIcon]), q[set accepted]);
		like (AttrVal($deviceName, q[devStateIcon], q[]), qr/attr_ver = "1\.4\.0"/, q[default restored]);
	};

	RemoveInternalTimer($hash);
	CommandDelete(undef, $deviceName);

	done_testing();
	exit(0);

},'' );

1;
