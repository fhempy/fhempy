#!/usr/bin/env perl
use strict;
use warnings;
use Test2::V0;
use Test2::Tools::Compare qw{is};

our %defs;

InternalTimer(time()+0.5, sub {
	plan(3);

	subtest 'define fhempy_local BindingsIo fhempy' => sub {
		plan(4);
		
        my $deviceName=q[fhempy_local];
        CommandDefine(undef,qq[$deviceName BindingsIo fhempy]); 
        is(IsDevice($deviceName), 1, q[check sensor created with define]);
		is ($defs{$deviceName}{IP}, q[localhost], q[check IP] );
		is ($defs{$deviceName}{localBinding},1, q[check localBinding] );
		is ($defs{$deviceName}{BindingType},q[fhempy], q[check bindingtype] );

		
	};

	subtest 'define fhempy_remote BindingsIo IP:15733 fhempy' => sub {
		plan(4);
		
        my $deviceName=q[fhempy_remote];
        CommandDefine(undef,qq[$deviceName BindingsIo 10.33.11.25:15733 fhempy]); 
        is(IsDevice($deviceName), 1, "check sensor created with define");
		is ($defs{$deviceName}{IP}, q[10.33.11.25], q[check IP ] );
		is ($defs{$deviceName}{localBinding},0, q[check localBinding] );
		is ($defs{$deviceName}{BindingType},q[fhempy], q[check bindigtype] );
	};
	
	subtest 'define fhempy_remote_2 BindingsIo HOSTNAME:15733 fhempy' => sub {
		plan(4);
		
        my $deviceName=q[fhempy_remote_2];
        CommandDefine(undef,qq[$deviceName BindingsIo fhempy-server:15733 fhempy]); 
        is(IsDevice($deviceName), 1, "check sensor created with define");
		is ($defs{$deviceName}{IP}, q[fhempy-server], q[check IP ] );
		is ($defs{$deviceName}{localBinding},0, q[check localBinding] );
		is ($defs{$deviceName}{BindingType},q[fhempy], q[check bindigtype] );
	};
	

	done_testing();
	exit(0);

},'' );

1;