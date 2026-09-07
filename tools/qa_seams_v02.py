import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
root=Path(r'D:\Codex_Trans\Fo4 modding');sys.path.insert(0,str(root/'tools/deps/pynifly28'))
import io_scene_nifly,addon_utils
addon_utils.enable('io_scene_nifly',default_set=True,persistent=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'build/Doro_FO4_rigged.blend'))
for o in bpy.context.scene.objects:
 if o.type in ['MESH','ARMATURE']:o.hide_set(True);o.hide_render=True
before=set(bpy.data.objects)
skel=Path(r'C:\Users\seung\OneDrive\Desktop\Meshes\Actors\YaoGuai\CharacterAssets\skeleton.nif')
bpy.ops.import_scene.pynifly(filepath=str(root/'build/DoroFollower/Meshes/Actors/Doro/Doro.nif'),reference_skel=str(skel),rename_bones=False,rotate_bones_pretty=False,blender_xf=False,import_collisions=False,import_pose=False)
new=set(bpy.data.objects)-before;rig=next(o for o in new if o.type=='ARMATURE');meshes=[o for o in new if o.type=='MESH']
assert len(meshes)==3,len(meshes)
mat=bpy.data.materials.get('Doro source texture preview')
for o in meshes:o.data.materials.clear();o.data.materials.append(mat)
scene=bpy.context.scene
floor=bpy.data.objects['Studio floor'];floor.hide_set(False);floor.hide_render=False
scene.render.resolution_x=512;scene.render.resolution_y=512;scene.cycles.samples=12
out=root/'build/qa_0.2';out.mkdir(exist_ok=True)
scene.render.filepath=str(out/'roundtrip_rest.png');bpy.ops.render.render(write_still=True)
import collections
seams=[]
for obj in meshes:
 if 'Body' not in obj.name:continue
 buckets=collections.defaultdict(list)
 for v in obj.data.vertices:buckets[tuple(round(x,3) for x in v.co)].append(v.index)
 seams.extend((obj,ids) for ids in buckets.values() if len(ids)>1)
print('ROUNDTRIP_SEAM_CLUSTERS',len(seams),flush=True)
seamchecks=[]
checks=[]
print('BONES',[(b.name,list(b.head_local)) for b in rig.data.bones if any(t in b.name for t in ['Front','Rear','SPINE','HEAD'])],flush=True)
for action in ['RunForward','RunStart','WalkForward','Attack1','Attack3']:
 bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
 bpy.ops.import_scene.pynifly_hkx(filepath=str(skel.parent.parent/'Animations'/f'{action}.hkx'),reference_skel=str(skel.with_suffix('.hkx')),rename_bones=False,rotate_bones_pretty=False,blender_xf=False)
 act=rig.animation_data.action;start,end=act.frame_range
 worst=0.
 for f in range(int(start),int(end)+1):
  scene.frame_set(f);dg=bpy.context.evaluated_depsgraph_get()
  for obj,ids in seams:
   vv=obj.evaluated_get(dg).data.vertices
   worst=max(worst,max((vv[i].co-vv[ids[0]].co).length for i in ids))
 seamchecks.append({'action':action,'frames':int(end-start+1),'max_seam_gap':worst})
 assert worst<0.001,(action,worst)
 for i in range(6):
  frame=round(start+(end-start)*i/5);scene.frame_set(frame);dg=bpy.context.evaluated_depsgraph_get()
  pts=[o.matrix_world@v.co for o in meshes for v in o.evaluated_get(dg).data.vertices]
  bounds=[[min(p[j] for p in pts) for j in range(3)],[max(p[j] for p in pts) for j in range(3)]]
  assert all(math.isfinite(x) for p in bounds for x in p)
  checks.append({'action':action,'frame':frame,'bounds':bounds})
  scene.render.filepath=str(out/f'{action}_{i:02}.png');bpy.ops.render.render(write_still=True)
(root/'build/seam_animation_checks.json').write_text(json.dumps(seamchecks,indent=2))
(root/'build/roundtrip_animation_checks.json').write_text(json.dumps(checks,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(root/'build/Doro_FO4_roundtrip_QA.blend'))
print('ROUNDTRIP_QA_FINISHED',flush=True)
