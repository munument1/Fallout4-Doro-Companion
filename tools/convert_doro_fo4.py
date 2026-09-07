import bpy,sys,json,shutil
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(r'D:\Codex_Trans\Fo4 modding')
sys.path.insert(0,str(ROOT/'tools/deps/pynifly28'))
import io_scene_nifly
import addon_utils
addon_utils.enable('io_scene_nifly', default_set=True, persistent=True)
SRC=ROOT/'reference/skyrim_doro_source'
OUT=ROOT/'build/DoroFollower'
for p in ['Meshes/Actors/Doro','Textures/Actors/Doro','Materials/Actors/Doro','Sound/FX/Doro']:(OUT/p).mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SRC/'Skyrim_Doro_inspection.blend'))
# Only the three body asset shapes; the accessory is a separate wearable miniature.
report=json.loads((SRC/'model_inspection.json').read_text())
sources=[bpy.data.objects[r['name']] for r in report if r['source']=='EMBody.nif' and r['type']=='MESH']
for o in bpy.context.scene.objects:o.hide_set(True);o.hide_render=True
col=bpy.data.collections.new('Doro Fallout 4');bpy.context.scene.collection.children.link(col)
before=set(bpy.data.objects)
skel=Path(r'C:\Users\seung\OneDrive\Desktop\Meshes\Actors\YaoGuai\CharacterAssets\skeleton.nif')
bpy.ops.import_scene.pynifly(filepath=str(skel),rename_bones=False,rotate_bones_pretty=False,blender_xf=False,import_collisions=False,create_bones=True,reference_skel=str(skel),import_pose=False)
rig=next(o for o in set(bpy.data.objects)-before if o.type=='ARMATURE');rig.name='Doro_YaoGuai_Rig';rig.show_in_front=True;rig.hide_render=True
for extra in set(bpy.data.objects)-before:
 if extra != rig:extra.hide_render=True;extra.hide_set(True)
mapping={'HEAD':'HEAD','Neck':'Neck1','Pelvis':'Pelvis','Torso':'SPINE1','SpineLowerSpine':'SPINE1','SpineUpperSpine':'SPINE2'}
for s in ['L','R']:
 for a,b in {'Arm_Clavicle':'Leg_Front_Thigh','Arm_Upper':'Leg_Front_Thigh','Arm_Forearm':'Leg_Front_Knee','Arm_Palm':'Leg_Front_Ankle','Arm_Index1':'Leg_Front_Ankle','Leg1':'Leg_Rear_Thigh','Leg2':'Leg_Rear_Knee','Leg3':'Leg_Rear_Ankle','LegAnkle':'Leg_Rear_Ankle'}.items():mapping[s+a]=s+b
meshes=[];diagnostics=[]
for src in sources:
 o=src.copy();o.data=bpy.data.meshes.new_from_object(src.evaluated_get(bpy.context.evaluated_depsgraph_get()), preserve_all_data_layers=True, depsgraph=bpy.context.evaluated_depsgraph_get());col.objects.link(o);o.parent=None;o.matrix_world=Matrix.Identity(4);o.modifiers.clear();o.hide_set(False);o.hide_render=False
 o.name={'006':'Doro_Face','007':'Doro_Body','010':'Doro_Hair'}[src.name.split('.mo.')[1][:3]]
 # Retain the source silhouette; scale once into the YaoGuai asset coordinate range.
 for v in o.data.vertices:v.co=src.matrix_world@v.co;v.co*=2.15;v.co.z+=6.56
 original={g.index:g.name for g in o.vertex_groups}
 vw=[]
 for v in o.data.vertices:
  d={}
  for g in v.groups:
   name=mapping.get(original[g.group])
   if name:d[name]=d.get(name,0)+g.weight
  if not d:d={'HEAD':1} if o.name!='Doro_Body' else {'SPINE1':1}
  total=sum(d.values());vw.append({n:w/total for n,w in d.items()})
 o.vertex_groups.clear()
 groups={n:o.vertex_groups.new(name=n) for n in sorted({n for d in vw for n in d})}
 for i,d in enumerate(vw):
  for n,w in d.items():groups[n].add([i],w,'REPLACE')
 for k in list(o.keys()):del o[k]
 o['pynRoot']='BSFadeNode';o['PYN_GAME']='FO4'
 mod=o.modifiers.new('YaoGuai skin','ARMATURE');mod.object=rig
 for f in o.data.polygons:f.use_smooth=True
 meshes.append(o);diagnostics.append({'mesh':o.name,'vertices':len(o.data.vertices),'triangles':sum(len(p.vertices)-2 for p in o.data.polygons),'bone_groups':list(groups),'max_weight_sum_error':max(abs(sum(d.values())-1) for d in vw)})
