from pathlib import Path
import zipfile,hashlib,json
r=Path(__file__).resolve().parent.parent;out=r/'build/DoroFollower'
files=['DoroFollower.esp','Scripts/DoroCompanionScript.pex','Scripts/DoroDialogueQuestScript.pex','Meshes/Actors/Doro/Doro.nif','Materials/Actors/Doro/Doro.bgsm','Textures/Actors/Doro/Doro_d.dds','Textures/Actors/Doro/Doro_n.dds','Textures/Actors/Doro/Doro_s.dds','Sound/FX/Doro/Doro01.wav','Sound/FX/Doro/Doro02.wav','README_KO.txt']
zpath=r/'build/DoroFollower_FO4_test_0.2.zip'
manifest={}
with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED) as z:
 for f in files:
  p=out/f;z.write(p,f);manifest[f]=hashlib.sha256(p.read_bytes()).hexdigest()
 for f in ['DoroCompanionScript.psc','DoroDialogueQuestScript.psc']:z.write(r/'tools'/f,'Source/Scripts/'+f)
 z.write(r/'build/verification_0.2.json','verification_0.2.json')
 z.writestr('SHA256.json',json.dumps(manifest,indent=2))
with zipfile.ZipFile(zpath) as z:
 assert z.testzip() is None
 assert len(z.namelist())==15
print(zpath,zpath.stat().st_size)
