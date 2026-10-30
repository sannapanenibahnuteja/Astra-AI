import math
import unittest
from unittest.mock import Mock
from desktop.conversational import QualityMetrics
from desktop.reliability import TurnTrace, ExpectedReply, latency_report, percentiles
from desktop.duplex_audio import DuplexAudio


class ReliabilityTests(unittest.TestCase):
    def answer(self,text='seven thirty',owner='fixture',confidence=.95):
        return {'text':text,'confidence':confidence,'needs_review':False,'speaker':{'state':'matched','profile_id':owner}}

    def test_expected_answer_is_narrow_same_owner_and_one_use(self):
        expected=ExpectedReply(clock=lambda:1.)
        expected.arm('What time?', 'fixture')
        self.assertFalse(expected.accepts(self.answer(owner='other')))
        self.assertFalse(expected.accepts(self.answer(confidence=.6)))
        self.assertFalse(expected.accepts(self.answer('open calculator')))
        self.assertTrue(expected.accepts(self.answer()))
        self.assertFalse(expected.accepts(self.answer()))

    def test_expected_answer_expiry_and_unrecognized_question_fail_closed(self):
        clock=[1.];expected=ExpectedReply(clock=lambda:clock[0])
        expected.arm('Which day?', 'fixture');clock[0]=14.
        self.assertFalse(expected.accepts(self.answer('tomorrow')))
        expected.arm('Tell me about yourself?', 'fixture')
        self.assertFalse(expected.accepts(self.answer('yes')))
        expected.arm('Should I send it?', '')
        self.assertFalse(expected.accepts(self.answer('yes')))

    def test_voice_trigger_allows_expected_answer_but_not_ambient_commands(self):
        from desktop.voice import Voice
        voice=Voice();self.addCleanup(voice.close);voice.speaker_enabled=True
        voice.expected_reply.arm('Which one?', 'fixture')
        self.assertTrue(voice.filter_voice_trigger(self.answer('open calculator'))['ignored'])
        self.assertTrue(voice.filter_voice_trigger(self.answer('the second one'))['expected_reply'])
        self.assertTrue(voice.filter_voice_trigger(self.answer('the second one'))['ignored'])

    def test_tail_latency_keeps_slow_cases_and_ignores_invalid_samples(self):
        metrics=QualityMetrics()
        for value in range(1,101):metrics.timing('test',value)
        metrics.timing('test',float('nan'));metrics.timing('test',float('inf'));metrics.timing('test',-10)
        row=metrics.snapshot()['latency_ms']['test']
        self.assertEqual(row['samples'],64)
        self.assertEqual(row['max'],100)
        self.assertEqual(row['p50'],68)
        self.assertEqual(row['p95'],97)
        self.assertEqual(row['p99'],100)

    def test_budget_never_fabricates_unobserved_stages(self):
        report=latency_report({'latency_ms':{'endpoint_latency':{'p95':650}}})
        self.assertEqual(len(report),12)
        self.assertEqual(report['endpoint_latency']['status'],'above_target')
        self.assertEqual(report['total_turn_latency']['status'],'unmeasured')
        self.assertIsNone(report['total_turn_latency']['observed'])

    def test_valid_capture_trace_replays_without_actions(self):
        trace=TurnTrace(clock=lambda:5.)
        for state in ('CAPTURING','VERIFYING','TRANSCRIBING','READY','IDLE'):
            self.assertTrue(trace.transition(state))
        replay=trace.replay(trace.snapshot()['events'])
        self.assertTrue(replay['passed']);self.assertEqual(replay['actions_executed'],0)

    def test_capture_cannot_jump_to_idle_while_endpoint_is_pending(self):
        trace=TurnTrace()
        trace.transition('CAPTURING')
        self.assertFalse(trace.transition('IDLE'))
        self.assertEqual(trace.state,'CAPTURING')
        self.assertFalse(trace.replay(trace.snapshot()['events'])['passed'])

    def test_trace_is_bounded_and_rejects_personal_content(self):
        trace=TurnTrace()
        for _ in range(100):
            trace.transition('CAPTURING');trace.transition('RECOVERY','no_words');trace.transition('IDLE')
        self.assertEqual(len(trace.snapshot()['events']),128)
        with self.assertRaises(ValueError):trace.transition('RECOVERY','a private transcript')
        self.assertTrue(trace.replay(trace.snapshot()['events'])['passed'])

    def test_stream_stall_reports_failure_without_submitting_a_turn(self):
        import time
        engine=DuplexAudio(Mock(),Mock())
        engine.stream=object();engine.last_callback_at=time.monotonic()-4
        engine._queue_turn=Mock()
        try:engine._work()
        finally:engine.stream=None;engine.close()
        self.assertIn('stopped arriving',engine.error)
        engine._queue_turn.assert_not_called()

    def test_cancel_recovery_and_percentiles_have_no_synthetic_scores(self):
        trace=TurnTrace()
        trace.transition('CAPTURING');trace.transition('RECOVERY','cancelled');trace.transition('IDLE')
        self.assertTrue(trace.replay(trace.snapshot()['events'])['passed'])
        self.assertEqual(percentiles([math.nan,-1]),{})
