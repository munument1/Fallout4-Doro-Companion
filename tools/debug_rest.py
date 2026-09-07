import bpy,json
bpy.ops.wm.open_mainfile(filepath=r'D:\Codex_Trans\Fo4 modding\build\Doro_FO4_rigged.blend')
r=bpy.data.objects['Doro_YaoGuai_Rig']
print('RIG_XF',list(r.location),list(r.scale))
print('POSE',[(b.name,[list(row) for row in b.matrix_basis]) for b in r.pose.bones if b.name in ['HEAD','SPINE1','Pelvis']])
for n in ['Doro_Face','Doro_Body','Doro_Hair']:
 o=bpy.data.objects[n];print(n,'bounds',[[min(v.co[i] for v in o.data.vertices) for i in range(3)],[max(v.co[i] for v in o.data.vertices) for i in range(3)]],[(m.name,m.type) for m in o.modifiers])
r.data.pose_position='REST'
bpy.context.scene.render.filepath=r'D:\Codex_Trans\Fo4 modding\build\rest_debug.png';bpy.ops.render.render(write_still=True)
