"""Spoken task interpretation belongs to Ollama, never the raw phrase parser."""
import tempfile
import json
import time
import unittest
from unittest.mock import Mock, patch
from desktop.runtime import Runtime


def response(*actions, text='Finished.'):
    message = {'tool_calls':[{'function':{'name':'windows_action','arguments':action}} for action in actions]} if actions else {'content':text}
    model=Mock(); model.stream.return_value=iter([{'message':message,'done':True}]); return model


class SemanticVoiceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.runtime=Runtime(self.temp.name); self.addCleanup(self.runtime._voice.close)
        self.runtime.save_settings({'voice_enabled':False})
        self.identity=self.runtime.new_conversation()

    def send(self, text):
        job=self.runtime.start_chat(self.identity,text,True)
        for _ in range(500):
            value=self.runtime.poll_chat(job)
            if value['done']: return value
            time.sleep(.01)
        self.fail('Semantic voice fixture timed out')

    def test_known_voice_phrase_still_goes_to_model_first(self):
        with patch.object(self.runtime._commands,'plan',side_effect=AssertionError('Do not parse raw speech')), patch.object(self.runtime._commands,'execute',return_value='Volume set to 20%.') as execute, patch('desktop.runtime.ChatConnection',side_effect=[response({'action':'volume','target':'20'}),response()]) as model:
            result=self.send('Set the volume to twenty percent')
        self.assertEqual(result['steps'],1); self.assertEqual(result['error'],'')
        self.assertEqual(execute.call_args.args[0]['target'],'20')
        self.assertIn('Set the volume to twenty percent',str(model.call_args_list[0].args[1]['messages']))

    def test_casual_compound_intent_and_literal_dictation(self):
        literal='Wait, actually do not close anything!'
        actions=[{'action':'volume_down','target':''},{'action':'type_text','target':literal,'window':'Notepad'}]
        with patch.object(self.runtime._commands,'plan',side_effect=AssertionError('Do not parse raw speech')), patch.object(self.runtime._commands,'execute',side_effect=['Volume lowered.','Typed the literal text.']) as execute, patch('desktop.runtime.ChatConnection',side_effect=[response(*actions),response()]) as model:
            result=self.send('It is too loud; bring it down a little and put this in Notepad: '+literal)
        self.assertEqual(result['steps'],2)
        self.assertEqual(execute.call_args_list[1].args[0]['target'],literal)
        self.assertIn('meaning',str(model.call_args_list[0].args[1]['messages']))

    def test_spoken_correction_and_action_history_reach_model_unchanged(self):
        self.runtime._store.record_action(self.identity,{'action':'volume','target':'40'},'Volume set to 40%.')
        with patch.object(self.runtime._commands,'plan',side_effect=AssertionError('Do not parse correction')), patch.object(self.runtime._commands,'execute',return_value='Volume set to 20%.'), patch('desktop.runtime.ChatConnection',side_effect=[response({'action':'volume','target':'20'}),response()]) as model:
            result=self.send('No, I meant twenty')
        payload=model.call_args_list[0].args[1]
        self.assertIn('No, I meant twenty',str(payload['messages']))
        self.assertIn('Volume set to 40%',str(payload['messages']))
        self.assertEqual(result['steps'],1)

    def test_ambiguous_model_reply_is_preserved_without_generic_parser_reply(self):
        with patch.object(self.runtime._commands,'execute') as execute, patch('desktop.runtime.ChatConnection',return_value=response(text='Which window should I move?')):
            result=self.send('Move it over there')
        self.assertEqual(result['text'],'Which window should I move?'); execute.assert_not_called()

    def test_missing_model_never_falls_back_to_guessing(self):
        with patch.object(self.runtime._commands,'plan') as parser, patch.object(self.runtime._commands,'execute') as execute, patch('desktop.runtime.ChatConnection',side_effect=ConnectionError('Start Ollama first.')):
            result=self.send('Mute')
        parser.assert_not_called(); execute.assert_not_called()
        self.assertIn('Start Ollama',result['error'])

    def test_unsupported_tool_and_unverified_claim_do_not_execute(self):
        for model in [response({'action':'run_arbitrary_shell','target':'whatever'}),response(text='I opened YouTube.')]:
            with patch.object(self.runtime._commands,'execute') as execute, patch('desktop.runtime.ChatConnection',return_value=model):
                result=self.send('Get YouTube up')
            execute.assert_not_called()
            self.assertTrue(result['error'] or 'Nothing was changed' in result['text'])

    def test_model_tab_pronouns_reuse_frozen_selection(self):
        rows=[{'handle':1,'id':[1],'title':'YouTube'},{'handle':2,'id':[2],'title':'Video - YouTube'}]
        self.runtime._store.context(self.identity,{'last_window':'Microsoft Edge','tab_reference':{'query':'youtube','tabs':rows,'time':time.time()}})
        step=self.runtime._commands.validate_model_action({'action':'edge_close_tabs','target':'those'},self.identity)
        self.assertEqual(step['tabs'],rows); self.assertEqual(step['target'],'youtube'); self.assertTrue(step['confirm'])
        self.runtime._store.context(self.identity,{})
        step=self.runtime._commands.validate_model_action({'action':'edge_close_tabs','target':'those'},self.identity)
        self.assertEqual(step['action'],'clarify')

    def test_information_like_spoken_task_keeps_tools_available(self):
        with patch('desktop.runtime.ChatConnection',return_value=response(text='Which day should I plan?')) as model:
            result=self.send('What is the best way to manage my day?')
        self.assertTrue(model.call_args.args[1]['tools']); self.assertEqual(result['error'],'')

    def test_final_action_reports_native_result_without_second_model_round(self):
        with patch.object(self.runtime._commands,'execute',return_value='Volume lowered.') as execute, patch('desktop.runtime.ChatConnection',return_value=response({'action':'volume_down','target':'','final_step':True})) as model:
            result=self.send('It is too loud; bring it down a little')
        self.assertEqual(model.call_count,1); self.assertEqual(execute.call_count,1)
        self.assertEqual(result['text'],'Volume lowered.'); self.assertEqual(result['error'],'')
        self.assertEqual(model.call_args.args[1]['options']['num_predict'],512)

    def test_final_action_still_stops_on_native_failure(self):
        with patch.object(self.runtime._commands,'execute',side_effect=RuntimeError('Device did not change')), patch('desktop.runtime.ChatConnection',return_value=response({'action':'volume_down','target':'','final_step':True})) as model:
            result=self.send('Bring the sound down a little')
        self.assertEqual(model.call_count,1); self.assertIn('Device did not change',result['error'])
        self.assertEqual(result['steps'],0)

    def test_final_flag_survives_approval_without_replanning(self):
        with patch.object(self.runtime._commands,'execute',return_value='Locked.') as execute, patch('desktop.runtime.ChatConnection',return_value=response({'action':'lock','target':'','final_step':True})) as model:
            waiting=self.send('Secure my computer')
            execute.assert_not_called(); self.assertIn('Should I',waiting['text'])
            done=self.send('Yes')
        self.assertEqual(model.call_count,1); self.assertEqual(execute.call_count,1)
        self.assertEqual(done['text'],'Locked.')

    def test_structured_intent_is_validated_and_reply_cannot_fake_success(self):
        plan={'intent':'action','actions':[{'action':'volume','target':'20','final_step':True}],'reply':'I changed everything.'}
        with patch.object(self.runtime._commands,'execute',return_value='Volume set to 20%.') as execute, patch('desktop.runtime.ChatConnection',return_value=response(text=json.dumps(plan))) as model:
            result=self.send('Could you bring the sound to twenty?')
        self.assertEqual(result['text'],'Volume set to 20%.'); self.assertEqual(model.call_count,1)
        self.assertEqual(execute.call_args.args[0]['target'],'20')
        self.assertIn('format',model.call_args.args[1]); self.assertEqual(model.call_args.args[1]['tools'],[])

    def test_conversation_plan_cannot_smuggle_actions(self):
        for plan in ['{bad',json.dumps({'intent':'conversation','actions':[{'action':'volume','target':'20','final_step':True}],'reply':'Just explaining.'})]:
            with patch.object(self.runtime._commands,'execute') as execute, patch('desktop.runtime.ChatConnection',return_value=response(text=plan)):
                result=self.send('I would like the sound adjusted')
            execute.assert_not_called(); self.assertIn('invalid voice plan',result['error'])


if __name__=='__main__': unittest.main()
