from pathlib import Path
import json,re,shutil,subprocess,hashlib
r=Path(r'C:\Users\herob\Documents\notion-code\work\ScheduleI-Performance-Lab-20261115')
p=r/'EXPORT/AI_RESEARCH_PACKAGE'
o=Path(__file__).parent
ms=json.loads((p/'EVIDENCE/phase2/evidence/methods-all.json').read_text(encoding='utf-8-sig'))
want={x['RVA']:x for x in ms if (x['Name']=='WalkCallback' and x['RVA']!=0x919EF0) or (x['Type']=='UnityEngine.AI.NavMeshPath' and x['Name'] in ['DestroyNavMeshPath','ClearCorners','ClearCornersInternal']) or (x['Type']=='UnityEngine.AI.NavMeshAgent' and x['Name'] in ['SetPath','CopyPathTo'])}
files=list(r.rglob('*.asm.txt')); found={}
for rv in want:
 hits=[f for f in files if re.search(r'(?:_|^)%X(?:[_.])'%rv,f.name,re.I)]
 if hits: found[rv]=str(hits[0])
(o/'range-discovery.json').write_text(json.dumps({'existing':found,'requested':list(want.values())},indent=2))
dst=o/'analyzer/bin/Release/net8.0'
assert not dst.exists(), 'Do not overwrite'
shutil.copytree(r/'phase2-ab-audit-20261116-0047/analyzer/bin/Release/net8.0',dst)
sha=hashlib.sha256(Path(r'B:\Schedule I\GameAssembly.dll').read_bytes()).hexdigest()
assert sha=='61829050e56ca180d67be592e4bfe61ec97d2e9573f720d90a54e318a7e4381d'
specs=['%X:%X'%(rv,x['Length']) for rv,x in want.items() if rv not in found]
print('EXISTING',found);print('EXTRACT',specs)
z=subprocess.run([str(dst/'Analyzer.exe'),*specs],capture_output=True,text=True)
print(z.returncode,z.stdout,z.stderr)
assert z.returncode==0
for f in (o/'evidence').glob('helper_*.asm.txt'):
 print('\n===',f.name,'===\n'+'\n'.join(l.split(' ; ')[0] for l in f.read_text().splitlines()))
