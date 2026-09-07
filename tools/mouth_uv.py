import bpy
from mathutils import Vector
from mathutils.geometry import barycentric_transform
for o in bpy.data.objects:
 if o.type!='MESH' or not o.name.startswith('CH_NPC'):continue
 me=o.data
 if not me.uv_layers:continue
 me.calc_loop_triangles();uv=me.uv_layers.active.data
 for target in [(.402,.637),(.402,.60)]:
  for tri in me.loop_triangles:
   p=[Vector((*uv[i].uv,0)) for i in tri.loops];q=Vector((*target,0))
   a,b,c=p;den=(b.y-c.y)*(a.x-c.x)+(c.x-b.x)*(a.y-c.y)
   if abs(den)<1e-10:continue
   w=((b.y-c.y)*(q.x-c.x)+(c.x-b.x)*(q.y-c.y))/den;t=((c.y-a.y)*(q.x-c.x)+(a.x-c.x)*(q.y-c.y))/den
   if min(w,t,1-w-t)>=-1e-5:
    pos=barycentric_transform(q,*p,*[me.vertices[i].co for i in tri.vertices]);print(o.name,target,list(o.matrix_world@pos));break
