import hashlib,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import s1lab

class Transactions(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.base=Path(self.tmp.name)
        self.root=self.base/'game'; self.root.mkdir(); self.pkg=self.base/'package'; self.pkg.mkdir()
        for rel in s1lab.IDENTITY:
            p=self.root/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(b'fixture not executable')
        self.target=self.root/s1lab.TARGET; self.target.parent.mkdir(exist_ok=True)
        self.original=b'[ScheduleRu]\nCanvasScanInterval = 0.0\n'
        self.target.write_bytes(self.original)
        self.candidate=s1lab.replace_one(self.original,*s1lab.PROFILES['ui-scan'])
        (self.pkg/'original.cfg').write_bytes(self.original); (self.pkg/'candidate.cfg').write_bytes(self.candidate)
        self.manifest={'root':str(self.root),'target':str(s1lab.TARGET),'profile':'ui-scan','identity':s1lab.identity(self.root),
            'before':hashlib.sha256(self.original).hexdigest(),'after':hashlib.sha256(self.candidate).hexdigest(),'applied':False}
        s1lab.write_json(self.pkg/'manifest.json',self.manifest)
    def tearDown(self): self.tmp.cleanup()
    def test_full_apply_rollback_fixture(self):
        with patch.object(s1lab,'ensure_stopped'):
            s1lab.transact(self.pkg,confirm=True); self.assertEqual(self.target.read_bytes(),self.candidate)
            s1lab.transact(self.pkg,rollback=True,confirm=True); self.assertEqual(self.target.read_bytes(),self.original)
    def test_confirmation_required(self):
        with self.assertRaises(ValueError):s1lab.transact(self.pkg)
        self.assertEqual(self.target.read_bytes(),self.original)
    def test_running_game_blocks(self):
        with patch.object(s1lab,'ensure_stopped',side_effect=RuntimeError('running')):
            with self.assertRaises(RuntimeError):s1lab.transact(self.pkg,confirm=True)
        self.assertEqual(self.target.read_bytes(),self.original)
    def test_changed_binary_blocks(self):
        (self.root/s1lab.IDENTITY[0]).write_bytes(b'new version')
        with patch.object(s1lab,'ensure_stopped'):
            with self.assertRaises(ValueError):s1lab.transact(self.pkg,confirm=True)
    def test_extra_patch_blocks_even_with_updated_hash(self):
        bad=self.candidate+b'DumpUntranslated=false\n'; (self.pkg/'candidate.cfg').write_bytes(bad)
        self.manifest['after']=hashlib.sha256(bad).hexdigest();s1lab.write_json(self.pkg/'manifest.json',self.manifest)
        with patch.object(s1lab,'ensure_stopped'):
            with self.assertRaises(ValueError):s1lab.transact(self.pkg,confirm=True)
        self.assertEqual(self.target.read_bytes(),self.original)
    def test_changed_preferences_blocks(self):
        self.target.write_bytes(self.original+b'# user change\n')
        with patch.object(s1lab,'ensure_stopped'):
            with self.assertRaises(ValueError):s1lab.transact(self.pkg,confirm=True)
    def test_target_escape_blocks(self):
        self.manifest['target']='../outside';s1lab.write_json(self.pkg/'manifest.json',self.manifest)
        with patch.object(s1lab,'ensure_stopped'):
            with self.assertRaises(ValueError):s1lab.transact(self.pkg,confirm=True)
if __name__=='__main__':unittest.main(verbosity=2)
