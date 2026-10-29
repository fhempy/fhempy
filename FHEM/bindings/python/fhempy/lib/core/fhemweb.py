"""Room and icons in FHEMWEB for modules which create a room of their own"""

from .. import fhem

SETUP_READING = ".room_setup"


async def setup_room(hash, room, room_icon, device_icon, keep_fhempy=False):
    """Once for a new device: put it into room, give it device_icon and the
    room room_icon in all FHEMWEB instances. Existing icons are kept, the
    user can change everything afterwards. keep_fhempy: stay in room fhempy
    too instead of moving from there."""
    name = hash["NAME"]
    if await fhem.ReadingsVal(name, SETUP_READING, "") == "done":
        return
    # fhempy puts new devices into room fhempy
    move = "" if keep_fhempy else " || $cur eq 'fhempy'"
    cmd = (
        f"my $n = {fhem.perlString(name)};"
        f" my $room = {fhem.perlString(room)};"
        " my $cur = AttrVal($n, 'room', '');"
        f" my $rooms = ($cur eq ''{move})"
        ' ? $room : "$cur,$room";'
        ' CommandAttr(undef, "$n room $rooms")'
        " if ((','.$cur.',') !~ /,\\Q$room\\E,/);"
        f" CommandAttr(undef, {fhem.perlString(name + ' icon ' + device_icon)})"
        " if (AttrVal($n, 'icon', '') eq '');"
        " foreach my $w (devspec2array('TYPE=FHEMWEB')) {"
        " next if ($defs{$w}{TEMPORARY});"
        " my $ri = AttrVal($w, 'roomIcons', '');"
        " next if ($ri =~ /(^|\\s)\\Q$room\\E:/);"
        " CommandAttr(undef, \"$w roomIcons \" . ($ri eq '' ? '' : \"$ri \")"
        f" . {fhem.perlString(room + ':' + room_icon)}) }}"
        " 'ok'"
    )
    await fhem.sendCommandHash(hash, cmd)
    await fhem.readingsSingleUpdate(hash, SETUP_READING, "done", 0)
