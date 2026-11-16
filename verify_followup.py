from pathlib import Path
import hashlib,json
r=Path(__file__).parent;p=r.parent/'EXPORT/AI_RESEARCH_PACKAGE';a=r.parent/'phase2-ab-audit-20261116-0047'
checks=[]
for base,manifest in [(p,p/'FILE_MANIFEST.json'),(a,a/'AUDIT_MANIFEST.json')]:
 rows=json.loads(manifest.read_text(encoding='utf-8-sig'));bad=[]
 for x in rows:
  f=base/x['path']
  if not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest().lower()!=x['sha256'].lower():bad.append(x['path'])
 checks.append({'root':str(base),'entries':len(rows),'mismatches':bad})
expected={'GameAssembly.dll':'61829050e56ca180d67be592e4bfe61ec97d2e9573f720d90a54e318a7e4381d','Schedule I_Data/il2cpp_data/Metadata/global-metadata.dat':'e775c97da277da8eb1a90265478f3b65c9c3d6464aff4f7255d45280a1d1181f'}
for name,sha in expected.items():checks.append({'path':name,'match':hashlib.sha256((Path(r'B:\Schedule I')/name).read_bytes()).hexdigest()==sha})
print(json.dumps(checks,ensure_ascii=False));(r/'integrity-check.json').write_text(json.dumps(checks,indent=2))
files=[f for f in r.rglob('*') if f.is_file() and f.suffix in ['.md','.json','.txt','.py','.cs','.csproj'] and 'bin' not in f.parts and 'obj' not in f.parts and f.name!='FOLLOWUP_MANIFEST.json']
m=[{'path':str(f.relative_to(r)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in files]
(r/'FOLLOWUP_MANIFEST.json').write_text(json.dumps(m,indent=2))
print('SAVED',r/'FOLLOWUP_AB.md','manifest entries',len(m))
assert (r/'FOLLOWUP_AB.md').read_text(encoding='utf-8').startswith('# Дополнение')
