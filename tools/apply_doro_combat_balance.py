import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ESP = ROOT / 'build/DoroFollower/DoroFollower.esp'

DORO_RACE = 0x01000800
DORO_NPC = 0x01000803
UNARMED_YAOGUAI = 0x000C2C38
UNARMED_DOGMEAT = 0x000C2C2B


def iter_records(buf, start=0, end=None):
    if end is None:
        end = len(buf)
    i = start
    while i + 24 <= end:
        sig = buf[i:i + 4]
        if sig == b'GRUP':
            size = struct.unpack_from('<I', buf, i + 4)[0]
            yield from iter_records(buf, i + 24, i + size)
            i += size
            continue
        size = struct.unpack_from('<I', buf, i + 4)[0]
        flags = struct.unpack_from('<I', buf, i + 8)[0]
        fid = struct.unpack_from('<I', buf, i + 12)[0]
        yield sig.decode('ascii', 'replace'), fid, flags, i + 24, size
        i += 24 + size


def subrecords(buf, body_start, body_size):
    i = body_start
    end = body_start + body_size
    ext_size = None
    while i + 6 <= end:
        sig = buf[i:i + 4].decode('ascii', 'replace')
        size = struct.unpack_from('<H', buf, i + 4)[0]
        data_start = i + 6
        if sig == 'XXXX':
            ext_size = struct.unpack_from('<I', buf, data_start)[0]
            i = data_start + size
            continue
        if ext_size is not None:
            size = ext_size
            ext_size = None
        yield sig, data_start, size
        i = data_start + size


def find_record(records, sig, fid):
    return next(r for r in records if r[0] == sig and r[1] == fid)


def find_sub(buf, record, sig):
    return next(s for s in subrecords(buf, record[3], record[4]) if s[0] == sig)


def main():
    if not ESP.exists():
        raise FileNotFoundError(ESP)

    data = bytearray(ESP.read_bytes())
    records = list(iter_records(data))

    race = find_record(records, 'RACE', DORO_RACE)
    unwp = find_sub(data, race, 'UNWP')
    old_weapon = struct.unpack_from('<I', data, unwp[1])[0]
    if old_weapon not in (UNARMED_YAOGUAI, UNARMED_DOGMEAT):
        raise AssertionError(f'Unexpected Doro UNWP: {old_weapon:08X}')
    struct.pack_into('<I', data, unwp[1], UNARMED_DOGMEAT)

    npc = find_record(records, 'NPC_', DORO_NPC)
    acbs = find_sub(data, npc, 'ACBS')
    flags = struct.unpack_from('<I', data, acbs[1])[0] | 0x80  # PC Level Mult
    struct.pack_into('<I', data, acbs[1], flags)
    struct.pack_into('<H', data, acbs[1] + 6, 1000)  # 1.000x player level
    struct.pack_into('<H', data, acbs[1] + 8, 1)
    struct.pack_into('<H', data, acbs[1] + 10, 100)

    dnam = find_sub(data, npc, 'DNAM')
    struct.pack_into('<H', data, dnam[1], 275)      # health
    struct.pack_into('<H', data, dnam[1] + 2, 100)  # AP

    # Keep the previously fixed dialogue and light-plugin flags intact.
    tes4 = find_record(records, 'TES4', 0)
    assert tes4[2] & 0x200, 'DoroFollower.esp lost its ESL flag'

    quest = find_record(records, 'QUST', 0x0100080C)
    qdnam = find_sub(data, quest, 'DNAM')
    quest_flags = struct.unpack_from('<H', data, qdnam[1])[0]
    assert quest_flags & 0x8000, 'Dialogue quest lost HasDialogueData'

    ESP.write_bytes(data)

    # Verify written values.
    check = bytearray(ESP.read_bytes())
    records = list(iter_records(check))
    race = find_record(records, 'RACE', DORO_RACE)
    unwp = find_sub(check, race, 'UNWP')
    assert struct.unpack_from('<I', check, unwp[1])[0] == UNARMED_DOGMEAT

    npc = find_record(records, 'NPC_', DORO_NPC)
    acbs = find_sub(check, npc, 'ACBS')
    flags = struct.unpack_from('<I', check, acbs[1])[0]
    level_mult = struct.unpack_from('<H', check, acbs[1] + 6)[0]
    min_level = struct.unpack_from('<H', check, acbs[1] + 8)[0]
    max_level = struct.unpack_from('<H', check, acbs[1] + 10)[0]
    assert flags & 0x80
    assert (level_mult, min_level, max_level) == (1000, 1, 100)

    dnam = find_sub(check, npc, 'DNAM')
    assert struct.unpack_from('<HH', check, dnam[1]) == (275, 100)

    print('DORO_COMBAT_BALANCE_OK')
    print('UNWP=UnarmedDogmeat[000C2C2B] base damage 25')
    print('PC_LEVEL_MULT=1.0 MIN=1 MAX=100 HEALTH=275 AP=100 ESSENTIAL=kept')


if __name__ == '__main__':
    main()
