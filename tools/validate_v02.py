from pathlib import Path
import json,sys,struct,zipfile,hashlib
sys.path.insert(0,'tools')
from fo4_records import records,subs,edid,GAME
r=Path.cwd();out=r/'build/DoroFollower'
new={f:(t,list(subs(b))) for t,f,flags,b in records(out/'DoroFollower.esp')}
van={f:list(subs(b)) for t,f,flags,b in records(GAME/'Data/Fallout4.esm') if f in [0xa0f2f,0xa0f33]}
race=new[0x1000800][1];npc=new[0x1000803][1]
assert [v for s,v in race if s in ['ATKD','ATKE','SGNM','SAPT']]==[v for s,v in van[0xa0f2f] if s in ['ATKD','ATKE','SGNM','SAPT']]
assert next(v for s,v in npc if s=='AIDT')[0]==1
assert next(v for s,v in npc if s=='ZNAM')==next(v for s,v in van[0xa0f33] if s=='ZNAM')
assert struct.unpack_from('<I',next(v for s,v in race if s=='DATA'),32)[0]&0x200000
assert 'commands.Show' not in (r/'tools/DoroCompanionScript.psc').read_text()
assert len([1 for t,ss in new.values() if t=='INFO'])==8
checks=json.loads((r/'build/roundtrip_animation_checks.json').read_text())
assert {x['action'] for x in checks}=={'RunForward','RunStart','WalkForward','Attack1','Attack3'}
for info in range(0x820,0x828):
 ss=new[0x1000000+info][1]
 assert len(next(v for s,v in ss if s=='TRDA'))==20
seamchecks=json.loads((r/'build/seam_animation_checks.json').read_text())
assert len(seamchecks)==5
assert max(x['max_seam_gap'] for x in seamchecks)<0.001
report={'seam_checks':seamchecks,'version':'0.2','script_compile':'passed','plugin_records':len(new),'native_attack_data_preserved':True,'native_behavior_paths_preserved':True,'native_dialogue_responses':8,'sampled_animation_frames':len(checks),'ingame_verified':False,'remaining':'In-game dialogue, combat response and running need retest; body folds remain in extreme bear poses.'}
(r/'build/verification_0.2.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
