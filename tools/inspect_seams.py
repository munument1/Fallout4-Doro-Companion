import bpy,collections,json
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath=r'D:\Codex_Trans\Fo4 modding\build\Doro_FO4_rigged.blend')
o=bpy.data.objects['Doro_Body'];groups=collections.defaultdict(list)
for v in o.data.vertices:groups[tuple(round(x,3) for x in v.co)].append(v)
clusters=[vs for vs in groups.values() if len(vs)>1]
print('DUPLICATE_CLUSTERS',len(clusters),'VERTICES',sum(map(len,clusters)),flush=True)
for vs in clusters[:15]:print('SEAM',[list(v.co) for v in vs],[[ (o.vertex_groups[w.group].name,round(w.weight,3)) for w in v.groups] for v in vs],flush=True)
import bmesh
bm=bmesh.new();bm.from_mesh(o.data)
boundaries=[e for e in bm.edges if e.is_boundary]
print('BOUNDARIES',len(boundaries),flush=True)
Path(r'D:\Codex_Trans\Fo4 modding\build\seam_inspection.json').write_text(json.dumps({'duplicate_clusters':len(clusters),'duplicate_vertices':sum(map(len,clusters)),'boundary_edges':len(boundaries)},indent=2))
