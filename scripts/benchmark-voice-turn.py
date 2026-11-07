"""Measure Bob's duplex handoff and local replies with no microphone or PC actions."""
import argparse
import json
from pathlib import Path
import sys
import tempfile
import threading
import time
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from desktop.duplex_audio import CapturedTurn, wav_samples
from desktop.lifecycle import shutdown
from desktop.runtime import Runtime
from desktop.voice import Voice
from desktop.voice_model_diagnostics import errors


def speech_trials():
    voice = Voice()
    try:
        for phrase in ('Hey Bob, open the calculator.',
                       'Hey Bob, set the volume to twenty percent.',
                       'Hey Bob, explain why we see rainbows.'):
            wav = voice._speech_worker().render(phrase, 0, '', threading.Event(), threading.Event())
            samples = wav_samples(wav)
            engine = Mock()
            engine.receive.return_value = CapturedTurn(samples, samples, room_mode='quiet')
            started = time.perf_counter()
            with patch.object(voice, '_ensure_duplex', return_value=engine):
                result = voice.listen()
            elapsed = round((time.perf_counter() - started) * 1000)
            wrong, total = errors(phrase, result.get('text', ''))
            yield {'expected': phrase, 'decoded': result.get('text', ''), 'word_errors': wrong,
                   'reference_words': total, 'review': result.get('needs_review'), 'ms': elapsed}
    finally:
        voice.close()


def measure(runtime, query):
    chat = runtime.new_conversation()
    started = time.perf_counter()
    job = runtime.start_chat(chat, query, True)
    first = None
    while True:
        state = runtime.poll_chat(job)
        elapsed = round((time.perf_counter() - started) * 1000)
        if state['text'] and first is None:
            first = elapsed
        if state['done'] or elapsed > 30_000:
            break
        time.sleep(.015)
    if not state['done']:
        runtime.cancel_chat()
    return {'first_visible_ms': first, 'complete_ms': elapsed,
            'done': state['done'], 'error': state['error'], 'reply_present': bool(state['text'])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='.cache/voice-turn-benchmark.json')
    args = parser.parse_args()
    report = {'synthetic_duplex_handoff': list(speech_trials()), 'microphone_used': False}
    with tempfile.TemporaryDirectory(prefix='bob-voice-turn-') as folder:
        runtime = Runtime(folder)
        try:
            runtime._store.save_settings({'voice_enabled': False})
            status = runtime.ollama_status()
            report['ollama_ready'] = status['ready']
            report['local_time'] = measure(runtime, 'What time is it?')
            if status['ready']:
                report['spoken_explanation'] = measure(runtime, 'Explain why we see rainbows.')
        finally:
            shutdown(runtime)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
