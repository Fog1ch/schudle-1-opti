"""Schedule I offline configuration lab. Python 3.11+, standard library only.
Never launches the game, loads a DLL, touches saves or alters binary assets.
All proposals are EXPERIMENTAL. No measured performance gain is claimed.
"""
import argparse, collections, datetime, difflib, hashlib, json, os, re
import shutil, struct, subprocess, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = Path('UserData/MelonPreferences.cfg')
IDENTITY = ('Schedule I.exe', 'UnityPlayer.dll', 'GameAssembly.dll',
            'Schedule I_Data/il2cpp_data/Metadata/global-metadata.dat',
            'Mods/S1Perf.dll', 'Mods/ScheduleRu.dll')
PROFILES = {
    'ui-scan': ('ScheduleRu', 'CanvasScanInterval', '0.05'),
    'quiet-translation': ('ScheduleRu', 'DumpUntranslated', 'false'),
    'texture-2560': ('S1Perf', 'TextureBudgetMB', '2560'),
}
RISKS = {
    'ui-scan': 'Experimental: limits canvas discovery to at most 20 passes/s; newly created text may translate later. Visual quality settings unchanged.',
    'quiet-translation': 'Stops collection of untranslated strings; reduces diagnostic coverage. Translation remains enabled.',
    'texture-2560': 'Experimental streaming texture budget, NOT a total VRAM cap. May reduce mip detail or increase texture loading. Test separately.',
}

