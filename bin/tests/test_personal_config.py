import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest


spec = importlib.util.spec_from_file_location(
    "personal_config", Path(__file__).resolve().parents[1] / "sync-personal-agent-config.py")
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)


class PersonalConfigTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="rig-config-test-")
        self.addCleanup(temp.cleanup)
        self.root, self.home = Path(temp.name) / "rig", Path(temp.name) / "home"
        for relative, source in config.FILES.items():
            path = self.root / source
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('model = "default"\n' if path.suffix == ".toml" else '{"setting": "default"}\n')

    def sync(self, apply=True, detach_only=False):
        with contextlib.redirect_stdout(io.StringIO()):
            return config.sync(self.root, self.home, apply, detach_only)

    def test_initial_install_and_idempotence(self):
        self.assertGreater(self.sync(False), 0)
        self.assertFalse(self.home.exists())
        self.sync()
        for relative in config.FILES:
            path = self.home / relative
            self.assertTrue(path.is_file())
            self.assertFalse(path.is_symlink())
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.sync(), 0)

    def test_detach_then_clean_defaults_keeps_runtime_bytes_and_backups(self):
        source = self.root / 'codex/config.toml'
        source.write_text('model = "default"\n[projects.private]\ntrust_level = "trusted"\n')
        target = self.home / '.codex-personal/config.toml'
        target.parent.mkdir(parents=True)
        target.symlink_to(source)
        before = source.read_text()
        self.sync(detach_only=True)
        self.assertFalse(target.is_symlink())
        self.assertEqual(target.read_text(), before)
        source.write_text('model = "default"\n')
        self.sync()
        self.assertEqual(target.read_text(), before)
        backups = list((self.home / '.local/state/rig-agent-config').glob('backup-*/.codex-personal/config.toml'))
        self.assertEqual(backups[0].read_text(), before)
        self.assertEqual(source.read_text(), 'model = "default"\n')

    def test_changed_default_updates_unmodified_setting_but_preserves_override(self):
        self.sync()
        (self.root / 'codex/config.toml').write_text('model = "next"\n')
        target = self.home / '.claude-personal/settings.json'
        target.write_text('{"setting": "local", "runtime": true}\n')
        (self.root / 'claude/settings.json').write_text('{"setting": "next", "added": 1}\n')
        self.sync()
        self.assertEqual(config.parse(Path('config.toml'), (self.home / '.codex-personal/config.toml').read_text()),
                         {'model': 'next'})
        self.assertEqual(json.loads(target.read_text()), {'setting': 'local', 'runtime': True, 'added': 1})
        self.assertEqual(self.sync(), 0)

    def test_removed_default_and_local_deletion(self):
        self.assertEqual(config.merge({'a': 1, 'b': 2}, {'a': 3}, {'b': 2, 'runtime': 4}), {'runtime': 4})
        self.assertEqual(config.merge({'a': 1}, {}, {'a': 2}), {'a': 2})

    def test_unknown_symlink_and_invalid_config_fail_before_writes(self):
        target = self.home / '.codex-personal/config.toml'
        target.parent.mkdir(parents=True)
        other = self.root / 'other.toml'
        other.write_text('model = "other"\n')
        target.symlink_to(other)
        with self.assertRaises(ValueError):
            self.sync()
        self.assertFalse((self.home / '.claude-personal/settings.json').exists())
        target.unlink()
        target.write_text('invalid toml !')
        with self.assertRaises(ValueError):
            self.sync()
        self.assertFalse((self.home / '.local/state').exists())

    def test_runtime_write_does_not_change_repo_or_work_profile(self):
        work = self.home / '.codex/config.toml'
        work.parent.mkdir(parents=True)
        work.write_text('model = "work"\n')
        self.sync()
        (self.home / '.codex-personal/config.toml').write_text('model = "runtime"\n')
        self.assertEqual((self.root / 'codex/config.toml').read_text(), 'model = "default"\n')
        self.assertEqual(work.read_text(), 'model = "work"\n')


if __name__ == '__main__':
    unittest.main()
