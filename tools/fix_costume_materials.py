import bpy,sys,json
from pathlib import Path
r=Path(r'D:\Codex_Trans\Fo4 modding');sys.path.insert(0,str(r/'tools/deps/pynifly28'))
from io_scene_nifly.pyn.pynifly import NifFile
from io_scene_nifly.pyn.niflydll import nifly_path
NifFile.Load(nifly_path)
report=[]
for p in (r/'build/DoroCostumes/Meshes/Armor/DoroCostumes').glob('*.nif'):
 n=NifFile(str(p))
 for shape in n.shapes:
  shape.shader.name='Materials\\Actors\\Doro\\Doro.bgsm'
  for kind,file in [('Diffuse','Doro_d.dds'),('Normal','Doro_n.dds'),('Specular','Doro_s.dds')]:shape.set_texture(kind,'Textures\\Actors\\Doro\\'+file)
 n.save()
 report.append({'file':p.name,'shapes':len(n.shapes),'vertices':sum(len(s.verts) for s in n.shapes)})
(r/'build/costume_mesh_validation.json').write_text(json.dumps(report,indent=2));print(report)
