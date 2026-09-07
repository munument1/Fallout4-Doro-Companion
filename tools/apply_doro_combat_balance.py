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
DORO_PACKAGES = (0x01000806, 0x01000807, 0x01000808, 0x0100082A)
DORO_MENU = 0x01000805
UNARMED_YAOGUAI = 0x000C2C38

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
    if i != end:
        raise AssertionError(f'ESP record walk ended at {i}, expected {end}')


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
    if i != end:
        raise AssertionError(f'Subrecord walk ended at {i}, expected {end}')


def find_record(records, sig, fid):
    return next(r for r in records if r[0] == sig and r[1] == fid)


def find_sub(buf, record, sig):
    return next(s for s in subrecords(buf, record[4], record[5]) if s[0] == sig)


def all_subs(buf, record, sig):
    return [s for s in subrecords(buf, record[4], record[5]) if s[0] == sig]


def main():
    if not ESP.exists():
        raise FileNotFoundError(ESP)

    data = bytearray(ESP.read_bytes())
    records = list(iter_records(data))

    # Doro keeps Yao Guai combat animation compatibility. Damage is reduced by
    # scaling the race ATKD multipliers, not by substituting Dogmeat's weapon.
    race = find_record(records, 'RACE', DORO_RACE)
    unwp = find_sub(data, race, 'UNWP')
    struct.pack_into('<I', data, unwp[1], UNARMED_YAOGUAI)

    race_data = find_sub(data, race, 'DATA')
    race_flags = struct.unpack_from('<I', data, race_data[1] + 32)[0]
    race_flags &= ~(1 << 20)  # Can't Open Doors
    race_flags |= 1 << 21     # Allow PC Dialogue
    struct.pack_into('<I', data, race_data[1] + 32, race_flags)
    struct.pack_into('<I', data, race_data[1] + 44, 1)  # Medium pathing size

    attacks = all_subs(data, race, 'ATKD')
    if not attacks:
        raise AssertionError('DoroRace has no ATKD attack data')
    multipliers = [struct.unpack_from('<f', data, s[1])[0] for s in attacks]
    # Generated Yao Guai records contain 1.0/0.1-style donor values. Scale once.
    # A second packaging pass must not scale the already-balanced 0.25/0.025 values again.
    if any(value > 0.250001 for value in multipliers):
        for s in attacks:
            value = struct.unpack_from('<f', data, s[1])[0]
            struct.pack_into('<f', data, s[1], value * 0.25)

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

    aidt = find_sub(data, npc, 'AIDT')
    data[aidt[1]] = 2      # Very Aggressive
    data[aidt[1] + 5] = 2  # Helps Friends and Allies

    # Ensure follower/home/dialogue packages never suppress combat.
    for fid in DORO_PACKAGES:
        package = find_record(records, 'PACK', fid)
        pkdt = find_sub(data, package, 'PKDT')
        package_flags = struct.unpack_from('<I', data, pkdt[1])[0] & ~(1 << 20)
        struct.pack_into('<I', data, pkdt[1], package_flags)

    # Mascot head occupies only FO4 biped slot 30 (helmet/head).
    for fid in (DORO_HELMET, DORO_HELMET_ARMA):
        rec = find_record(records, 'ARMO' if fid == DORO_HELMET else 'ARMA', fid)
        bod2 = find_sub(data, rec, 'BOD2')
        struct.pack_into('<I', data, bod2[1], 1)

    # Shrink the placed actor controller enough for ordinary interior navigation.
    placed = find_record(records, 'ACHR', DORO_REF)
    name = find_sub(data, placed, 'NAME')
    assert struct.unpack_from('<I', data, name[1])[0] == DORO_NPC
    xscl = find_sub(data, placed, 'XSCL')
    struct.pack_into('<f', data, xscl[1], 0.42)

    # Keep the legacy dialogue data structurally valid even though current runtime
    # activation uses the script-driven command menu instead of native Greeting.
    quest = find_record(records, 'QUST', DORO_DIALOGUE_QUEST)
    qdnam = find_sub(data, quest, 'DNAM')
    quest_flags = struct.unpack_from('<H', data, qdnam[1])[0]
    assert quest_flags & 0x8000, 'Dialogue quest lost HasDialogueData'

    menu = find_record(records, 'MESG', DORO_MENU)
    menu_dnam = find_sub(data, menu, 'DNAM')
    assert struct.unpack_from('<I', data, menu_dnam[1])[0] & 1, 'DoroCommandMenu is not a Message Box'
    assert len(all_subs(data, menu, 'ITXT')) == 5, 'DoroCommandMenu must contain five buttons'

    vmad = find_sub(data, npc, 'VMAD')
    assert b'DoroCompanionScript' in data[vmad[1]:vmad[1] + vmad[2]], 'NPC lost DoroCompanionScript VMAD'

    # Full ESP for existing-save development by default; ESP-FE only on clean-save tests.
    tes4 = find_record(records, 'TES4', 0)
    header_flags = struct.unpack_from('<I', data, tes4[3] + 8)[0]
    if USE_ESPFE:
        header_flags |= 0x200
    else:
        header_flags &= ~0x200
    struct.pack_into('<I', data, tes4[3] + 8, header_flags)

    ESP.write_bytes(data)

    # Full post-write validation.
    check = bytearray(ESP.read_bytes())
    records = list(iter_records(check))
    form_ids = [r[1] for r in records]
    assert len(form_ids) == len(set(form_ids)), 'Duplicate FormID detected'

    tes4 = find_record(records, 'TES4', 0)
    hedr = find_sub(check, tes4, 'HEDR')
    _version, declared_count, _next_id = struct.unpack_from('<fII', check, hedr[1])
    assert declared_count == len(records) - 1, (declared_count, len(records) - 1)

    race = find_record(records, 'RACE', DORO_RACE)
    unwp = find_sub(check, race, 'UNWP')
    assert struct.unpack_from('<I', check, unwp[1])[0] == UNARMED_YAOGUAI
    race_data = find_sub(check, race, 'DATA')
    race_flags = struct.unpack_from('<I', check, race_data[1] + 32)[0]
    assert not (race_flags & (1 << 20))
    assert race_flags & (1 << 21)
    assert struct.unpack_from('<I', check, race_data[1] + 44)[0] == 1
    attack_mults = [struct.unpack_from('<f', check, s[1])[0] for s in all_subs(check, race, 'ATKD')]
    assert attack_mults and max(attack_mults) <= 0.250001

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
    aidt = find_sub(check, npc, 'AIDT')
    assert check[aidt[1]] == 2 and check[aidt[1] + 5] == 2

    for fid in DORO_PACKAGES:
        package = find_record(records, 'PACK', fid)
        pkdt = find_sub(check, package, 'PKDT')
        assert not (struct.unpack_from('<I', check, pkdt[1])[0] & (1 << 20))

    for fid in (DORO_HELMET, DORO_HELMET_ARMA):
        rec = find_record(records, 'ARMO' if fid == DORO_HELMET else 'ARMA', fid)
        bod2 = find_sub(check, rec, 'BOD2')
        assert struct.unpack_from('<I', check, bod2[1])[0] == 1

    placed = find_record(records, 'ACHR', DORO_REF)
    xscl = find_sub(check, placed, 'XSCL')
    assert abs(struct.unpack_from('<f', check, xscl[1])[0] - 0.42) < 1e-6

    header_flags = struct.unpack_from('<I', check, tes4[3] + 8)[0]
    assert bool(header_flags & 0x200) == USE_ESPFE

    print('DORO_RUNTIME_PATCH_OK')
    print('UNWP=UnarmedYaoGuai[000C2C38] ATKD_MAX<=0.25')
    print('RACE_SIZE=MEDIUM CANT_OPEN_DOORS=OFF ALLOW_PC_DIALOGUE=ON')
    print('AI=VERY_AGGRESSIVE ASSIST=FRIENDS_AND_ALLIES PACK_IGNORE_COMBAT=OFF')
    print('PC_LEVEL_MULT=1.0 MIN=1 MAX=100 HEALTH=275 AP=100 ESSENTIAL=kept')
    print('PLACED_SCALE=0.42 HELMET_SLOT=30_ONLY')
    print('PLUGIN_TYPE=' + ('ESP-FE' if USE_ESPFE else 'FULL_ESP'))


if __name__ == '__main__':
    main()
