#!/usr/bin/env perl
use strict;
use warnings;
use Test2::V0;
use Test2::Tools::Compare qw{is like};
# reference implementation, only used by this test
use Protocol::WebSocket::Frame;
use Encode;

is(CommandReload(undef, "10_BindingsIo"), U(), "10_BindingsIo loaded");

sub frames_of {
  my ($hash) = @_;
  my @frames;
  while (my ($opcode, $payload) = BindingsIo_wsNextFrame($hash)) {
    push(@frames, [$opcode, $payload]);
  }
  return @frames;
}

sub new_hash {
  my $hash = { NAME => "wsTest" };
  BindingsIo_initFrame($hash);
  return $hash;
}

subtest 'text frame received byte by byte' => sub {
  my $hash = new_hash();
  my $json = Encode::encode('UTF-8', qq[{"msgtype":"version","version":"0.1.777","text":"\x{e4}\x{f6}\x{fc}"}]);
  my $bytes = Protocol::WebSocket::Frame->new(buffer => $json, type => 'text')->to_bytes;
  my @frames;
  foreach my $byte (split(//, $bytes)) {
    $hash->{".wsBuffer"} .= $byte;
    push(@frames, frames_of($hash));
  }
  is(scalar(@frames), 1, "one frame");
  is($frames[0][0], 1, "text frame");
  is($frames[0][1], $json, "payload");
  is($hash->{".wsBuffer"}, "", "buffer empty");
};

subtest 'several frames and payload lengths at once' => sub {
  my $hash = new_hash();
  my @payloads = ("a", "b" x 125, "c" x 126, "d" x 65535, "e" x 65536, "f" x 200000);
  $hash->{".wsBuffer"} = join("", map {
    Protocol::WebSocket::Frame->new(buffer => $_, type => 'text', max_payload_size => 0)->to_bytes
  } @payloads);
  my @frames = frames_of($hash);
  is([map { $_->[1] } @frames], \@payloads, "all payloads");
};

subtest 'masked frames are unmasked' => sub {
  my $hash = new_hash();
  $hash->{".wsBuffer"} = Protocol::WebSocket::Frame->new(buffer => "masked", masked => 1)->to_bytes;
  is([frames_of($hash)], [[1, "masked"]], "payload unmasked");
};

subtest 'fragmented message with a ping in between' => sub {
  my $hash = new_hash();
  $hash->{".wsBuffer"} =
    Protocol::WebSocket::Frame->new(buffer => "part1-", type => 'text', fin => 0)->to_bytes.
    Protocol::WebSocket::Frame->new(buffer => "ping", type => 'ping')->to_bytes.
    Protocol::WebSocket::Frame->new(buffer => "part2-", type => 'continuation', fin => 0)->to_bytes.
    Protocol::WebSocket::Frame->new(buffer => "part3", type => 'continuation', fin => 1)->to_bytes;
  is([frames_of($hash)], [[9, "ping"], [1, "part1-part2-part3"]], "ping first, then the whole message");
};

subtest 'control frames' => sub {
  my $hash = new_hash();
  $hash->{".wsBuffer"} =
    Protocol::WebSocket::Frame->new(buffer => "fhem", type => 'pong')->to_bytes.
    Protocol::WebSocket::Frame->new(buffer => pack("n", 1000), type => 'close')->to_bytes;
  is([frames_of($hash)], [[10, "fhem"], [8, pack("n", 1000)]], "pong and close");
};

subtest 'frames sent by FHEM' => sub {
  foreach my $case ([0x9, "fhem", "is_ping"], [0x1, "x" x 300, "is_text"], [0x2, "y" x 70000, "is_binary"], [0x2, "", "is_binary"]) {
    my ($opcode, $payload, $check) = @$case;
    my $bytes = BindingsIo_wsFrame($opcode, $payload);
    my $frame = Protocol::WebSocket::Frame->new(max_payload_size => 0);
    $frame->append($bytes);
    my $received = $frame->next_bytes;
    is($received, $payload, "payload of $check with ".length($payload)." bytes");
    ok($frame->$check, $check);
    ok($frame->masked, "masked");
  }
};

done_testing();
exit(0);

1;
