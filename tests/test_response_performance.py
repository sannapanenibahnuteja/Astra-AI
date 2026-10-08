import tempfile
import time
import unittest
from unittest.mock import Mock,patch
from desktop.runtime import Runtime,TOOLS
from desktop import conversation

class ResponsePerformanceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.runtime=Runtime(self.temp.name); self.identity=self.runtime.new_conversation()

    def request(self,text):
        model=Mock();model.stream.return_value=iter([{'message':{'content':'Here is the answer.'},'done':True}])
        with patch('desktop.runtime.ChatConnection',return_value=model) as connection:
            job=self.runtime.start_chat(self.identity,text)
            for _ in range(500):
                result=self.runtime.poll_chat(job)
                if result['done']: break
                time.sleep(.01)
            self.assertTrue(result['done'])
            return connection.call_args.args[1]

    def test_greetings_and_questions_keep_memory_without_tool_overhead(self):
        self.runtime._store.remember('favorite subject','astronomy')
        payload=self.request('Hello Bob')
        self.assertEqual(payload['tools'],[])
        self.assertIn('astronomy',str(payload['messages']))
        self.assertNotIn('Some available apps:\ncalculator',str(payload['messages']))
        self.assertTrue(payload['messages'][0]['content'].index('Current local time:')>payload['messages'][0]['content'].index('You are Bob'))
        self.assertEqual(self.request('What are black holes?')['tools'],[])

    def test_mixed_action_requests_do_not_take_information_shortcut(self):
        for text in ['Tell me about cats and open youtube','What is the weather and remind me at 9','Hello Bob and close youtube','How can you move that window','Do the same thing again']:
            self.assertFalse(conversation.information_request(text),text)
        self.assertEqual(self.request('Could you organize my workspace?')['tools'],TOOLS)

if __name__=='__main__': unittest.main()
