import bpy,json
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath=r'D:\Codex_Trans\Fo4 modding\build\Doro_FO4_rigged.blend')
o=bpy.data.objects['Doro_Body']
for g in o.vertex_groups:
 vs=[(v.co,w.weight) for v in o.data.vertices for w in v.groups if w.group==g.index]
 total=sum(w for v,w in vs)
 print(g.name, [round(sum(v[i]*w for v,w in vs)/total,2) for i in range(3)],round(total,1),flush=True)
