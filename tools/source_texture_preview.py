import bpy
from pathlib import Path
root=Path(r'D:\Codex_Trans\Fo4 modding\reference\skyrim_doro_source')
img=bpy.data.images.load(str(root/'Textures/SB_Doro/CH_NPC_Dororog_A.png'),check_existing=True)
for n in bpy.data.materials['Doro source texture preview'].node_tree.nodes:
 if n.type=='TEX_IMAGE':n.image=img
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(root/'Skyrim_Doro_inspection.blend'))
