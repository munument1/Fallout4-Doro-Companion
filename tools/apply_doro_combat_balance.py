import os
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ESP = ROOT / 'build/DoroFollower/DoroFollower.esp'

DORO_RACE = 0x01000800
DORO_NPC = 0x01000803
DORO_REF = 0x0100080B
DORO_DIALOGUE_QUEST = 0x0100080C
DORO_HELMET = 0x01000840
DORO_HELMET_ARMA = 0x01000841
UNARMED_YAOGUAI = 0x000C2C38
UNARMED_DOGMEAT = 0x000C2C2B

# Development builds default to a normal/full ESP. 0.2.4 was a full ESP, and
# flipping the same plugin name to ESP-FE in an existing test save can invalidate
# saved references. Set DORO_ESPFE=1 only for clean-save light-plugin testing.
USE_ESPFE = os.environ.get('DORO_ESPFE', '0') == '1'


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
        yield sig.decode('ascii', 'replace'), fid, flags, i, i + 24, size
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
    return next(s for s in subrecords(buf, record[4], record[5]) if s[0] == sig)


def main():
    if not ESP.exists():
        raise FileNotFoundError(ESP)

    data = bytearray(ESP.read_bytes())
    records = list(iter_records(data))

    # Dogmeat-level base unarmed damage while retaining Doro's Yao Guai rig and animations.
    race = find_record(records, 'RACE', DORO_RACE)
    unwp = find_sub(data, race, 'UNWP')
    old_weapon = struct.unpack_from('<I', data, unwp[1])[0]
    if old_weapon not in (UNARMED_YAOGUAI, UNARMED_DOGMEAT):
        raise AssertionError(f'Unexpected Doro UNWP: {old_weapon:08X}')
    struct.pack_into('<I', data, unwp[1], UNARMED_DOGMEAT)

    # Companion balance: player-level scaling, moderate durability, essential preserved.
    npc = find_record(records, 'NPC_', DORO_NPC)
    acbs = find_sub(data, npc, 'ACBS')
    flags = struct.unpack_from('<I', data, acbs[1])[0] | 0x80  # PC Level Mult
    struct.pack_into('<I', data, acbs[1], flags)
    struct.pack_into('<H', data, acbs[1] + 6, 1000)  # 1.000x player level
    struct.pack_into('<H', data, acbs[1] + 8, 1)
    struct.pack_into('<H', data, acbs[1] + 10, 100)

    dnam = find_sub(data, npc, 'DNAM')
    struct.pack_into('<H', data, dnam[1], 275)       # health
    struct.pack_into('<H', data, dnam[1] + 2, 100)  # AP

    # Mascot head occupies only FO4 biped slot 30 (helmet/head) instead of 30+31+32.
    for fid in (DORO_HELMET, DORO_HELMET_ARMA):
        rec = find_record(records, 'ARMO' if fid == DORO_HELMET else 'ARMA', fid)
        bod2 = find_sub(data, rec, 'BOD2')
        struct.pack_into('<I', data, bod2[1], 1)

    # Keep the dialogue fix intact.
    quest = find_record(records, 'QUST', DORO_DIALOGUE_QUEST)
    qdnam = find_sub(data, quest, 'DNAM')
    quest_flags = struct.unpack_from('<H', data, qdnam[1])[0]
    assert quest_flags & 0x8000, 'Dialogue quest lost HasDialogueData'

    # Keep the original 0.2.4 placed reference intact.
    placed = find_record(records, 'ACHR', DORO_REF)
    name = find_sub(data, placed, 'NAME')
    assert struct.unpack_from('<I', data, name[1])[0] == DORO_NPC

    # Full ESP for existing-save development by default; ESP-FE only on clean-save tests.
    tes4 = find_record(records, 'TES4', 0)
    header_flags = struct.unpack_from('<I', data, tes4[3] + 8)[0]
    if USE_ESPFE:
        header_flags |= 0x200
    else:
        header_flags &= ~0x200
    struct.pack_into('<I', data, tes4[3] + 8, header_flags)

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

    for fid in (DORO_HELMET, DORO_HELMET_ARMA):
        rec = find_record(records, 'ARMO' if fid == DORO_HELMET else 'ARMA', fid)
        bod2 = find_sub(check, rec, 'BOD2')
        assert struct.unpack_from('<I', check, bod2[1])[0] == 1

    tes4 = find_record(records, 'TES4', 0)
    header_flags = struct.unpack_from('<I', check, tes4[3] + 8)[0]
    assert bool(header_flags & 0x200) == USE_ESPFE

    print('DORO_RUNTIME_PATCH_OK')
    print('UNWP=UnarmedDogmeat[000C2C2B] base damage 25')
    print('PC_LEVEL_MULT=1.0 MIN=1 MAX=100 HEALTH=275 AP=100 ESSENTIAL=kept')
    print('HELMET_SLOT=30_ONLY BOD2=1')
    print('PLUGIN_TYPE=' + ('ESP-FE' if USE_ESPFE else 'FULL_ESP'))


if __name__ == '__main__':
    main()
