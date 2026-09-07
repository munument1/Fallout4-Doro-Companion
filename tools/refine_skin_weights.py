import bpy
from pathlib import Path
r=Path(r'D:\Codex_Trans\Fo4 modding');bpy.ops.wm.open_mainfile(filepath=str(r/'build/Doro_FO4_rigged.blend'))
o=bpy.data.objects['Doro_Body'];adj=[set() for v in o.data.vertices]
for e in o.data.edges:
 a,b=e.vertices;adj[a].add(b);adj[b].add(a)
weights=[{g.group:g.weight for g in v.groups} for v in o.data.vertices]
for iteration in range(4):
 new=[]
 for i,own in enumerate(weights):
  d={k:v*.6 for k,v in own.items()};neighbors=adj[i]
  if neighbors:
   for j in neighbors:
    for k,v in weights[j].items():d[k]=d.get(k,0)+.4*v/len(neighbors)
  d=dict(sorted(d.items(),key=lambda t:t[1],reverse=True)[:4]);total=sum(d.values());new.append({k:v/total for k,v in d.items()})
 weights=new
for g in o.vertex_groups:g.remove(list(range(len(o.data.vertices))))
for i,d in enumerate(weights):
 for k,v in d.items():o.vertex_groups[k].add([i],v,'REPLACE')
bpy.ops.wm.save_as_mainfile(filepath=str(r/'build/Doro_FO4_rigged.blend'))
