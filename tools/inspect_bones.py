import bpy,json
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath=r'D:\Codex_Trans\Fo4 modding\build\Doro_FO4_rigged.blend')

for b in bpy.data.objects['Doro_YaoGuai_Rig'].data.bones: print(b.name,[round(x,2) for x in b.head_local],flush=True)
