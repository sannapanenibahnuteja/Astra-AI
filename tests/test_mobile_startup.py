import json
from pathlib import Path
import shutil
import subprocess
import unittest
from desktop.mobile import HTML


class MobileStartupTests(unittest.TestCase):
    def test_phone_startup_handles_storage_history_missing_token_and_timeouts(self):
        node=shutil.which('node')
        if not node:self.fail('Node is required for phone client startup regression checks.')
        result=subprocess.run([node,str(Path(__file__).with_name('mobile_client.test.cjs'))],
            input=json.dumps(HTML),text=True,capture_output=True,timeout=15)
        self.assertEqual(result.returncode,0,result.stderr)
        report=json.loads(result.stdout)
        self.assertTrue(report['passed']);self.assertEqual(report['checks'],11)