texture=OUT/'Textures/Actors/Doro/Doro_d.dds';shutil.copy2(SRC/'Textures/SB_Doro/CH_NPC_Dororog_A.dds',texture)
for p in (SRC/'Sound/FX').glob('*.wav'):shutil.copy2(p,OUT/'Sound/FX/Doro'/p.name)
# New export material avoids inherited Skyrim shader flags.
m=bpy.data.materials.new('Materials/Actors/Doro/Doro.bgsm');m.use_nodes=True
n=m.node_tree.nodes;bs=n.get('Principled BSDF');tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(SRC/'Textures/SB_Doro/CH_NPC_Dororog_A.png'),check_existing=True)
m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=.75
for o in meshes:o.data.materials.clear();o.data.materials.append(m)
bpy.ops.object.select_all(action='DESELECT');rig.hide_set(False);rig.select_set(True)
for o in meshes:o.select_set(True)
bpy.context.view_layer.objects.active=rig
print('EXPORT_PROPS',[p.identifier for p in bpy.ops.export_scene.pynifly.get_rna_type().properties],flush=True)
status=bpy.ops.export_scene.pynifly(filepath=str(OUT/'Meshes/Actors/Doro/Doro.nif'),target_game='FO4',rename_bones=False,rotate_bones_pretty=False,blender_xf=False,preserve_hierarchy=True,export_pose=False,export_modifiers=False,write_tris=False,intuit_defaults=False)
print('NIF_EXPORT',status,flush=True)
(ROOT/'build/mesh_validation.json').write_text(json.dumps(diagnostics,indent=2))
# Render the rest pose and import an actual vanilla walk action for inspection.
scene=bpy.context.scene
for o in bpy.data.collections['STUDIO • preview only'].objects:
 o.hide_set(False);o.hide_render=False
 if o.type=='LIGHT':o.data.energy*=4
ground=bpy.data.objects['Studio floor'];ground.location.z=-.3
cam=scene.camera;cam.location=(225,310,180);cam.rotation_euler=(Vector((0,-8,74))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=240
scene.render.resolution_x=800;scene.render.resolution_y=800;scene.cycles.samples=24;scene.render.filepath=str(ROOT/'build/doro_fo4_rest.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'build/Doro_FO4_rigged.blend'))
bpy.ops.render.render(write_still=True)
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
hkx=skel.with_suffix('.hkx')
try:
 status=bpy.ops.import_scene.pynifly_hkx(filepath=str(skel.parent.parent/'Animations/WalkForward.hkx'),reference_skel=str(hkx),rename_bones=False,blender_xf=False,rotate_bones_pretty=False)
 print('WALK_IMPORT',status,flush=True)
 if rig.animation_data and rig.animation_data.action:
  act=rig.animation_data.action;print('WALK_ACTION',act.name,list(act.frame_range),flush=True)
  scene.frame_set(int((act.frame_range[0]+act.frame_range[1])/2));scene.render.filepath=str(ROOT/'build/doro_fo4_walk_mid.png');bpy.ops.render.render(write_still=True)
  bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'build/Doro_FO4_walk_test.blend'))
except Exception as e:print('WALK_ERROR',repr(e),flush=True)
print('CONVERSION_FINISHED',flush=True)

