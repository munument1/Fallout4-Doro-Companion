import bpy,math
from pathlib import Path
r=Path(r'D:\Codex_Trans\Fo4 modding')
bpy.ops.wm.open_mainfile(filepath=str(r/'build/backup_0.1/Doro_FO4_rigged.blend'))
o=bpy.data.objects['Doro_Body']
# Old Skyrim torso group names do not correspond to the YaoGuai spine chain.
chain=[(-83,'SPINE1'),(-60.38,'SPINE2'),(-37.37,'Spine3'),(-14.48,'Ribcage'),(18.73,'Neck1'),(38.28,'Neck2'),(57.90,'HEAD')]
oldnames={g.index:g.name for g in o.vertex_groups};allw=[]
for v in o.data.vertices:
 d={oldnames[g.group]:g.weight for g in v.groups}
 trunk=sum(w for n,w in d.items() if 'Leg_' not in n)
 d={n:w for n,w in d.items() if 'Leg_' in n}
 # Reduce shoulder/hip weights spilling into the upper torso, keeping limbs separate.
 fade=max(0,min(1,(v.co.z-58)/26))
 for n in list(d):
  removed=d[n]*fade;d[n]-=removed;trunk+=removed
 y=v.co.y
 if y<=chain[0][0]:d[chain[0][1]]=trunk
 elif y>=chain[-1][0]:d['HEAD']=trunk
 else:
  for (a,na),(b,nb) in zip(chain,chain[1:]):
   if a<=y<=b:
    t=(y-a)/(b-a);d[na]=d.get(na,0)+trunk*(1-t);d[nb]=d.get(nb,0)+trunk*t;break
 # Blend compact lower limbs toward the body root to limit long bear-joint lever arms.
 limb=sum(w for n,w in d.items() if 'Leg_' in n)
 anchor=0.5*limb*max(0,min(1,(65-v.co.z)/35))
 d={n:w*(1-anchor) for n,w in d.items()}
 d['COM']=anchor
 d=dict(sorted(d.items(),key=lambda x:x[1],reverse=True)[:4]);s=sum(d.values());allw.append({n:w/s for n,w in d.items() if w>1e-6})
o.vertex_groups.clear();groups={n:o.vertex_groups.new(name=n) for n in sorted({n for d in allw for n in d})}
for i,d in enumerate(allw):
 for n,w in d.items():groups[n].add([i],w,'REPLACE')
bpy.ops.wm.save_as_mainfile(filepath=str(r/'build/Doro_FO4_rigged.blend'))
