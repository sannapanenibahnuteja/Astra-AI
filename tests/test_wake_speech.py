import unittest
from unittest.mock import Mock, patch
from desktop.voice import Voice
from desktop.voice_triggers import split_wake, session_stop
from desktop.interruption import intended_interruption
from desktop.speech_output import spoken_text, speech_chunks
from desktop.conversational import SpeechBudget, response_plan
from desktop.reply_audio import ReplyAudio
import threading


class WakePhraseTests(unittest.TestCase):
    def setUp(self):
        self.voice=Voice()

    def result(self,text,**values):
        return self.voice.filter_voice_trigger(dict(text=text,confidence=.96,needs_review=False,**values))

    def test_default_rejects_untriggered_chatter_even_from_known_user(self):
        self.assertTrue(self.voice.audio_options['audio_wake_phrase_only'])
        for text in ('open YouTube','Actually, open calculator','Shorter','Bob, open calculator','blah blah'):
            self.assertTrue(self.result(text)['trigger_required'])

    def test_prefix_removed_once_and_payload_preserved(self):
        for prefix in ('Hey Bob, ','Okay Bob: ','OK Bob ','Hey, Bob. '):
            self.assertEqual(self.result(prefix+'type Hey Bob in Notepad')['text'],'type Hey Bob in Notepad')

    def test_wake_only_arms_exactly_one_next_request(self):
        self.assertTrue(self.result('Hey Bob')['wake_triggered'])
        self.assertEqual(self.result('Open YouTube')['text'],'Open YouTube')
        self.assertTrue(self.result('Close YouTube')['trigger_required'])

    def test_expired_window_rejects_speech(self):
        self.voice.arm_wake();self.voice._wake_until=0
        self.assertTrue(self.result('Open YouTube')['ignored'])

    def test_slow_decode_retains_permission_from_capture_start(self):
        self.voice.arm_wake();armed=self.voice.wake_window_open();self.voice._wake_until=0
        result=self.voice.filter_voice_trigger(dict(text='open YouTube',confidence=.95,needs_review=False),armed=armed)
        self.assertEqual(result['text'],'open YouTube')
        self.assertTrue(self.result('close YouTube')['trigger_required'])

    def test_uncertain_wake_cannot_arm_or_dispatch(self):
        for confidence,review in ((.79,False),(.99,True)):
            value=self.voice.filter_voice_trigger(dict(text='Hey Bob, open YouTube',confidence=confidence,needs_review=review))
            self.assertTrue(value['ignored']);self.assertFalse(self.voice.wake_window_open())

    def test_explicit_session_stop_without_prefix(self):
        self.assertEqual(self.result('Stop listening.')['text'],'stop listening')
        self.assertFalse(session_stop('stop listening and open YouTube'))

    def test_interruption_requires_trigger_and_confident_meaningful_speech(self):
        for text in ('Hey Bob','Okay Bob','Shorter','Actually open calculator','No I meant Friday','Bob banana','Hey Bob flibber wibble'):
            self.assertFalse(intended_interruption(text,.99,False,require_trigger=True),text)
        for text in ('Okay Bob, shorter','Hey Bob open calculator','Bob please stop talking','Stop listening','Go to sleep'):
            self.assertTrue(intended_interruption(text,.99,False,require_trigger=True),text)
        self.assertFalse(intended_interruption('Hey Bob',.7,False,require_trigger=True))

    def test_wake_only_interruption_arms_next_request_without_reply_control_leak(self):
        self.assertTrue(self.result('Hey Bob',interrupted_reply=True)['wake_triggered'])
        result=self.result('please stop talking')
        self.assertEqual(result['text'],'');self.assertEqual(result['interruption_control'],'stop_reply')

    def test_off_is_explicit_opt_out_and_payload_not_mutated(self):
        self.voice.audio_options['audio_wake_phrase_only']=False
        self.assertEqual(self.result('Actually open YouTube')['text'],'Actually open YouTube')
        self.assertEqual(split_wake('type Hey Bob in Notepad'),(False,'type Hey Bob in Notepad'))

    def test_wake_mode_keeps_authorization_even_if_older_guard_off(self):
        self.voice.audio_options['audio_verified_interruptions']=False
        engine=Mock();self.voice.configure_interruptions(engine)
        self.assertEqual(engine.authorize_interrupt,self.voice._authorize_interrupt)


class CompleteSpeechTests(unittest.TestCase):
    def text(self):
        return ' '.join(f'Sentence {i} has enough words to exceed the previous speech budget.' for i in range(100))

    def test_full_prose_over_five_thousand_characters_survives(self):
        text=self.text();self.assertGreater(len(text),5000)
        self.assertEqual(spoken_text(text),text)
        for mode in ('normal','fast','driving','tutor'):
            self.assertEqual(SpeechBudget(response_plan(mode)).take(text),text)

    def test_streamed_answer_speaks_every_sentence_and_final_tail_once(self):
        text=self.text()+' Final words without punctuation';heard=[];budget=SpeechBudget(response_plan('fast'))
        stream=ReplyAudio(lambda value:heard.append(budget.take(value)),threading.Event())
        for offset in range(0,len(text),23):stream.add(text[offset:offset+23])
        stream.add('',flush=True);stream.finish()
        self.assertEqual(' '.join(heard),text)

    def test_render_chunks_are_bounded_and_preserve_all_words(self):
        text=self.text();parts=list(speech_chunks(text))
        self.assertGreater(len(parts),3);self.assertTrue(all(len(part)<=1800 for part in parts))
        self.assertEqual(' '.join(parts),text)
        self.assertEqual(''.join(speech_chunks('z'*5500)),'z'*5500)

    def test_voice_renders_and_plays_all_chunks(self):
        voice=Voice();engine=Mock();engine.last_interrupted_serial=engine.acknowledged_serial=0
        voice._ensure_duplex=Mock(return_value=engine);voice._pause_wake=Mock()
        worker=Mock();worker.render.return_value=b'RIFFfixture';voice._speech_worker=Mock(return_value=worker)
        text=self.text()
        self.assertTrue(voice.speak(text,0))
        self.assertEqual(' '.join(call.args[0] for call in worker.render.call_args_list),text)
        self.assertEqual(engine.play.call_count,worker.render.call_count)

    def test_cancel_between_render_chunks_stops_remaining_output(self):
        voice=Voice();engine=Mock();engine.last_interrupted_serial=engine.acknowledged_serial=0
        voice._ensure_duplex=Mock(return_value=engine);voice._pause_wake=Mock()
        worker=Mock();worker.render.return_value=b'RIFFfixture';voice._speech_worker=Mock(return_value=worker)
        engine.play.side_effect=lambda *args:voice._speech_interrupted.set()
        self.assertFalse(voice.speak(self.text(),0));self.assertEqual(worker.render.call_count,1)


if __name__=='__main__':unittest.main()
