import bpy,sys,json,shutil,collections
from pathlib import Path
from mathutils import Vector
r=Path(r'D:\Codex_Trans\Fo4 modding');sys.path.insert(0,str(r/'tools/deps/pynifly28'))
import addon_utils
addon_utils.enable('io_scene_nifly',default_set=True,persistent=True)
bpy.ops.wm.open_mainfile(filepath=str(r/'build/Doro_FO4_rigged.blend'))
out=r/'build/DoroCostumes';(out/'Meshes/Armor/DoroCostumes').mkdir(parents=True,exist_ok=True)
for folder in ['Materials/Actors/Doro','Textures/Actors/Doro']:
 shutil.copytree(r/'build/DoroFollower'/folder,out/folder,dirs_exist_ok=True)
source={n:bpy.data.objects[n] for n in ['Doro_Face','Doro_Body','Doro_Hair']}
for o in bpy.context.scene.objects:
 if o.type in ['MESH','ARMATURE']:o.hide_set(True);o.hide_render=True

def import_rig(p,name):
 bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=None;before=set(bpy.data.objects)
 bpy.ops.import_scene.pynifly(filepath=str(p),reference_skel=str(p),rename_bones=False,rotate_bones_pretty=False,blender_xf=False,import_collisions=False,create_bones=True,import_pose=False)
 rig=next(o for o in set(bpy.data.objects)-before if o.type=='ARMATURE');rig.name=name
 for extra in set(bpy.data.objects)-before:
  if extra!=rig:extra.hide_set(True);extra.hide_render=True
 return rig

def duplicate(src,name,rig,transform,weights):
 o=src.copy();o.data=src.data.copy();bpy.context.collection.objects.link(o);o.name=name;o.modifiers.clear();o.parent=None;o.hide_set(False);o.hide_render=False;o.shape_key_clear()
 original={g.index:g.name for g in o.vertex_groups};vw=[]
 for v in o.data.vertices:
  v.co=transform(v.co.copy());vw.append(weights(v,{original[g.group]:g.weight for g in v.groups}))
 o.vertex_groups.clear();gs={n:o.vertex_groups.new(name=n) for n in sorted({n for d in vw for n in d})}
 for i,d in enumerate(vw):
  total=sum(d.values())
  for n,w in d.items():gs[n].add([i],w/total,'REPLACE')
 if rig:
  mod=o.modifiers.new('Costume skin','ARMATURE');mod.object=rig
 for k in list(o.keys()):del o[k]
 o['PYN_GAME']='FO4'
 o.data.materials[0]['BSLSP_Shader_Name']='Materials\\Actors\\Doro\\Doro.bgsm'
 return o

def export(name,meshes,rig=None):
 bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=None
 for o in meshes:o.select_set(True)
 if rig:rig.hide_set(False);rig.select_set(True);bpy.context.view_layer.objects.active=rig
 else:bpy.context.view_layer.objects.active=meshes[0]
 bpy.ops.export_scene.pynifly(filepath=str(out/'Meshes/Armor/DoroCostumes'/name),target_game='FO4',rename_bones=False,rotate_bones_pretty=False,blender_xf=False,preserve_hierarchy=True,export_pose=False,export_modifiers=False,export_animations=False,write_tris=False,intuit_defaults=False)

rig=import_rig(r/'reference/dogmeat/skeleton.nif','DoroCostume_Dogmeat_Rig')
mapping={'HEAD':'Dogmeat_Head','Neck1':'Dogmeat_Neck1','Neck2':'Dogmeat_Neck2','COM':'Dogmeat_COM','Pelvis':'Dogmeat_Pelvis','SPINE1':'Dogmeat_Spine1','SPINE2':'Dogmeat_Spine2','Spine3':'Dogmeat_Spine3','Ribcage':'Dogmeat_Ribcage'}
for s in ['L','R']:
 for area in ['Front','Rear']:
  for a,b in [('Thigh','1'),('Knee','2'),('Ankle','Ankle')]:mapping[f'{s}Leg_{area}_{a}']=f'Dogmeat_{area}_{s}Leg{b}'
dog=[]
for n,src in source.items():
 dog.append(duplicate(src,n+'_DogCostume',rig,lambda v:Vector((v.x*.56,v.y*.68-6,v.z*.56)),lambda v,d:{mapping[k]:w for k,w in d.items()}))
export('DoroDogSuit.nif',dog,rig)
# Neutral animation files used only for Blender verification.
for o in dog:o.hide_set(True);o.hide_render=True
rig.hide_set(True)
hrig=import_rig(r/'reference/costumes/human_skeleton.nif','DoroHelmet_Human_Rig')
headsource=[source['Doro_Face'],source['Doro_Hair']];pts=[v.co for o in headsource for v in o.data.vertices]
ycenter=(max(p.y for p in pts)+min(p.y for p in pts))/2;zmin=min(p.z for p in pts)
# 0.2.5-test3: lower the worn mascot head by 18 units (112 -> 94) so it sits
# around the player's head/neck instead of floating above the shoulders.
HELMET_Z=94
head=[]
for src in headsource:
 head.append(duplicate(src,src.name+'_Helmet',hrig,lambda v:Vector((v.x*.42,(v.y-ycenter)*.42-1,(v.z-zmin)*.42+HELMET_Z)),lambda v,d:{'HEAD':1.}))
export('DoroHelmet.nif',head,hrig)
# Ground/inventory display mesh at origin; no armature or actor reference is required.
ground=[]
for src in head:
 g=src.copy();g.data=src.data.copy();bpy.context.collection.objects.link(g);g.name=src.name+'_Ground';g.modifiers.clear();g.vertex_groups.clear()
 for v in g.data.vertices:v.co.z-=HELMET_Z
 ground.append(g)
export('DoroHelmetGO.nif',ground)
for o in ground:o.hide_set(True);o.hide_render=True
# Preview the helmet with a neutral bust, which is excluded from exports.
scene=bpy.context.scene
for o in bpy.data.objects:
 if o.type=='LIGHT':o.hide_render=False;o.hide_set(False)
floor=bpy.data.objects['Studio floor'];floor.hide_render=False;floor.hide_set(False);floor.location.z=78
for o in head:o.hide_set(False);o.hide_render=False
scene.camera.location=(85,120,127);scene.camera.rotation_euler=(Vector((0,0,112))-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=85
scene.render.resolution_x=640;scene.render.resolution_y=640;scene.cycles.samples=20
scene.render.filepath=str(r/'build/doro_helmet_preview.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(r/'build/DoroCostumes.blend'))
print('COSTUME_MESHES_EXPORTED',flush=True)
