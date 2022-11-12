#!/usr/bin/env perl
use strict;
use warnings;
use Test2::V0;
use Test2::Tools::Compare qw{is like};
use Test2::Mock;
our %defs;

InternalTimer(time()+0.5, sub {
	plan(7);

	subtest 'define fhempy_local_2 BindingsIo Python (legacy define)' => sub {
		plan(6);
		
        my $deviceName=q[fhempy_local_2];
        my $ret = CommandDefine(undef,qq[$deviceName BindingsIo fhempy]); 
        is ($ret, U(), q[check return from define]);
		is (IsDevice($deviceName), 1, q[check device created with define]);
		is ($defs{$deviceName}{IP}, q[127.0.0.1], q[check IP] );
		is ($defs{$deviceName}{localBinding},1, q[check localBinding] );
		is ($defs{$deviceName}{BindingType},q[fhempy], q[check bindingtype] );
		is (IsDevice(q[fhempyserver_15733]),T(), q[check fhempyserver created] );
		CommandDelete(undef,$deviceName);
	};


	subtest 'define fhempy_local BindingsIo fhempy' => sub {
		plan(6);
		
        my $deviceName=q[fhempy_local];
        my $ret = CommandDefine(undef,qq[$deviceName BindingsIo fhempy]); 
        is ($ret, U(), q[check return from define]);
		is (IsDevice($deviceName), 1, q[check device created with define]);
		is ($defs{$deviceName}{IP}, q[127.0.0.1], q[check IP] );
		is ($defs{$deviceName}{localBinding},1, q[check localBinding] );
		is ($defs{$deviceName}{BindingType},q[fhempy], q[check bindingtype] );
		is (IsDevice(q[fhempyserver_15733]),T(), q[check fhempyserver created] );
	};


	subtest 'define fhempy_remote BindingsIo IP:15733 fhempy' => sub {
		plan(5);
		
        my $deviceName=q[fhempy_remote];
        my $ret = CommandDefine(undef,qq[$deviceName BindingsIo 10.33.11.25:15733 fhempy]); 
        is ($ret, U(), q[check return from define]);
		is (IsDevice($deviceName), 1, q[check device created with define]);
		is ($defs{$deviceName}{IP}, q[10.33.11.25], q[check IP ] );
		is ($defs{$deviceName}{localBinding},0, q[check localBinding] );
		is ($defs{$deviceName}{BindingType},q[fhempy], q[check bindigtype] );
	};
	
	
	subtest 'define fhempy_remote_2 BindingsIo HOSTNAME:15733 fhempy' => sub {
		plan(5);
		
        my $deviceName=q[fhempy_remote_2];
        my $ret = CommandDefine(undef,qq[$deviceName BindingsIo fhempy-server:15733 fhempy]); 
        is ($ret, U(), q[check return from define]);
        is (IsDevice($deviceName), 1, q[check device created with define]);
		is ($defs{$deviceName}{IP}, q[fhempy-server], q[check IP ] );
		is ($defs{$deviceName}{localBinding},0, q[check localBinding] );
		is ($defs{$deviceName}{BindingType},q[fhempy], q[check bindingtype] );
	};


	
	subtest 'define fhempy_remote_3_ip BindingsIo IP:15733 fhempy, already defined via hostname (fhempy_remote_3_hostname)' => sub {
		plan(6);

		my $fhem_addr = gethostbyname(q[fhem.de]) ;
		my $fhem_ip = inet_ntoa($fhem_addr) ;
		my $deviceName_hn=q[fhempy_remote_3_hostname];
        # note(qq[defining $deviceName_hn BindingsIo fhem.de:15733 fhempy]);
		my $ret = CommandDefine(undef,qq[$deviceName_hn BindingsIo fhem.de:15733 fhempy]); 
		
		my $deviceName_ip=q[fhempy_remote_3_ip];
		# note(qq[defining $deviceName_ip BindingsIo $fhem_ip:15733 fhempy]);
		$ret = CommandDefine(undef,qq[$deviceName_ip BindingsIo $fhem_ip:15733 fhempy]); 
        like ($ret,qr/already defined and/, q[check return from define]);
		is (IsDevice($deviceName_hn), 1, q[check device created with define]);
		is ($defs{$deviceName_hn}{IP}, qq[$fhem_ip], q[check IP ] );
		is ($defs{$deviceName_hn}{localBinding},0, q[check localBinding] );
		is ($defs{$deviceName_hn}{BindingType},q[fhempy], q[check bindigtype] );

		is (IsDevice($deviceName_ip), 0, q[check device with ip is not created]);

	};

	subtest 'define fhempy_3 BindingsIo | to few parameters' => sub {
		plan(2);
		
        my $deviceName=q[fhempy_3];
        my $ret = CommandDefine(undef,qq[$deviceName BindingsIo]); 
        like ($ret,qr/to few parameters/ , q[check return from define]);
		is (IsDevice($deviceName), 0, q[check device is not created with define]);
	};

	subtest 'define fhempy_3 BindingsIo wrongtype | wrong binding type' => sub {
		plan(2);
		
        my $deviceName=q[fhempy_3];
        my $ret = CommandDefine(undef,qq[$deviceName BindingsIo wrongtype]); 
        like ($ret,qr/unsupported parameters given/ , q[check return from define]);
		is (IsDevice($deviceName), 0, q[check device is not created with define]);

	};



	done_testing();
	exit(0);

},'' );

1;