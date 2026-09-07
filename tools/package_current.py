from pathlib import Path
import hashlib,json,zipfile

root=Path(__file__).resolve().parent.parent
follower=root/'build/DoroFollower'
costumes=root/'build/DoroCostumes'
out=root/'build/Doro_FO4_test_0.2.5.zip'

# One plugin only: DoroFollower.esp contains follower, dialogue and all costume recipes.
files={
    follower/'DoroFollower.esp':'DoroFollower.esp',
    follower/'Scripts/DoroCompanionScript.pex':'Scripts/DoroCompanionScript.pex',
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
    for src,dst in [
        (root/'tools/DoroCompanionScript.psc','Source/Scripts/DoroCompanionScript.psc'),
        (root/'tools/DoroDialogueQuestScript.psc','Source/Scripts/DoroDialogueQuestScript.psc'),
    ]:
        z.write(src,dst)
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

print('PACKAGE_OK_SINGLE_ESP_FE',out,out.stat().st_size)
