#!/usr/bin/env perl
# The MQTT2_DEVICEs of fhempy's Home Assistant MQTT discovery (core/mqtt_ha.py)
# with the attributes of mqtt_ha_devices.json: readings and published messages.
use strict;
use warnings;
use Test2::V0;
use JSON;
use File::Basename;
our %defs;

InternalTimer(time()+0.5, sub {
	# $/ only while reading: FW_makeImage reads the icons line by line
	my $read_json = sub {
		my $file = dirname(__FILE__) . q[/] . shift;
		open(my $fh, q[<], $file) or die "$file: $!";
		local $/;
		my $data = JSON->new->decode(<$fh>);
		close($fh);
		return $data;
	};
	my $scenarios = $read_json->(q[mqtt_ha_devices.json]);

	my @published;
	{
		no warnings 'redefine';
		*main::IOWrite = sub ($@) { my ($hash, $fn, $msg) = @_; push @published, $msg; return undef; };
	}
	my $io = { NAME => q[m2s] };

	# icons of FHEMWEB like on a page: devStateIcon returns them as HTML
	$main::FW_wname = q[WEB];
	FW_setStylesheet();
	FW_readIcons($_) foreach (qw(f18 fhemSVG openautomation default));
	foreach my $icon (@{$read_json->(q[mqtt_ha_icons.json])}) {
		ok(FW_iconName($icon), qq[FHEMWEB has the icon $icon]);
	}
	my $check_state = sub {
		my ($name, $key, $expected, $after) = @_;
		if ($key eq q[STATE]) {
			is($defs{$name}{STATE}, $expected, qq[$name STATE$after]);
		} elsif ($key eq q[ICON]) {
			my ($html) = FW_dev2image($name);
			like($html, qr/^<.*\b\Q$expected\E(?=[ "])/s, qq[$name icon $expected$after]);
		} else {
			is(ReadingsVal($name, $key, undef), $expected, qq[$name reading $key$after]);
		}
	};

	foreach my $sc (@{$scenarios}) {
		my $name = $sc->{name};
		is(CommandDefine(undef, qq[$name MQTT2_DEVICE]), U(), qq[$name defined]);
		my $attrs = $sc->{attributes};
		foreach my $attr (sort keys %{$attrs}) {
			my $value = $attrs->{$attr};
			$value = join(qq[\n], @{$value}) if (ref($value) eq q[ARRAY]);
			next if ($value eq q[]);
			ok(!CommandAttr(undef, qq[$name $attr $value]), qq[$name attr $attr]);
		}

		foreach my $msg (@{$sc->{messages}}) {
			MQTT2_DEVICE_Parse($io, join(qq[\0], q[cid], @{$msg}));
		}
		foreach my $reading (sort keys %{$sc->{readings}}) {
			is(ReadingsVal($name, $reading, undef), $sc->{readings}{$reading}, qq[$name reading $reading]);
		}
		foreach my $key (qw(STATE ICON)) {
			$check_state->($name, $key, $sc->{$key}, q[]) if (defined($sc->{$key}));
		}

		my @later = @{$sc->{later} // []};
		while (@later) {
			my ($msgs, $expected) = splice(@later, 0, 2);
			MQTT2_DEVICE_Parse($io, join(qq[\0], q[cid], @{$_})) foreach (@{$msgs});
			my $after = q[ after ] . join(q[, ], map { $_->[1] } @{$msgs});
			foreach my $key (sort keys %{$expected}) {
				$check_state->($name, $key, $expected->{$key}, $after);
			}
		}

		foreach my $set (@{$sc->{sets}}) {
			@published = ();
			ok(!CommandSet(undef, qq[$name $set->[0]]), qq[set $name $set->[0]]);
			is(\@published, [$set->[1]], qq[set $name $set->[0] publishes]);
		}
	}

	done_testing();
	exit(0);
}, 0);

1;
