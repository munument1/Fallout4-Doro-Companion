"""Read-only audit of the supplied test14 archive's extracted files and vanilla assets."""
from pathlib import Path
import collections, hashlib, json, re, struct
from fo4_records import records, subs, edid, GAME

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'reference/test14_review'

def nif_blocks(path):
    data = Path(path).read_bytes()
    pos = data.index(b'\n') + 1
    version, endian, user, count, bs = struct.unpack_from('<IBIII', data, pos)
    assert (version, endian, user, bs) == (0x14020007, 1, 12, 130)
    pos += 17
    for _ in range(4):
        n = data[pos]; pos += n + 1
    ntypes = struct.unpack_from('<H', data, pos)[0]; pos += 2
    types = []
    for _ in range(ntypes):
        n = struct.unpack_from('<I', data, pos)[0]; pos += 4
        types.append(data[pos:pos+n].decode()); pos += n
    indices = struct.unpack_from(f'<{count}H', data, pos); pos += count*2
    sizes = struct.unpack_from(f'<{count}I', data, pos); pos += count*4
    nstrings, _ = struct.unpack_from('<II', data, pos); pos += 8
    strings = []
    for _ in range(nstrings):
        n = struct.unpack_from('<I', data, pos)[0]; pos += 4
        strings.append(data[pos:pos+n].decode(errors='replace')); pos += n
    groups = struct.unpack_from('<I', data, pos)[0]; pos += 4 + groups*4
    result = []
    for i, (index, size) in enumerate(zip(indices, sizes)):
        b = data[pos:pos+size]; pos += size
        row = {'block': i, 'type': types[index], 'size': size}
        if types[index] == 'NiNode':
            name, extras = struct.unpack_from('<II', b)
            row['name'] = strings[name] if name != 0xffffffff else ''
            # FO4 NiAVObject: controller, 32-bit flags, translation, rotation, scale, collision.
            start = 8 + 4*extras
            row['translation'] = struct.unpack_from('<3f', b, start+8)
            row['scale'] = struct.unpack_from('<f', b, start+56)[0]
            row['collision'] = struct.unpack_from('<I', b, start+60)[0]
        elif types[index] == 'BSBound':
            row['center'] = struct.unpack_from('<3f', b, 4)
            row['dimensions'] = struct.unpack_from('<3f', b, 16)
        elif types[index] == 'bhkNPCollisionObject':
            row['raw_hex'] = b.hex()
            row['target'], row['flags'], row['data'], row['body_id'] = struct.unpack('<IHII', b)
        elif types[index] in ('bhkPhysicsSystem', 'bhkRagdollSystem'):
            row['havok_strings'] = [x.decode() for x in re.findall(rb'[A-Za-z_][A-Za-z0-9_:]{5,}', b) if b'hk' in x or b'Character' in x]
        result.append(row)
    assert pos + 8 == len(data), (pos, len(data))
    return {'sha256': hashlib.sha256(data).hexdigest(), 'block_counts': dict(collections.Counter(x['type'] for x in result)), 'blocks': result}

def main():
    report = {'ingame_tested': False}
    rows = list(records(SRC/'DoroFollower.esp'))
    doro = {fid: (typ, list(subs(body))) for typ,fid,flags,body in rows}
    wanted = {0xa0f2f,0xa0f33,0xb3d81,0x27075,0x1c21c,0x337f3,0x106c30,0x106c31,0x68043}
    vanilla = {fid:(typ,list(subs(body))) for typ,fid,flags,body in records(GAME/'Data/Fallout4.esm') if fid in wanted}
    report['form_id_resolution'] = {f'{fid:08X}': {'type':typ,'editor_id':dict(ss).get('EDID',b'').rstrip(b'\0').decode(errors='replace')} for fid,(typ,ss) in vanilla.items()}
    report['record_count'] = len(rows)
    report['header_flags'] = rows[0][2]
    report['manifest_checks'] = {}
    manifest = json.loads((SRC/'SHA256.json').read_text(encoding='utf-8-sig'))
    for name, digest in manifest.items():
        p = SRC / name
        report['manifest_checks'][name] = p.exists() and hashlib.sha256(p.read_bytes()).hexdigest().lower() == str(digest).lower()
    original = vanilla[0xa0f2f][1]; current = doro[0x1000800][1]
    assert len(original) == len(current)
    report['race_diff'] = [{'index':i,'subrecord':s,'original':a.hex(),'test14':b.hex()} for i,((s,a),(t,b)) in enumerate(zip(original,current)) if (s,a)!=(t,b)]
    report['attack_events'] = [b.rstrip(b'\0').decode() for s,b in current if s=='ATKE']
    report['race_height'] = struct.unpack_from('<2f',dict(current)['DATA'])
    report['race_flags'] = hex(struct.unpack_from('<I',dict(current)['DATA'],32)[0])
    report['race_flags2'] = hex(struct.unpack_from('<I',dict(current)['DATA'],88)[0])
    for fid in [0x1000803,0x1000806,0x1000807,0x1000808,0x100080b]:
        report[f'{fid:08X}'] = [(s,b.hex()) for s,b in doro[fid][1]]
    report['vanilla_template'] = [(s,b.hex()) for s,b in vanilla[0xa0f33][1] if s in ['ATKR','TPLT','TPTA','ACBS','CNAM','RNAM']]
    report['wearables'] = [{'id':f'{fid:08X}','type':t,'name':dict(ss).get('EDID',b'').rstrip(b'\0').decode(),'BOD2':dict(ss).get('BOD2',b'').hex()} for fid,(t,ss) in doro.items() if t in ['ARMO','ARMA','COBJ']]
    report['nifs'] = {name:nif_blocks(path) for name,path in {
        'yaoguai_skeleton':Path('C:/Users/seung/OneDrive/Desktop/Meshes/Actors/YaoGuai/CharacterAssets/skeleton.nif'),
        'doro_mesh':SRC/'Meshes/Actors/Doro/Doro.nif',
        'dogmeat_skeleton':ROOT/'reference/dogmeat/skeleton.nif',
    }.items()}
    dest=ROOT/'build/test14_verification.json'
    dest.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('Report:',dest)
    print('Manifest:',report['manifest_checks'])
    print('Forms:',report['form_id_resolution'])
    print('Wearables:',report['wearables'])
    print('Template:',report['vanilla_template'])
    for name, data in report['nifs'].items():
        print(name,data['block_counts'])
        for block in data['blocks']:
            if block.get('name') in ('CharacterController','CharacterBumper') or block['type'] in ('BSBound','bhkPhysicsSystem'):
                print(block)

if __name__ == '__main__':
    main()
