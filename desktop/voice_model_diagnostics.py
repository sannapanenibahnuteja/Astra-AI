"""Local generated-speech checks, without recording or executing a command."""
import re
import threading
import time
import queue
import numpy as np
from desktop.duplex_audio import wav_samples
from desktop.voice_evidence import interruption_speech


def words(text):
    return re.findall(r'[a-z0-9]+', text.casefold())


def errors(expected, actual):
    a, b = words(expected), words(actual)
    row = list(range(len(b) + 1))
    for index, token in enumerate(a, 1):
        updated = [index]
        for other, received in enumerate(b, 1):
            updated.append(min(updated[-1] + 1, row[other] + 1,
                               row[other - 1] + (token != received)))
        row = updated
    return row[-1], len(a)


def double_talk(speech):
    """Generated near speech plus delayed playback echo through actual DSP."""
    from desktop.duplex_audio import DuplexAudio, RATE, BLOCK
    count=(len(speech)+RATE*4)//BLOCK+1
    length=count*BLOCK
    far=np.resize(speech,length)*.3
    near=np.r_[np.zeros(2880,np.float32),far[:-2880]*.4]
    user=np.zeros(length,np.float32)
    user[RATE*2:RATE*2+len(speech)]=speech*.3
    engine=DuplexAudio(lambda:False,lambda **values:None)
    engine.blocks=queue.Queue()
    engine.authorize_interrupt=lambda *args:False
    engine.response_active=lambda:True
    engine.play_started=0.;engine.echo_until=float('inf')
    candidates=[];engine._submit_focused_turn=candidates.append
    processed=0
    def status(**values):
        nonlocal processed
        if 'level' in values:
            processed+=1
            if processed>=count:engine.closed.set()
    engine.on_status=status
    try:
        for offset in range(0,length,BLOCK):
            engine.blocks.put((near[offset:offset+BLOCK]+user[offset:offset+BLOCK],far[offset:offset+BLOCK],60))
        engine._work()
        return {'passed':not engine.error and bool(candidates)
                and any(interruption_speech(turn.audio) for turn in candidates),
                'capture_starts':engine.turn_serial, 'candidates':len(candidates),
                'scope':'Generated speech with simulated 60ms playback echo; no real microphone'}
    finally:engine.close()


def verify(voice):
    from faster_whisper import WhisperModel
    from desktop.speech_models import options, path_for
    from desktop.audio_pipeline import recognition_samples
    phrases = ['Hey Bob, please stop talking.',
               'Hey Bob, open the calculator and tell me the time.',
               'Help me plan my morning, then remind me to take a break.']
    audio = []
    render_times = []
    for phrase in phrases:
        start = time.perf_counter()
        wav = voice._speech_worker().render(phrase, 0, '', threading.Event(), threading.Event())
        if not wav:
            raise RuntimeError('Generated Windows speech was empty.')
        render_times.append(round(time.perf_counter() - start, 3))
        audio.append(wav_samples(wav))
    evidence = [interruption_speech(sample) for sample in audio]
    duplex = double_talk(audio[0])
    models = []
    for option in options():
        if not option['installed']:
            continue
        start = time.perf_counter()
        model = WhisperModel(str(path_for(option['id'])), device='cpu', compute_type='int8',
                             cpu_threads=2, num_workers=1, local_files_only=True)
        load_seconds = time.perf_counter() - start
        total_errors = total_words = 0
        samples = []
        for phrase, sample in zip(phrases, audio):
            start = time.perf_counter()
            segments, _ = model.transcribe(recognition_samples(sample), language='en',
                beam_size=3, vad_filter=True, condition_on_previous_text=False, temperature=0)
            text = ' '.join(segment.text for segment in segments)
            count, length = errors(phrase, text)
            total_errors += count
            total_words += length
            samples.append({'transcribe_seconds':round(time.perf_counter()-start,3),
                            'audio_seconds':round(len(sample)/48000,3),
                            'word_errors':count, 'reference_words':length, 'text_present':bool(text.strip())})
        models.append({'id':option['id'], 'load_seconds':round(load_seconds,3),
                       'samples':samples, 'word_error_rate':round(total_errors/max(1,total_words),3)})
        del model
    return {'passed':all(evidence) and duplex['passed'] and bool(models)
            and all(m['word_error_rate'] <= .4 and all(s['text_present'] for s in m['samples']) for m in models),
            'neural_speech_accepted':evidence, 'models':models,
            'generated_double_talk':duplex,
            'windows_render_seconds':render_times, 'microphone_used':False,
            'scope':'Three generated Windows voice phrases; not accent/noisy-room or live user accuracy'}
