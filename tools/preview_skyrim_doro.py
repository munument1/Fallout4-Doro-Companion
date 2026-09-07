import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path(r'D:\Codex_Trans\Fo4 modding\reference\skyrim_doro_source')
report=json.loads((root/'model_inspection.json').read_text())
objs=[bpy.data.objects[r['name']] for r in report if r['type']=='MESH']
img=bpy.data.images.load(str(root/'Textures/SB_Doro/CH_NPC_Dororog_A.dds'),check_existing=True)
print('TEXTURE',img.size[:])
for o in objs:
 for m in o.data.materials:
  if not m:continue
  m.use_nodes=True;n=m.node_tree.nodes;bs=n.get('Principled BSDF')
  if bs:
   tex=n.new('ShaderNodeTexImage');tex.image=img;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=.65
bounds=[o.matrix_world@Vector(c) for o in objs for c in o.bound_box]
lo=Vector(tuple(min(p[i] for p in bounds) for i in range(3)));hi=Vector(tuple(max(p[i] for p in bounds) for i in range(3)));center=(lo+hi)/2
scene=bpy.context.scene
for o in bpy.data.collections['STUDIO • preview only'].objects:
 o.hide_set(False);o.hide_render=False
 if o.type=='LIGHT':o.data.energy*=.25
floor=bpy.data.objects.get('Studio floor');floor.location.z=lo.z-.3
cam=scene.camera;cam.location=center+Vector((110,-155,75));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=max(hi-lo)*1.65
scene.render.resolution_x=800;scene.render.resolution_y=800;scene.cycles.samples=24;scene.render.filepath=str(root/'skyrim_doro_preview.png')
print('BOUNDS',list(lo),list(hi))
bpy.ops.wm.save_as_mainfile(filepath=str(root/'Skyrim_Doro_inspection.blend'))
bpy.ops.render.render(write_still=True)
