#!/usr/bin/env perl
use strict;
use warnings;
use Test2::V0;
use Test2::Tools::Compare qw{is like};
our %defs;

InternalTimer(time()+0.5, sub {
	plan(2);

	# devStateIcon is a FHEMWEB attribute
	LoadModule(q[FHEMWEB]);
	my $deviceName = q[fhempy_devstateicon];
	CommandDefine(undef, qq[$deviceName BindingsIo 10.33.11.27:15733 fhempy]);
	my $hash = $defs{$deviceName};
	RemoveInternalTimer($hash);

	subtest 'define sets the current devStateIcon' => sub {
		plan(1);
		like (AttrVal($deviceName, q[devStateIcon], q[]), qr/attr_ver = "1\.3\.0"/, q[devStateIcon is current]);
	};

	subtest 'an older devStateIcon from fhem.cfg is rejected' => sub {
		plan(2);
		my $ret = CommandAttr(undef, qq[$deviceName devStateIcon {my \$attr_ver = "1.2.0";; "old"}]);
		is ($ret, q[devStateIcon updated], q[old devStateIcon rejected]);
		like (AttrVal($deviceName, q[devStateIcon], q[]), qr/attr_ver = "1\.3\.0"/, q[current devStateIcon kept]);
	};

	RemoveInternalTimer($hash);
	CommandDelete(undef, $deviceName);

	done_testing();
	exit(0);

},'' );

1;
