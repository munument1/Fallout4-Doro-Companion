import bpy,sys,json
from pathlib import Path
from mathutils import Vector
root=Path(r'D:\Codex_Trans\Fo4 modding');sys.path.insert(0,str(root/'tools/deps/pynifly28'))
import io_scene_nifly,addon_utils
addon_utils.enable('io_scene_nifly',default_set=True,persistent=True)
bpy.ops.import_scene.pynifly(filepath=str(root/'reference/dogmeat/dogmeat.nif'),reference_skel=str(root/'reference/dogmeat/skeleton.nif'),rename_bones=False,import_collisions=False,import_pose=False)
pts=[o.matrix_world@Vector(c) for o in bpy.context.scene.objects if o.type=='MESH' and o.name!='Cube' for c in o.bound_box]
bounds={'min':[min(p[i] for p in pts) for i in range(3)],'max':[max(p[i] for p in pts) for i in range(3)]}
(root/'build/dogmeat_bounds.json').write_text(json.dumps(bounds));print(bounds)
