import bpy,sys,json,collections,math
from pathlib import Path
from mathutils import Vector
r=Path(r'D:\Codex_Trans\Fo4 modding');sys.path.insert(0,str(r/'tools/deps/pynifly28'))
import addon_utils
addon_utils.enable('io_scene_nifly',default_set=True,persistent=True)
bpy.ops.wm.open_mainfile(filepath=str(r/'build/DoroCostumes.blend'))
for o in bpy.context.scene.objects:
 if o.type in ['MESH','ARMATURE']:o.hide_set(True);o.hide_render=True
bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=None
before=set(bpy.data.objects);sk=r/'reference/dogmeat/skeleton.nif'
bpy.ops.import_scene.pynifly(filepath=str(r/'build/DoroCostumes/Meshes/Armor/DoroCostumes/DoroDogSuit.nif'),reference_skel=str(sk),rename_bones=False,rotate_bones_pretty=False,blender_xf=False,import_pose=False,import_collisions=False)
new=set(bpy.data.objects)-before;rig=next(o for o in new if o.type=='ARMATURE');meshes=[o for o in new if o.type=='MESH'];assert len(meshes)==3
mat=bpy.data.materials.get('Doro source texture preview')
for o in meshes:o.data.materials.clear();o.data.materials.append(mat)
scene=bpy.context.scene;floor=bpy.data.objects['Studio floor'];floor.hide_set(False);floor.hide_render=False;floor.location.z=-.3
scene.camera.location=(130,160,110);scene.camera.rotation_euler=(Vector((0,-10,43))-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=145
scene.render.resolution_x=512;scene.render.resolution_y=512;scene.cycles.samples=16
out=r/'build/costume_qa';out.mkdir(exist_ok=True)
scene.render.filepath=str(out/'dog_rest.png');bpy.ops.render.render(write_still=True)
seams=[]
for o in meshes:
 groups=collections.defaultdict(list)
 for v in o.data.vertices:groups[tuple(round(x,3) for x in v.co)].append(v.index)
 seams.extend((o,ids) for ids in groups.values() if len(ids)>1)
checks=[]
for action in ['walkforward','runforward']:
 bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
 bpy.ops.import_scene.pynifly_hkx(filepath=str(r/'reference/costumes'/(action+'.hkx')),reference_skel=str(r/'reference/costumes/skeleton.hkx'),rename_bones=False,rotate_bones_pretty=False,blender_xf=False)
 act=rig.animation_data.action;a,b=act.frame_range;gap=0.
 for frame in range(int(a),int(b)+1):
  scene.frame_set(frame);dg=bpy.context.evaluated_depsgraph_get()
  for o,ids in seams:
   vs=o.evaluated_get(dg).data.vertices;gap=max(gap,max((vs[i].co-vs[ids[0]].co).length for i in ids))
 assert gap<.001,(action,gap)
 for i in range(6):
  scene.frame_set(round(a+(b-a)*i/5));scene.render.filepath=str(out/f'{action}_{i}.png');bpy.ops.render.render(write_still=True)
 checks.append({'action':action,'frames':int(b-a+1),'seam_gap_max':gap})
# Reimport helmet against human skeleton, then exercise head rotations.
for o in new:o.hide_set(True);o.hide_render=True
bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=None;before=set(bpy.data.objects)
bpy.ops.import_scene.pynifly(filepath=str(r/'build/DoroCostumes/Meshes/Armor/DoroCostumes/DoroHelmet.nif'),reference_skel=str(r/'reference/costumes/human_skeleton.nif'),rename_bones=False,rotate_bones_pretty=False,blender_xf=False,import_pose=False,import_collisions=False)
new=set(bpy.data.objects)-before;hrig=next(o for o in new if o.type=='ARMATURE');hm=[o for o in new if o.type=='MESH'];assert len(hm)==2
for o in hm:
 assert all(o.vertex_groups[g.group].name=='HEAD' for v in o.data.vertices for g in v.groups if g.weight>0)
 o.data.materials.clear();o.data.materials.append(mat)
scene.camera.location=(85,120,145);scene.camera.rotation_euler=(Vector((0,0,130))-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=85;floor.location.z=96
for i,angle in enumerate([-35,0,35]):
 bone=hrig.pose.bones['HEAD'];bone.rotation_mode='XYZ';bone.rotation_euler.z=math.radians(angle);bpy.context.view_layer.update()
 scene.render.filepath=str(out/f'helmet_yaw_{i}.png');bpy.ops.render.render(write_still=True)
(r/'build/costume_animation_validation.json').write_text(json.dumps({'dog':checks,'helmet_head_only_weights':True,'helmet_pose_samples':3,'ingame_tested':False},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(r/'build/DoroCostumes_roundtrip_QA.blend'))
print('COSTUME_QA_PASS',flush=True)
