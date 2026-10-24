import json
import unittest

from desktop.readiness import report


class ReadinessTests(unittest.TestCase):
    def run_report(self, **overrides):
        probes = dict(settings={}, ollama=lambda: {'online': True, 'ready': True},
                      speech=lambda: True, microphone=lambda: {'calibrated': True},
                      output=lambda: True)
        probes.update(overrides)
        return report(**probes)

    def test_core_available_and_no_inferred_voice_identity(self):
        result = self.run_report()
        self.assertTrue(result['core_ready'])
        self.assertEqual(result['ready_count'], 4)
        self.assertEqual(result['checks'][-1]['state'], 'optional')

    def test_offline_model_is_not_ready_even_with_stale_ready_flag(self):
        result = self.run_report(ollama=lambda: {'online': False, 'ready': True})
        self.assertFalse(result['core_ready'])
        self.assertEqual(result['ready_count'], 3)

    def test_failed_probes_are_isolated_and_errors_never_leak(self):
        def fail():
            raise RuntimeError('secret-token private-path private-person')
        result = self.run_report(ollama=fail, speech=fail, microphone=fail, output=fail)
        self.assertEqual(result['ready_count'], 0)
        self.assertEqual(len(result['checks']), 6)
        self.assertNotIn('secret-token', json.dumps(result))
        self.assertNotIn('private-path', json.dumps(result))

    def test_support_summary_is_allowlisted(self):
        result = self.run_report(
            settings={'auth_token': 'SECRET', 'speaker_enabled': True},
            ollama=lambda: {'online': True, 'ready': True, 'models': ['PRIVATE'], 'detail': 'SECRET'},
            microphone=lambda: {'name': 'PRIVATE DEVICE', 'calibrated': False})
        serialized = json.dumps(result)
        self.assertNotIn('SECRET', serialized)
        self.assertNotIn('PRIVATE', serialized)
        summary = json.loads(result['support_summary'])
        self.assertEqual(set(summary), {'schema', 'application', 'checks', 'scope'})
        self.assertEqual(summary['checks']['calibration'], 'optional')

    def test_each_probe_runs_once_only(self):
        calls = []
        def probe(name, value):
            def run():
                calls.append(name)
                return value
            return run
        self.run_report(ollama=probe('model', {'online': True, 'ready': True}),
                        speech=probe('speech', True), microphone=probe('mic', {}),
                        output=probe('output', True))
        self.assertEqual(calls, ['model', 'speech', 'mic', 'output'])


if __name__ == '__main__':
    unittest.main()
