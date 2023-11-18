#!/usr/bin/env perl
use strict;
use warnings;
use File::Basename;

use Test2::V0;
use Test2::Tools::Compare qw{ is };

my $module = basename (dirname(__FILE__));

plan(1);
is(CommandReload(undef,$module), U(), "$module loaded");

exit(0);  # necessary

1;

