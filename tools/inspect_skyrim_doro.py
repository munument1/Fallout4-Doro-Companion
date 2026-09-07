import bpy,json
from pathlib import Path
root=Path(r'D:\Codex_Trans\Fo4 modding\reference\skyrim_doro_source')
for o in bpy.context.scene.objects:
    o.hide_set(True);o.hide_render=True
report=[]
for filename in ['EMBody.nif','DoroHead.nif','Doro_HeadACC.nif']:
    before=set(bpy.data.objects)
    status=bpy.ops.import_scene.pynifly(filepath=str(root/'Meshes/SB_Doro'/filename),create_bones=True,rename_bones=False,import_collisions=False,create_collection=True)
    for o in set(bpy.data.objects)-before:
        r={'source':filename,'name':o.name,'type':o.type,'dimensions':list(o.dimensions)}
        if o.type=='ARMATURE':r['bones']=[b.name for b in o.data.bones]
        if o.type=='MESH':
            r['vertices']=len(o.data.vertices);r['polygons']=len(o.data.polygons);r['uv_layers']=[u.name for u in o.data.uv_layers];r['vertex_groups']=[g.name for g in o.vertex_groups]
            r['materials']=[m.name for m in o.data.materials if m]
        report.append(r)
print(json.dumps(report))
(root/'model_inspection.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(root/'Skyrim_Doro_inspection.blend'))
