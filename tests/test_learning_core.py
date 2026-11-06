import json
import tempfile
import threading
import time
import unittest
from unittest.mock import Mock,patch
from desktop.storage import Store
from desktop.command_learning import CommandLearning,key
from desktop.semantic_memory import SemanticMemory,embedding
from desktop.expression import choose,prosody
from desktop.prompt import build_messages


class LearningCoreTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.store=Store(self.temp.name);self.cache=CommandLearning(self.store)
    def test_polite_variants_reuse_intent_not_old_result(self):
        plan={'action':'volume_down','target':'10','confirm':False}
        self.assertTrue(self.cache.learn('owner','Could you lower the volume a little?',plan))
        self.assertEqual(self.cache.lookup('owner','Please lower my volume a bit.'),{'action':'volume_down','target':'10'})
        self.assertIsNone(self.cache.lookup('other','Please lower my volume a bit.'))
        self.assertNotIn('result',json.dumps(self.cache.rows('owner')))
    def test_negation_numbers_opposites_and_context_do_not_collide(self):
        self.cache.learn('owner','set volume to 40',{'action':'volume','target':'40'})
        for text in ('set volume to 50','do not set volume to 40','set volume to 40 and open notepad','set it to 40'):
            self.assertIsNone(self.cache.lookup('owner',text))
        self.cache.learn('owner','lower volume',{'action':'volume_down','target':'10'})
        self.assertIsNone(self.cache.lookup('owner','raise volume'))
        self.assertEqual(key('Please set the volume to forty percent.'),key('set volume to 40'))
    def test_unsafe_or_contextual_plans_cannot_be_learned(self):
        for plan in ({'action':'file_recycle','target':'x'},{'action':'brightness','target':'40','display':'previous'},
                     {'action':'open','target':'C:/private.exe'},{'action':'volume','target':'40','confirm':True}):
            self.assertFalse(self.cache.learn('owner','Set volume to forty',plan))
    def test_conflicting_interpretations_fail_closed_and_clear_is_scoped(self):
        self.cache.learn('a','lower volume',{'action':'volume_down','target':'10'})
        self.cache.learn('a','please lower volume',{'action':'volume_down','target':'20'})
        self.assertIsNone(self.cache.lookup('a','lower volume'))
        self.cache.learn('b','lower volume',{'action':'volume_down','target':'10'})
        self.cache.clear('a');self.assertEqual(self.cache.rows('a'),[]);self.assertEqual(len(self.cache.rows('b')),1)
    def test_local_neural_embeddings_never_send_to_remote_ollama(self):
        with patch('desktop.semantic_memory.urllib.request.urlopen') as network:
            with self.assertRaises(ValueError):embedding('private fact','https://remote.example')
            network.assert_not_called()
    def test_neural_ranking_respects_profile_and_deleted_facts(self):
        memory=SemanticMemory(self.store)
        self.store.remember('diet','vegan','alice');self.store.remember('hobby','cycling','alice')
        def embed(text,*args,**kwargs):return [1.,0.] if 'diet' in text or 'dinner' in text else [0.,1.]
        with patch('desktop.semantic_memory.embedding',side_effect=embed),patch('desktop.semantic_memory.threading.Thread'):
            # Index synchronously to make the test independent of worker timing.
            memory.index_lock.acquire()
            import hashlib
            facts=self.store.memories('alice')
            memory._index('alice',[(f,f['key']+': '+f['value'],hashlib.sha256((f['key']+': '+f['value']).encode()).hexdigest()) for f in facts],'http://localhost:11434',0)
            ranked=memory.rank('alice','dinner suggestions',facts,'http://localhost:11434')
            self.assertGreater(ranked[0]['_semantic_score'],ranked[1]['_semantic_score'])
            self.assertEqual(memory.rank('bob','dinner',[],'http://localhost:11434'),[])
            self.store.forget('diet','alice')
            with self.store.connect() as db:self.assertIsNone(db.execute("SELECT 1 FROM memory_vectors WHERE scope='alice' AND key='diet'").fetchone())
    def test_offline_neural_retrieval_keeps_existing_facts(self):
        facts=[{'key':'diet','value':'vegan'}]
        with patch('desktop.semantic_memory.embedding',side_effect=TimeoutError):
            self.assertEqual(SemanticMemory(self.store).rank('owner','dinner',facts,'http://localhost:11434'),facts)
    def test_expression_is_bounded_explicit_and_escaped(self):
        self.assertEqual(choose('I feel stressed'),'calm')
        self.assertEqual(choose('Great news!'),'bright')
        self.assertEqual(choose('I am happy','serious'),'serious')
        self.assertEqual(choose('I am happy',enabled=False),'neutral')
        xml=prosody('A & B <audio src="x"/>','calm')
        self.assertIn('&lt;audio',xml);self.assertNotIn('<audio',xml)
        self.assertIn('rate="-8%"',xml)
    def test_semantic_scores_rank_facts_but_are_not_prompt_content(self):
        facts=[{'key':'a','value':'unrelated','_semantic_score':0.},{'key':'z','value':'important','_semantic_score':.9}]
        messages=build_messages('system',{'context_size':4096,'personality':''},facts,[],[{'role':'user','content':'question'}])
        self.assertLess(messages[0]['content'].index('important'),messages[0]['content'].index('unrelated'))
        self.assertNotIn('_semantic_score',messages[0]['content'])
