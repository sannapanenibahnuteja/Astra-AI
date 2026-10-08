import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

class PortablePackageTests(unittest.TestCase):
    def test_zip_keeps_support_folder_and_excludes_unrelated_runtime_data(self):
        with tempfile.TemporaryDirectory() as directory:
            release=Path(directory); bundle=release/'Bob'; internal=bundle/'_internal'/'models'
            internal.mkdir(parents=True)
            (bundle/'Bob.exe').write_bytes(b'fixture executable')
            (internal/'model.bin').write_bytes(b'fixture model')
            (bundle/'phone-calls.json').write_text('private runtime data')
            subprocess.run([sys.executable,'scripts/package-release.py','--release-dir',str(release)],check=True,capture_output=True)
            with ZipFile(release/'Bob-Windows-x64.zip') as archive:
                self.assertIn('Bob.exe',archive.namelist())
                self.assertIn('_internal/models/model.bin',archive.namelist())
                self.assertIn('Release-Notes.md',archive.namelist())
                self.assertNotIn('phone-calls.json',archive.namelist())
                self.assertIsNone(archive.testzip())

if __name__=='__main__': unittest.main()
