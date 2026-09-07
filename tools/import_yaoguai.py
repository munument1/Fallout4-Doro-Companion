import bpy, json
from pathlib import Path
src=Path(r'C:\Users\seung\OneDrive\Desktop\Meshes\Actors\YaoGuai\CharacterAssets')
out=Path(r'D:\Codex_Trans\Fo4 modding\reference')
out.mkdir(exist_ok=True)
before=set(bpy.data.objects)
print('SKELETON_IMPORT', bpy.ops.import_scene.pynifly(filepath=str(src/'skeleton.nif'),create_bones=True,rename_bones=False,import_collisions=False,create_collection=True))
skeleton_objects=set(bpy.data.objects)-before
bpy.ops.object.select_all(action='DESELECT')
print('BODY_IMPORT',bpy.ops.import_scene.pynifly(filepath=str(src/'YaoGuai.nif'),create_bones=True,rename_bones=False,import_collisions=False,create_collection=True,reference_skel=str(src/'skeleton.nif')))
added=set(bpy.data.objects)-before
report=[]
for obj in sorted(added,key=lambda o:o.name):
    item={'name':obj.name,'type':obj.type,'dimensions':list(obj.dimensions)}
    if obj.type=='ARMATURE':
        obj.show_in_front=True
        item['bones']=[{'name':b.name,'parent':b.parent.name if b.parent else None} for b in obj.data.bones]
    if obj.type=='MESH':
        item['vertices']=len(obj.data.vertices)
        item['vertex_groups']=len(obj.vertex_groups)
        item['armatures']=[m.object.name if m.object else None for m in obj.modifiers if m.type=='ARMATURE']
    report.append(item)
for obj in before:
    obj.hide_set(True)
for obj in added:
    obj.select_set(True)
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        with bpy.context.temp_override(area=area,region=next(r for r in area.regions if r.type=='WINDOW')):
            bpy.ops.view3d.view_selected(use_all_regions=False)
(out/'yaoguai_inspection.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'YaoGuai_reference.blend'))
bpy.ops.wm.save_userpref()
print('SUMMARY',json.dumps([{**{k:v for k,v in r.items() if k!='bones'},'bone_count':len(r.get('bones',[]))} for r in report]))
