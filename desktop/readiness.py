"""On-demand setup checks. Never capture audio, load models or expose user data."""
import json


def report(settings, ollama, speech, microphone, output):
    checks = []

    def add(key, title, state, detail, action='settings'):
        checks.append(dict(id=key, title=title, state=state, detail=detail, action=action))

    try:
        status = ollama()
        ready = bool(status.get('online') and status.get('ready'))
        detail = ('Selected model is installed. Tool compatibility and speed still depend on the model.'
                  if ready else 'Start Ollama, download a model, then select its exact name in Settings.')
        add('model', 'Local intelligence', 'ready' if ready else 'attention', detail)
    except Exception:
        add('model', 'Local intelligence', 'attention', 'Connection check failed. Review Local intelligence in Settings.')
    try:
        speech()
        add('speech', 'Offline transcription files', 'ready', 'Bundled English model files are present. A live voice test is still needed.')
    except Exception:
        add('speech', 'Offline transcription files', 'attention', 'Speech files are incomplete. Reinstall the complete Bob release folder.')
    try:
        mic = microphone()
        add('microphone', 'Microphone device', 'ready', 'An input device is available. This check does not record or test Windows microphone permission.')
        add('calibration', 'Microphone calibration', 'ready' if mic.get('calibrated') else 'optional',
            'Calibration matches this device.' if mic.get('calibrated') else 'Optional: calibrate in Settings for your current microphone.')
    except Exception:
        add('microphone', 'Microphone device', 'attention', 'No input device could be queried. Choose an input in Windows Sound settings.')
        add('calibration', 'Microphone calibration', 'optional', 'Connect a microphone before calibrating.')
    try:
        output()
        add('output', 'Speaker device', 'ready', 'An output device is available. Use Test voice output in Settings to check audible speech.')
    except Exception:
        add('output', 'Speaker device', 'attention', 'No output device could be queried. Choose an output in Windows Sound settings.')
    add('identity', 'Personal voice focus', 'optional',
        'Enabled: review saved profiles and test a match in Settings. Matching is approximate.'
        if settings.get('speaker_enabled') else 'Off. Enable and enroll in Settings if you want personal voice focus.')
    core = [c for c in checks if c['id'] in ('model', 'speech', 'microphone', 'output')]
    result = {'schema': 1, 'checks': checks,
              'core_ready': all(c['state'] == 'ready' for c in core),
              'ready_count': sum(c['state'] == 'ready' for c in core), 'required_count': len(core)}
    # Deliberately use only fixed, allowlisted diagnostic fields. No exception
    # text, addresses, device names, profiles, paths or provider configuration.
    result['support_summary'] = json.dumps({
        'schema': 1, 'application': 'Bob',
        'checks': {c['id']: c['state'] for c in checks},
        'scope': 'Setup availability only; not an end-to-end acceptance test',
    }, indent=2)
    return result
