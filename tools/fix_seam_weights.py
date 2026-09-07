import bpy,collections,json
from pathlib import Path
r=Path(r'D:\Codex_Trans\Fo4 modding');bpy.ops.wm.open_mainfile(filepath=str(r/'build/Doro_FO4_rigged.blend'))
o=bpy.data.objects['Doro_Body'];groups=collections.defaultdict(list)
for v in o.data.vertices:groups[tuple(round(x,3) for x in v.co)].append(v)
count=0
for vs in groups.values():
 if len(vs)<2:continue
 weights=collections.defaultdict(float)
 for v in vs:
  for g in v.groups:weights[g.group]+=g.weight/len(vs)
 weights=dict(sorted(weights.items(),key=lambda x:x[1],reverse=True)[:4]);total=sum(weights.values())
 indices=[v.index for v in vs]
 for g in o.vertex_groups:g.remove(indices)
 for g,w in weights.items():o.vertex_groups[g].add(indices,w/total,'REPLACE')
 co=sum((v.co for v in vs),vs[0].co*0)/len(vs)
 for v in vs:v.co=co
 count+=1
bpy.ops.wm.save_as_mainfile(filepath=str(r/'build/Doro_FO4_rigged.blend'))
print('SYNCHRONIZED_SEAM_CLUSTERS',count,flush=True)
