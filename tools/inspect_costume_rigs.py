import bpy,sys,json
from pathlib import Path
r=Path(r'D:\Codex_Trans\Fo4 modding');sys.path.insert(0,str(r/'tools/deps/pynifly28'))
import addon_utils
addon_utils.enable('io_scene_nifly',default_set=True,persistent=True)
report={}
for name,p in [('dog',r/'reference/dogmeat/skeleton.nif'),('human',r/'reference/costumes/human_skeleton.nif')]:
 bpy.ops.object.select_all(action="DESELECT");bpy.context.view_layer.objects.active=None
 before=set(bpy.data.objects)
 bpy.ops.import_scene.pynifly(filepath=str(p),reference_skel=str(p),rename_bones=False,rotate_bones_pretty=False,blender_xf=False,import_collisions=False,import_pose=False,create_bones=True)
 rig=next(o for o in set(bpy.data.objects)-before if o.type=='ARMATURE')
 report[name]=[{'name':b.name,'head':list(b.head_local)} for b in rig.data.bones]
(r/'build/costume_bones.json').write_text(json.dumps(report,indent=2))
print('INSPECTED',flush=True)
