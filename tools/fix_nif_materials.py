import bpy,sys,json
from pathlib import Path
r=Path(r'D:\Codex_Trans\Fo4 modding');sys.path.insert(0,str(r/'tools/deps/pynifly28'))
from io_scene_nifly.pyn.pynifly import NifFile
from io_scene_nifly.pyn.niflydll import nifly_path
NifFile.Load(nifly_path)
p=r/'build/DoroFollower/Meshes/Actors/Doro/Doro.nif';n=NifFile(str(p))
print('GAME',n.game)
result=[]
for s in n.shapes:
 s.shader.name='Materials\\Actors\\Doro\\Doro.bgsm'
 s.set_texture('Diffuse','Textures\\Actors\\Doro\\Doro_d.dds')
 s.set_texture('Normal','Textures\\Actors\\Doro\\Doro_n.dds')
 s.set_texture('Specular','Textures\\Actors\\Doro\\Doro_s.dds')
 item={'name':s.name,'block':s.blockname,'vertices':len(s.verts),'bones':s.bone_names,'material':s.shader.name,'partitions':[str(p) for p in s.partitions]}
 result.append(item)
n.save()
(r/'build/nif_validation.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
