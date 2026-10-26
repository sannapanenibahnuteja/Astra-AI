"""Independent neural speech evidence for stopping a reply, never a sound trigger.

Uses the local Silero ONNX model already shipped with faster-whisper. Runs only
on completed candidates on the verification worker, not the audio callback.
No samples or transcripts are retained by this module.
"""
import numpy as np


def interruption_speech(audio, room_mode='balanced'):
    from desktop.audio_pipeline import recognition_samples
    samples = np.asarray(audio, dtype=np.float32).reshape(-1)
    if not 48000 * .5 <= len(samples) <= 48000 * 21:
        return False
    if not np.isfinite(samples).all():
        return False
    samples = recognition_samples(samples)
    samples = samples - float(samples.mean())
    rms = float(np.sqrt(np.mean(samples * samples)))
    quiet = room_mode == 'quiet'
    if rms < (.00012 if quiet else .0002):
        return False
    # Bound normalization: quiet consonants remain useful, tiny residual sound
    # does not become a loud signal. The acoustic gate is separately mandatory.
    samples = np.clip(samples * min(6. if quiet else 4., max(1., .025 / rms)), -.999, .999)
    try:
        from faster_whisper.vad import get_speech_timestamps, VadOptions
        spans = get_speech_timestamps(samples, VadOptions(
            threshold=.55 if quiet else .70, min_speech_duration_ms=240 if quiet else 320,
            min_silence_duration_ms=120, speech_pad_ms=0))
    except Exception:
        # A missing/broken model must retain playback, not fall back to VAD-only.
        return False
    lengths = [max(0, min(len(samples), int(s['end'])) - max(0, int(s['start'])))
               for s in spans]
    return bool(lengths and max(lengths) >= (.24 if quiet else .32) * 16000
                and sum(lengths) >= (.35 if quiet else .45) * 16000)


def learnable_turn(result):
    """Only accepted high-confidence matched-user text may adjust timing."""
    return bool(isinstance(result, dict) and result.get('text', '').strip()
                and not result.get('ignored') and not result.get('needs_review', True)
                and result.get('confidence', 0) >= .80
                and result.get('speaker', {}).get('state') == 'matched'
                and result.get('speaker', {}).get('profile_id'))
