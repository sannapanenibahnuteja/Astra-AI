import tempfile
import unittest
from desktop.storage import Store
from desktop.personal_memory import facts, learn
from desktop.runtime import Runtime


class PersonalMemoryTests(unittest.TestCase):
    def test_natural_facts_and_relationships(self):
        self.assertEqual(facts('My favourite food is dosa. Alex is my brother.'),[('favorite food','dosa'),('relationship: alex','brother')])
        self.assertEqual(facts('My sister is Maya'),[('relationship: maya','sister')])
        self.assertEqual(facts('I usually exercise in the morning'),[('routine','exercise in the morning')])
        self.assertFalse(facts('I do not like coffee'))
        self.assertFalse(facts('For example my name is Alex'))
        self.assertFalse(facts('My password is secret'))

    def test_profiles_do_not_share_memories(self):
        with tempfile.TemporaryDirectory() as root:
            store=Store(root); a=store.voice_conversation('alex'); b=store.voice_conversation('maya')
            learn(store,a,'My favorite food is dosa',{'state':'matched','profile_id':'alex'},True)
            learn(store,b,'My favorite food is pasta',{'state':'matched','profile_id':'maya'},True)
            self.assertEqual(store.memories('alex'),[{'key':'favorite food','value':'dosa'}])
            self.assertEqual(store.memories('maya'),[{'key':'favorite food','value':'pasta'}])
            self.assertEqual(store.memories(),[])
            self.assertEqual(learn(store,a,'I love tea',{'state':'uncertain'},True),[])
            self.assertEqual(learn(store,a,'I love tea',{'state':'matched','profile_id':'maya'},True),[])
            store.save_settings({'conversation_memory':False})
            self.assertEqual(learn(store,a,'I love tea',{'state':'matched','profile_id':'alex'},True),[])

    def test_uncertain_voice_does_not_reuse_previous_users_chat(self):
        with tempfile.TemporaryDirectory() as root:
            runtime=Runtime(root); runtime._voice.speaker_enabled=True
            old=runtime._store.voice_conversation('alex')
            new=runtime.voice_conversation(old,{'state':'uncertain'})
            self.assertNotEqual(old,new)
            self.assertEqual(runtime._store.context(new),{'unidentified_voice':True})
            self.assertEqual(runtime.voice_conversation(new,{'state':'uncertain'}),new)
            runtime._pending[old]={'steps':[{'action':'lock','target':''}]}
            self.assertEqual(runtime.voice_conversation(old,{'state':'uncertain'},'yes'),old)
            self.assertNotEqual(runtime.voice_conversation(old,{'state':'uncertain'},'Tell me about my family'),old)
            with self.assertRaisesRegex(ValueError,'uncertain'):
                runtime._commands.execute({'action':'remember','target':'food: tea'},new)
