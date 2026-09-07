from pathlib import Path
import hashlib,json,zipfile,subprocess,sys

root=Path(__file__).resolve().parent.parent
follower=root/'build/DoroFollower'
costumes=root/'build/DoroCostumes'
out=root/'build/Doro_FO4_test_0.2.5.zip'

# Apply the approved companion profile immediately before packaging. The patch is
# intentionally idempotent so repeated local packaging cannot keep reducing damage.
# Development packages default to a normal/full ESP for compatibility with 0.2.4
# test saves. Set DORO_ESPFE=1 only for clean-save ESP-FE tests.
subprocess.check_call([sys.executable,str(root/'tools/apply_doro_combat_balance.py')])

pex=follower/'Scripts/DoroCompanionScript.pex'
if not pex.exists():
    raise FileNotFoundError(pex)
pex_bytes=pex.read_bytes()
# Refuse the stale 0.2.4 runtime. These markers are present in the new direct-menu,
# forced-retaliation PEX produced from tools/DoroCompanionScript.psc.
required_pex_markers=[
    b'Doro: command menu missing from DoroFollower.esp',
    b'OnCombatStateChanged',
    b'StartCombat',
    b'Show',
]
for marker in required_pex_markers:
    if marker not in pex_bytes:
        raise AssertionError(f'Stale/incorrect DoroCompanionScript.pex: missing {marker!r}')
if b'dialogue quest missing from ESP' in pex_bytes:
    raise AssertionError('Stale 0.2.4 DoroCompanionScript.pex detected')
if b'StopCombatAlarm' in pex_bytes:
    raise AssertionError('Pre-review Doro PEX detected: StopCombatAlarm must not be used')

# One plugin only: DoroFollower.esp contains follower, command runtime and costumes.
files={
    follower/'DoroFollower.esp':'DoroFollower.esp',
    pex:'Scripts/DoroCompanionScript.pex',
    follower/'Scripts/DoroDialogueQuestScript.pex':'Scripts/DoroDialogueQuestScript.pex',
    follower/'Meshes/Actors/Doro/Doro.nif':'Meshes/Actors/Doro/Doro.nif',
    follower/'Materials/Actors/Doro/Doro.bgsm':'Materials/Actors/Doro/Doro.bgsm',
    follower/'Textures/Actors/Doro/Doro_d.dds':'Textures/Actors/Doro/Doro_d.dds',
    follower/'Textures/Actors/Doro/Doro_n.dds':'Textures/Actors/Doro/Doro_n.dds',
    follower/'Textures/Actors/Doro/Doro_s.dds':'Textures/Actors/Doro/Doro_s.dds',
    follower/'Sound/FX/Doro/Doro01.wav':'Sound/FX/Doro/Doro01.wav',
    follower/'Sound/FX/Doro/Doro02.wav':'Sound/FX/Doro/Doro02.wav',
    costumes/'Meshes/Armor/DoroCostumes/DoroHelmet.nif':'Meshes/Armor/DoroCostumes/DoroHelmet.nif',
    costumes/'Meshes/Armor/DoroCostumes/DoroHelmetGO.nif':'Meshes/Armor/DoroCostumes/DoroHelmetGO.nif',
    costumes/'Meshes/Armor/DoroCostumes/DoroDogSuit.nif':'Meshes/Armor/DoroCostumes/DoroDogSuit.nif',
    root/'tools/DoroCompanionScript.psc':'Source/Scripts/DoroCompanionScript.psc',
    root/'tools/DoroDialogueQuestScript.psc':'Source/Scripts/DoroDialogueQuestScript.psc',
}

readme=follower/'README_KO.txt'
if readme.exists():
    files[readme]='README_KO.txt'

missing=[str(path) for path in files if not path.exists()]
if missing:
    raise FileNotFoundError('Missing build outputs:\n'+'\n'.join(missing))

manifest={}
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for src,dst in files.items():
        z.write(src,dst)
        manifest[dst]=hashlib.sha256(src.read_bytes()).hexdigest()
    z.writestr('SHA256.json',json.dumps(manifest,indent=2))

with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    names=z.namelist()
    assert names.count('DoroFollower.esp')==1
    assert not any(name.lower().endswith('.esp') and name!='DoroFollower.esp' for name in names)
    assert 'Scripts/DoroCompanionScript.pex' in names
    assert 'Scripts/DoroDialogueQuestScript.pex' in names
    assert 'Meshes/Armor/DoroCostumes/DoroHelmet.nif' in names
    assert 'Meshes/Armor/DoroCostumes/DoroDogSuit.nif' in names
    assert 'Source/Scripts/DoroCompanionScript.psc' in names
    packed_manifest=json.loads(z.read('SHA256.json'))
    for name,digest in packed_manifest.items():
        assert hashlib.sha256(z.read(name)).hexdigest()==digest, name

print('PACKAGE_OK_SINGLE_ESP',out,out.stat().st_size)
print('DORO_PEX_SHA256',hashlib.sha256(pex_bytes).hexdigest())
