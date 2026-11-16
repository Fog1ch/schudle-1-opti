from pathlib import Path
import json,re,subprocess
r=Path(__file__).parent;p=r.parent/'EXPORT/AI_RESEARCH_PACKAGE'
ms=json.loads((r/'evidence/methods-all.json').read_text())
targets=[0x96C800,0x96E970,0x96FE00,0x989CE0]
for x in ms:
 if x['Type']=='ScheduleOne.NPCs.Behaviour.MoveToAndActBehaviour' and 'RpcLogic___StartAct' in x['Name']: targets.append(x['RVA'])
print('NEXT METHODS',[x for x in ms if x['RVA'] in targets])
new=[]
for rv in targets:
 hits=[f for f in p.rglob('*.asm.txt') if re.search(r'(?:_|^)%X[_.]'%rv,f.name,re.I)]
 if hits: print('EXISTS',hits)
 elif not (r/'evidence'/('helper_%X.asm.txt'%rv)).exists():
  x=next(x for x in ms if x['RVA']==rv);new.append('%X:%X'%(rv,x['Length']))
if new:
 z=subprocess.run([str(r/'analyzer/bin/Release/net8.0/Analyzer.exe'),*new],capture_output=True,text=True);print(z.returncode,z.stdout);assert z.returncode==0
for rv in targets:
 f=r/'evidence'/('helper_%X.asm.txt'%rv)
 if f.exists():
  print('\n===',f.name,'===')
  for l in f.read_text().splitlines():
   if any(s in l for s in ['call','jmp','lea rdx','lea r8','mov byte']):print(l)
hits=[]
for f in (p/'EVIDENCE/phase2/evidence').glob('*.asm.txt'):
 if f.name.startswith('helper_'):continue
 for l in f.read_text().splitlines():
  if '+1B8h]' in l: hits.append({'file':str(f.relative_to(p)),'line':l.split(' ; ')[0]})
(r/'path-field-sites.json').write_text(json.dumps(hits,indent=2));print('FIELD SITES',json.dumps(hits))
targets=[0x2B20AF0,0x2B20AB0,0x2B20A60,0x2B20A20,0x469210,0x423EA0]; matched=[]
for f in (p/'EVIDENCE').rglob('*.asm.txt'):
 for l in f.read_text(encoding='utf-8-sig').splitlines():
  if ('call' in l or 'jmp' in l) and any(('%016Xh'%(0x180000000+t)).lower() in l.lower() for t in targets): matched.append({'file':str(f.relative_to(p)),'line':l.split(' ; ')[0]})
(r/'path-api-sites.json').write_text(json.dumps(matched,indent=2));print('API SITES',json.dumps(matched))
