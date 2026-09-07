import bpy,sys,json
from pathlib import Path
root=Path(r'D:\Codex_Trans\Fo4 modding');sys.path.insert(0,str(root/'tools/deps/pynifly28'))
import io_scene_nifly,addon_utils
addon_utils.enable('io_scene_nifly',default_set=True,persistent=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'build/Doro_FO4_rigged.blend'))
bpy.ops.object.select_all(action='DESELECT')
rig=bpy.data.objects['Doro_YaoGuai_Rig'];rig.select_set(True)
for name in ['Doro_Face','Doro_Body','Doro_Hair']:
 o=bpy.data.objects[name]
 if 'pynRoot' in o:del o['pynRoot']
 o.shape_key_clear();o.select_set(True)
 o.data.materials[0]['BSLSP_Shader_Name']='Materials\\Actors\\Doro\\Doro.bgsm'
bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.pynifly(filepath=str(root/'build/DoroFollower/Meshes/Actors/Doro/Doro.nif'),target_game='FO4',rename_bones=False,rotate_bones_pretty=False,blender_xf=False,preserve_hierarchy=True,export_pose=False,export_modifiers=False,export_animations=False,write_tris=False,intuit_defaults=False)
bpy.ops.wm.save_as_mainfile(filepath=str(root/'build/Doro_FO4_rigged.blend'))
