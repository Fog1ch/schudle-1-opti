"""Package checks; writes only into the lab and its ZIP sibling."""
import collections,datetime,json,subprocess,sys,zipfile
from pathlib import Path
from s1lab import HERE,identity,digest
root=Path(r'B:\Schedule I')
audit=json.loads((HERE/'evidence/audit.json').read_text(encoding='utf-8'))
assert identity(root)==audit['identity'],'Installation binary fingerprint changed'
current=digest(root/'UserData/MelonPreferences.cfg')
profiles=[]
for p in sorted((HERE/'profiles').iterdir()):
    m=json.loads((p/'manifest.json').read_text(encoding='utf-8'))
    assert m['before']==current and m['applied'] is False
    assert digest(p/'original.cfg')==m['before'] and digest(p/'candidate.cfg')==m['after']
    profiles.append(p.name)
logs=[]
for args in ([sys.executable,'s1lab.py','selftest'],[sys.executable,'test_integration.py']):
    r=subprocess.run(args,cwd=HERE,capture_output=True,text=True,encoding='utf-8',errors='replace')
    logs.extend([' '.join(args),r.stdout,r.stderr])
    assert r.returncode==0,'Tests failed'
(HERE/'tests.txt').write_text('\n'.join(logs),encoding='utf-8')
assets=json.loads((HERE/'evidence/assets.json').read_text(encoding='utf-8'))
assert len(assets)==9 and not any('error' in x for x in assets)
c=collections.Counter()
for x in assets:c.update(x['class_counts'])
verification={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'binary_identity_unchanged':True,'preferences_unchanged':True,'profiles_prepared_not_applied':profiles,
 'unit_tests_passed':7,'fixture_integration_tests_passed':7,'game_tests_performed':False,
 'asset_containers_indexed':9,'asset_type_records':{k:c[k] for k in ('Texture2D','AudioClip','Shader','Mesh')},
 'historical_log_summary':audit.get('historical_frametime_summary'),
 'scope':'No game launch, binary patch, save change or profile application. Tests touched fixtures only.',
 'known_limits':['Asset parser is narrow, not independently cross-validated','Assembly names extracted from IL are not a complete dependency resolver','No measured performance benefit','No full native decompilation or per-resource decoding']}
(HERE/'verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2),encoding='utf-8')
files=sorted(p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='SHA256SUMS.txt')
(HERE/'SHA256SUMS.txt').write_text('\n'.join(digest(p)+'  '+p.relative_to(HERE).as_posix() for p in files)+'\n',encoding='utf-8')
archive=HERE.with_suffix('.zip')
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
    for p in files+[HERE/'SHA256SUMS.txt']:z.write(p,HERE.name+'/'+p.relative_to(HERE).as_posix())
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print(json.dumps(verification,ensure_ascii=True,indent=2))
print('ZIP:',archive,'bytes:',archive.stat().st_size,'SHA256:',digest(archive))
