"""Run every desktop regression and record each outcome without private user data."""
import argparse
import json
import sys
import time
import unittest
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
parser=argparse.ArgumentParser();parser.add_argument('--output',default=str(root/'.cache/release-tests.json'));args=parser.parse_args()
class Results(unittest.TextTestResult):
    def __init__(self,*args,**kwargs): super().__init__(*args,**kwargs);self.checks=[]
    def addSuccess(self,test): super().addSuccess(test);self.checks.append({'test':test.id(),'status':'passed'})
    def addFailure(self,test,error): super().addFailure(test,error);self.checks.append({'test':test.id(),'status':'failed'})
    def addError(self,test,error): super().addError(test,error);self.checks.append({'test':test.id(),'status':'error'})
    def addSkip(self,test,reason): super().addSkip(test,reason);self.checks.append({'test':test.id(),'status':'skipped','reason':reason})
    def addSubTest(self,test,subtest,error):
        super().addSubTest(test,subtest,error)
        self.checks.append({'test':subtest.id(),'status':'passed' if error is None else 'failed'})
start=time.monotonic()
suite=unittest.defaultTestLoader.discover(str(root/'tests'),pattern='test_*.py')
result=unittest.TextTestRunner(resultclass=Results,verbosity=1).run(suite)
output=Path(args.output);output.parent.mkdir(parents=True,exist_ok=True)
output.write_text(json.dumps({'passed':result.wasSuccessful(),'tests':result.testsRun,'seconds':round(time.monotonic()-start,2),'checks':result.checks},indent=2),encoding='utf-8')
print('Per-check results:',output)
sys.exit(0 if result.wasSuccessful() else 1)
