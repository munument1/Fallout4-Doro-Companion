import struct

def build_dialogue(add,clone,own,U,F,S,rec,group,placed,npc,voice):
 quest,scene=own(0x80c),own(0x80d)
 name=b'DoroDialogueQuestScript'
 vmad=struct.pack('<HHHH',6,2,1,len(name))+name+b'\0'+struct.pack('<H',0)
 # Quest VMAD trailing fragment header: no fragments, no aliases with scripts.
 vmad+=struct.pack('<BH',3,0)+struct.pack('<H',0)+struct.pack('<H',0)
 ss=[('EDID',S('DoroDialogueQuest')),('VMAD',vmad),('FULL',S('Doro')),('DNAM',struct.pack('<HBBfB3s',0x8019,70,0,0.,0,b'\0'*3)),('NEXT',b'')]
 for stage in [10,20,30,40]:ss.extend([('INDX',struct.pack('<HBB',stage,0,0)),('QSDT',b'\0')])
 ss.extend([('ANAM',U(1)),('ALST',U(0)),('ALID',S('Doro')),('FNAM',U(0x28A)),('ALFR',U(placed)),('ALED',b'')])
 add('QUST',quest,ss)
 # One genuine four-option dialogue action, with the player as implicit actor -2.
 ss=clone(0x1ab276,{'EDID':S('DoroMainDialogueScene')})
 start=next(i for i,(s,b) in enumerate(ss) if s=='ANAM' and b==b'\x01\x00')
 end=next(i for i in range(start+1,len(ss)) if ss[i]==('ANAM',b''))+1
 del ss[start:end]
 topickeys=['PTOP','NTOP','NETO','QTOP','NPOT','NNGT','NNUT','NQUT']
 for i,(s,b) in enumerate(ss):
  if s in topickeys:ss[i]=(s,U(own(0x810+topickeys.index(s))))
  elif s=='PNAM':ss[i]=(s,U(quest))
  elif s=='INAM':ss[i]=(s,U(1))
 add('SCEN',scene,ss)
 names=['Follow me','Head home','Trade','Wait here']
 chunks=[]
 for i in range(8):
  topic,info=own(0x810+i),own(0x820+i)
  isplayer=i<4
  text=names[i%4] if isplayer else 'Doro~'
  dial=[('EDID',S('DoroTopic'+str(i))),('PNAM',F(50)),('QNAM',U(quest)),('DATA',bytes.fromhex('00021100')),('SNAM',b'SCEN'),('TIFC',U(1))]
  inf=[('EDID',S('DoroResponse'+str(i))),('ENAM',struct.pack('<HH',0x800,0xffff)),('TPIC',U(topic)),('PNAM',U(0)),('TRDA',struct.pack('<IBIBHii',0xffffffff,1,0 if isplayer else voice,1,0,-1,-1)),('NAM1',S(text)),('NAM2',S('')),('NAM3',S('')),('NAM4',S(''))]
  if isplayer:inf.append(('RNAM',S(text)))
  else:inf.append(('TIQS',struct.pack('<HH',[10,40,30,20][i%4],0)))
  chunks.append(rec('DIAL',topic,dial)+group(U(topic),7,rec('INFO',info,inf)))
 # Native activation selects Greeting, establishes the conversation target, then
 # starts the player-dialogue scene, as Dogmeat's vanilla greeting does.
 topic,info=own(0x828),own(0x829)
 dial=[('EDID',S('DoroGreeting')),('PNAM',F(80)),('QNAM',U(quest)),('DATA',bytes([0,7,118,0])),('SNAM',b'GREE'),('TIFC',U(1))]
 condition=struct.pack('<B3sfH2sIIIII',0,b'\0'*3,1.,72,b'\0'*2,npc,0,0,0,0xffffffff)
 inf=[('EDID',S('DoroGreetingResponse')),('ENAM',struct.pack('<HH',0x809,0)),('TRDA',struct.pack('<IBIBHii',0xffffffff,1,voice,1,0,-1,-1)),('NAM1',S('Doro~')),('NAM2',S('')),('NAM3',S('')),('NAM4',S('')),('CTDA',condition),('TSCE',U(scene)),('NAM0',S('MainDogmeatDialoguePhase')),('INAM',U(1))]
 chunks.append(rec('DIAL',topic,dial)+group(U(topic),7,rec('INFO',info,inf)))
 return group(b'DIAL',0,b''.join(chunks)),18
