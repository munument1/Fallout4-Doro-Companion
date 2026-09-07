import struct,json
from pathlib import Path


def build_dialogue(add,clone,own,U,F,S,rec,group,placed,npc,voice):
 donor={int(r['id'],16):[(s,bytes.fromhex(v)) for s,v in r['subrecords']] for r in json.loads((Path(__file__).resolve().parent.parent/'build/gorilla_records.json').read_text())}
 quest,scene,stay,vtyp=map(own,[0x80c,0x80d,0x82a,0x82b])
 name=b'DoroDialogueQuestScript'
 vmad=struct.pack('<HHHH',6,2,1,len(name))+name+b'\0'+struct.pack('<H',0)+struct.pack('<BH',3,0)+struct.pack('<H',0)+struct.pack('<H',0)
 # Fallout 4 requires HasDialogueData (0x8000) on QUST records that own dialogue.
 quest_flags=0x8119
 ss=[('EDID',S('DoroDialogueQuest')),('VMAD',vmad),('DNAM',struct.pack('<HBBfB3s',quest_flags,70,0,0.,0,b'\0'*3)),('NEXT',b'')]
 for stage,label in [(10,'Follow'),(20,'Wait'),(30,'Trade'),(40,'Dismiss')]:ss.extend([('INDX',struct.pack('<HBB',stage,0,0)),('QSDT',b'\0'),('NAM2',S(label))])
 ss.extend([('ANAM',U(1)),('ALST',U(0)),('ALID',S('Doro')),('FNAM',U(0x28a)),('ALUA',U(npc)),('VTCK',U(0)),('ALED',b'')]);add('QUST',quest,ss)
 add('VTYP',vtyp,[('EDID',S('DoroDialogueVoice')),('DNAM',b'\0')])
 add('PACK',stay,[(s,S('DoroStayForDialogue') if s=='EDID' else v) for s,v in donor[0x19aa2]])
 keys=['PTOP','NTOP','NETO','QTOP','NPOT','NNGT','NNUT','NQUT']
 source_scene=donor[0x1002670]
 source_topics={s:int.from_bytes(v,'little') for s,v in source_scene if s in keys}
 ss=[]
 for s,v in source_scene:
  if s=='EDID':v=S('DoroMainDialogueScene')
  elif s in keys:v=U(own(0x810+keys.index(s)))
  elif s=='PNAM':v=U(stay if int.from_bytes(v,'little')==0x19aa2 else quest)
  elif s=='XNAM':v=U(0)
  ss.append((s,v))
 add('SCEN',scene,ss)
 chunks=[];labels=['Follow me','Head home','Trade','Wait here'];stages=[10,40,30,20]
 for i,key in enumerate(keys):
  topic,info=own(0x810+i),own(0x820+i);src=source_topics[key]
  dial=[(s,U(quest) if s=='QNAM' else v) for s,v in donor[src]]
  inf=[]
  for s,v in donor[src+1]:
   if s in ['CTDA','NAM9','TIQS','TSCE','VMAD','RNAM']:continue
   if s=='NAM1':v=S(labels[i] if i<4 else 'Doro~')
   elif s=='ENAM':v=struct.pack('<HH',0 if i<4 else 0x40,0)
   inf.append((s,v))
  if i<4:
   ix=next((j for j,(s,v) in enumerate(inf) if s=='NAM0'),len(inf));inf.insert(ix,('RNAM',S(labels[i])))
  else:
   ix=next((j for j,(s,v) in enumerate(inf) if s=='NAM0'),len(inf));inf.insert(ix,('TIQS',struct.pack('<HH',0xffff,stages[i-4])))
  chunks.append(rec('DIAL',topic,dial)+group(U(topic),7,rec('INFO',info,inf)))
 topic,info=own(0x828),own(0x829)
 dial=[(s,S('DoroGreeting') if s=='EDID' else U(quest) if s=='QNAM' else U(1) if s=='TIFC' else v) for s,v in donor[0x1002671]]
 inf=[]
 for s,v in donor[0x1002672]:
  if s=='NAM9':continue
  if s=='NAM1':v=S('Doro~')
  elif s=='CTDA':
   fn=struct.unpack_from('<H',v,8)[0]
   if fn!=72:continue
   v=struct.pack('<B3sfH2sIIIII',0,b'\0'*3,1.,72,b'\0'*2,npc,0,0,0,0xffffffff)
  elif s=='TSCE':v=U(scene)
  inf.append((s,v))
 chunks.append(rec('DIAL',topic,dial)+group(U(topic),7,rec('INFO',info,inf)))
 return group(b'DIAL',0,b''.join(chunks)),18
