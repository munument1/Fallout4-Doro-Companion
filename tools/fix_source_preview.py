import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path(r'D:\Codex_Trans\Fo4 modding\reference\skyrim_doro_source')
report=json.loads((root/'model_inspection.json').read_text())
objs=[bpy.data.objects[r['name']] for r in report if r['type']=='MESH' and r['source']=='EMBody.nif']
for r in report:
 if r['type']=='MESH' and r['source']!='EMBody.nif':bpy.data.objects[r['name']].hide_render=True
img=bpy.data.images.get('CH_NPC_Dororog_A.dds')
m=bpy.data.materials.new('Doro source texture preview');m.use_nodes=True
n=m.node_tree.nodes;bs=n.get('Principled BSDF');t=n.new('ShaderNodeTexImage');t.image=img
m.node_tree.links.new(t.outputs['Color'],bs.inputs['Base Color']);m.node_tree.links.new(t.outputs['Color'],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=.25;bs.inputs['Roughness'].default_value=.7
for o in objs:o.data.materials.clear();o.data.materials.append(m)
bounds=[o.matrix_world@Vector(c) for o in objs for c in o.bound_box];lo=Vector(tuple(min(p[i] for p in bounds) for i in range(3)));hi=Vector(tuple(max(p[i] for p in bounds) for i in range(3)));center=(lo+hi)/2
scene=bpy.context.scene;cam=scene.camera;cam.location=center+Vector((90,150,65));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=max(hi-lo)*1.6
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(root/'Skyrim_Doro_inspection.blend'))