def digest(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()

def no_links(p):
    p = Path(os.path.abspath(p))
    for q in (p, *p.parents):
        if q.exists() and (q.is_symlink() or getattr(q.lstat(), 'st_file_attributes', 0) & 1024):
            raise ValueError('Refusing symbolic link or junction: ' + str(q))
    return p

def root_checked(root):
    root = no_links(root)
    for rel in IDENTITY:
        p = no_links(root / rel)
        if not p.is_file():
            raise ValueError('Required installation component missing: ' + rel)
    no_links(root / TARGET)
    if not (root / TARGET).is_file():
        raise ValueError('Preferences not found')
    return root

def identity(root):
    return {rel: digest(root / rel) for rel in IDENTITY}

def ensure_stopped():
    if os.name != 'nt':
        raise RuntimeError('Apply/rollback supported only on Windows')
    command = "$p=Get-Process -Name 'Schedule I' -ErrorAction SilentlyContinue; if($p){exit 2}else{exit 0}"
    r = subprocess.run(['powershell', '-NoProfile', '-NonInteractive', '-Command', command], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError('Game is running or process check failed. No changes made.')

def replace_one(data, section, key, value):
    text = data.decode('utf-8-sig')
    lines = text.splitlines(keepends=True)
    active, section_count, hits = False, 0, []
    for i, line in enumerate(lines):
        header = re.fullmatch(r'\s*\[([^\]]+)\]\s*(?:#.*)?(?:\r?\n)?', line)
        if header:
            active = header.group(1).strip().strip('"') == section
            section_count += int(active)
        elif active:
            m = re.match(r'^(\s*' + re.escape(key) + r'\s*=\s*)([^#\r\n]*)(.*)$', line.rstrip('\r\n'))
            if m:
                hits.append((i, m))
    if section_count != 1 or len(hits) != 1:
        raise ValueError('Expected exactly one section/key: ' + section + '.' + key)
    i, m = hits[0]
    ending = '\r\n' if lines[i].endswith('\r\n') else ('\n' if lines[i].endswith('\n') else '')
    lines[i] = m.group(1) + value + ((' ' + m.group(3)) if m.group(3) else '') + ending
    result = ''.join(lines).encode('utf-8')
    return (b'\xef\xbb\xbf' if data.startswith(b'\xef\xbb\xbf') else b'') + result

def write_json(p, data):
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

def outside(root, p):
    p = no_links(p)
    if p == root or root in p.parents:
        raise ValueError('Output must be outside the game installation')
    return p

def atomic_change(target, data, expected):
    no_links(target)
    if digest(target) != expected:
        raise ValueError('Target changed since inspection; refusing overwrite')
    fd, name = tempfile.mkstemp(prefix='.s1lab-', dir=target.parent)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(data); f.flush(); os.fsync(f.fileno())
        if digest(target) != expected:
            raise ValueError('Concurrent edit detected')
        os.replace(name, target)
    finally:
        if os.path.exists(name):
            os.unlink(name)
    if digest(target) != hashlib.sha256(data).hexdigest():
        raise RuntimeError('Post-write verification failed; retain backup')

def audit(root, out):
    root = root_checked(root); out = outside(root, out)
    out.mkdir(parents=True, exist_ok=False)
    data = {'root': str(root), 'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'identity': identity(root), 'read_only_game': True, 'performance_tested': False}
    excluded = {'freetp', 'usersaves', 'saves', 'defaultsave', 'defaulttutorialsave'}
    files = []
    for base, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = [d for d in dirs if d.lower() not in excluded and not (Path(base)/d).is_symlink()
                   and not (getattr((Path(base)/d).lstat(), 'st_file_attributes', 0) & 1024)]
        for name in names:
            p = Path(base)/name
            if p.is_symlink(): continue
            files.append({'path': str(p.relative_to(root)), 'bytes': p.stat().st_size})
    data['inventory'] = files
    data['active_mod_hashes'] = {p.name: digest(p) for p in sorted((root/'Mods').glob('*.dll')) if not p.is_symlink()}
    same = collections.defaultdict(list)
    for n, h in data['active_mod_hashes'].items(): same[h].append(n)
    data['identical_binary_groups'] = [n for n in same.values() if len(n)>1]
    data['backup_like_mods'] = [p.name for p in (root/'Mods').iterdir() if p.is_file() and '.bak' in p.name]
    data['addressables_filename_candidates'] = [f for f in files if re.search(r'(?i)(catalog.*\.(json|bin|hash)$|\.bundle$|addressables)', f['path'])]
    boot = root/'Schedule I_Data/boot.config'; baseline = boot.with_name('boot.config.orig')
    if baseline.is_file():
        data['boot_diff_against_unverified_local_orig'] = list(difflib.unified_diff(
            baseline.read_text(encoding='utf-8-sig').splitlines(), boot.read_text(encoding='utf-8-sig').splitlines(),
            fromfile='unverified local boot.config.orig', tofile='current boot.config', lineterm=''))
    meta = root/IDENTITY[3]
    with meta.open('rb') as f: magic, version = struct.unpack('<II', f.read(8))
    data['il2cpp_metadata_header'] = {'magic': hex(magic), 'version': version, 'standard_magic': magic == 0xFAB11BAF}
    pref = (root/TARGET).read_bytes()
    import tomllib
    parsed = tomllib.loads(pref.decode('utf-8-sig'))
    data['relevant_preferences'] = {k: parsed.get(k, {}) for k in ('S1Perf', 'ScheduleRu')}
    frames = root/'UserData/S1Perf/frametime.log'
    if frames.is_file():
        rows = []
        for line in frames.read_text(encoding='utf-8-sig').splitlines():
            m = re.search(r'avgFps=([\d.]+).*?p99=([\d.]+)ms.*?worst=([\d.]+)ms', line)
            if m: rows.append(tuple(map(float, m.groups())))
        data['historical_frametime_summary'] = {'records':len(rows),'uncontrolled_sessions':True,
            'min_reported_avg_fps':min((r[0] for r in rows), default=None),
            'max_reported_avg_fps':max((r[0] for r in rows), default=None),
            'largest_reported_frame_ms':max((r[2] for r in rows), default=None),
            'warning':'Not a baseline or A/B test. Reported 1% low is reciprocal p99, not mean slowest 1%.'}
    write_json(out/'audit.json', data)
    print('Audit saved: '+str(out/'audit.json'))

def prepare(root, out, profile):
    root = root_checked(root); out = outside(root, out)
    # Pin to the researched installation, not an arbitrary game/mod version.
    evidence = json.loads((HERE/'evidence/audit.json').read_text(encoding='utf-8'))
    current = identity(root)
    if current != evidence['identity']:
        raise ValueError('Game/mod fingerprint differs from the researched build')
    out.mkdir(parents=True, exist_ok=False)
    original = (root/TARGET).read_bytes()
    patched = replace_one(original, *PROFILES[profile])
    if original == patched: raise ValueError('Profile already applied; no new package needed')
    import tomllib
    tomllib.loads(patched.decode('utf-8-sig'))
    (out/'original.cfg').write_bytes(original)
    (out/'candidate.cfg').write_bytes(patched)
    manifest = {'root':str(root), 'target':str(TARGET), 'profile':profile, 'risk':RISKS[profile],
        'identity':current, 'before':hashlib.sha256(original).hexdigest(),
        'after':hashlib.sha256(patched).hexdigest(), 'applied':False, 'performance_tested':False}
    write_json(out/'manifest.json', manifest)
    diff = ''.join(difflib.unified_diff(original.decode('utf-8-sig').splitlines(True),
        patched.decode('utf-8-sig').splitlines(True), fromfile='current preferences', tofile=profile))
    (out/'changes.diff').write_text(diff, encoding='utf-8')
    print(diff); print(RISKS[profile]); print('Prepared only. Game unchanged.')

def transact(package, rollback=False, confirm=False):
    if not confirm: raise ValueError('Explicit --confirm required; read changes.diff and risks first')
    package = no_links(package)
    m = json.loads((package/'manifest.json').read_text(encoding='utf-8'))
    root = root_checked(m['root']); outside(root, package); ensure_stopped()
    if m['target'] != str(TARGET) or m['profile'] not in PROFILES:
        raise ValueError('Target/profile not allowed')
    if identity(root) != m['identity']:
        raise ValueError('Game or mod versions changed; refuse automatic changes')
    original = (package/'original.cfg').read_bytes(); candidate = (package/'candidate.cfg').read_bytes()
    if hashlib.sha256(original).hexdigest()!=m['before'] or hashlib.sha256(candidate).hexdigest()!=m['after']:
        raise ValueError('Package integrity failure')
    if replace_one(original, *PROFILES[m['profile']]) != candidate:
        raise ValueError('Candidate contains changes outside the selected allowlisted setting')
    if rollback:
        atomic_change(root/TARGET, original, m['after'])
    else:
        # Verify original backup before touching the target. It is already in this package.
        atomic_change(root/TARGET, candidate, m['before'])
    m['applied'] = not rollback
    write_json(package/'manifest.json', m)
    print('Rollback verified.' if rollback else 'Applied and verified. No game launched.')

def selftest():
    import unittest
    class Tests(unittest.TestCase):
        def test_edit(self):
            src=b'[ScheduleRu]\r\nCanvasScanInterval = 0.0\r\nOther = true\r\n'
            self.assertEqual(replace_one(src,*PROFILES['ui-scan']), b'[ScheduleRu]\r\nCanvasScanInterval = 0.05\r\nOther = true\r\n')
        def test_bom(self):
            self.assertTrue(replace_one(b'\xef\xbb\xbf[ScheduleRu]\nDumpUntranslated=true\n',*PROFILES['quiet-translation']).startswith(b'\xef\xbb\xbf'))
        def test_missing(self):
            with self.assertRaises(ValueError): replace_one(b'[Other]\na=1\n',*PROFILES['ui-scan'])
        def test_duplicate(self):
            with self.assertRaises(ValueError): replace_one(b'[ScheduleRu]\nCanvasScanInterval=0\nCanvasScanInterval=1\n',*PROFILES['ui-scan'])
        def test_sections(self):
            with self.assertRaises(ValueError): replace_one(b'[ScheduleRu]\nCanvasScanInterval=0\n[ScheduleRu]\n',*PROFILES['ui-scan'])
        def test_rollback(self):
            with tempfile.TemporaryDirectory() as d:
                p=Path(d)/'fixture.cfg'; p.write_bytes(b'original'); h=digest(p)
                atomic_change(p,b'candidate',h); atomic_change(p,b'original',digest(p))
                self.assertEqual(p.read_bytes(),b'original')
        def test_stale(self):
            with tempfile.TemporaryDirectory() as d:
                p=Path(d)/'fixture.cfg'; p.write_bytes(b'new user edit')
                with self.assertRaises(ValueError): atomic_change(p,b'candidate','bad-hash')
                self.assertEqual(p.read_bytes(),b'new user edit')
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    if not result.wasSuccessful(): raise SystemExit(1)

def main():
    a=argparse.ArgumentParser(description=__doc__)
    s=a.add_subparsers(dest='cmd',required=True)
    for name in ('audit','prepare'):
        p=s.add_parser(name); p.add_argument('--root',type=Path,default=Path(r'B:\Schedule I')); p.add_argument('--out',type=Path,required=True)
        if name=='prepare': p.add_argument('--profile',choices=PROFILES,required=True)
    for name in ('apply','rollback'):
        p=s.add_parser(name); p.add_argument('--package',type=Path,required=True); p.add_argument('--confirm',action='store_true')
    s.add_parser('selftest'); args=a.parse_args()
    if args.cmd=='audit': audit(args.root,args.out)
    elif args.cmd=='prepare': prepare(args.root,args.out,args.profile)
    elif args.cmd=='selftest': selftest()
    else: transact(args.package,args.cmd=='rollback',args.confirm)
if __name__=='__main__':
    try: main()
    except Exception as e: raise SystemExit('STOP: '+str(e))
