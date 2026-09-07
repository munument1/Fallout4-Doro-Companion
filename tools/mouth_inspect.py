import bpy,json
from mathutils import Vector
for o in bpy.context.scene.objects:
 if o.type=='MESH' and o.name.startswith('CH_NPC'):
  pts=[o.matrix_world@Vector(c) for c in o.bound_box]
  print(o.name,'bounds',[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]], 'verts',len(o.data.vertices),'matrix',[list(r) for r in o.matrix_world])
