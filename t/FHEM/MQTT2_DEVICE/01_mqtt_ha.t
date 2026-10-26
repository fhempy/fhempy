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
	my $file = dirname(__FILE__) . q[/mqtt_ha_devices.json];
	open(my $fh, q[<], $file) or die "$file: $!";
	local $/;
	my $scenarios = JSON->new->decode(<$fh>);
	close($fh);

	my @published;
	{
		no warnings 'redefine';
		*main::IOWrite = sub { my ($hash, $fn, $msg) = @_; push @published, $msg; return undef; };
	}
	my $io = { NAME => q[m2s] };

	foreach my $sc (@{$scenarios}) {
		my $name = $sc->{name};
		is(CommandDefine(undef, qq[$name MQTT2_DEVICE]), U(), qq[$name defined]);
		my $attrs = $sc->{attributes};
		foreach my $attr (sort keys %{$attrs}) {
			my $value = $attrs->{$attr};
			$value = join(qq[\n], @{$value}) if (ref($value) eq q[ARRAY]);
			next if ($value eq q[]);
			is(CommandAttr(undef, qq[$name $attr $value]), U(), qq[$name attr $attr]);
		}

		foreach my $msg (@{$sc->{messages}}) {
			MQTT2_DEVICE_Parse($io, join(qq[\0], q[cid], @{$msg}));
		}
		foreach my $reading (sort keys %{$sc->{readings}}) {
			is(ReadingsVal($name, $reading, undef), $sc->{readings}{$reading}, qq[$name reading $reading]);
		}
		is($defs{$name}{STATE}, $sc->{STATE}, qq[$name STATE]) if (defined($sc->{STATE}));

		my @later = @{$sc->{later} // []};
		while (@later) {
			my ($msgs, $expected) = splice(@later, 0, 2);
			MQTT2_DEVICE_Parse($io, join(qq[\0], q[cid], @{$_})) foreach (@{$msgs});
			foreach my $reading (sort keys %{$expected}) {
				is(ReadingsVal($name, $reading, undef), $expected->{$reading},
					qq[$name reading $reading after ] . join(q[, ], map { $_->[1] } @{$msgs}));
			}
		}

		foreach my $set (@{$sc->{sets}}) {
			@published = ();
			is(CommandSet(undef, qq[$name $set->[0]]), U(), qq[set $name $set->[0]]);
			is(\@published, [$set->[1]], qq[set $name $set->[0] publishes]);
		}
	}

	done_testing();
	exit(0);
}, 0);

1;
