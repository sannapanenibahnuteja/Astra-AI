"""Device-specific input calibration. Stores levels only, never recorded audio."""
import math
import numpy as np


def input_device(sd):
    """Use the same Windows WASAPI default input as conversational capture."""
    index = None
    host = 'default'
    for api in sd.query_hostapis():
        if api['name'] == 'Windows WASAPI' and api['default_input_device'] >= 0:
            index = api['default_input_device']; host = api['name']; break
    device = sd.query_devices(index) if index is not None else sd.query_devices(kind='input')
    name = device.get('name', 'Default microphone')
    if 'stereo mix' in name.lower():
        raise ValueError('Choose your laptop microphone in Windows Sound → Input, not Stereo Mix.')
    return index, device, host + ':' + name


def rms_levels(audio, rate):
    audio = np.asarray(audio, dtype=np.float32).flatten()
    width = int(rate * .02)
    if len(audio) < width or not np.isfinite(audio).all():
        raise ValueError('No usable microphone audio. Check Windows microphone access.')
    frames = audio[:len(audio)//width*width].reshape(-1, width)
    frames = frames - frames.mean(axis=1, keepdims=True)
    return np.sqrt(np.mean(frames*frames, axis=1))


def calibration(device, name, noise, audio, rate):
    from desktop.duplex_audio import acoustic_speech
    levels = rms_levels(audio, rate)
    samples = np.asarray(audio, dtype=np.float32).flatten()
    if np.mean(np.abs(samples) >= .995) > .02:
        raise ValueError('The microphone is clipping. Lower its Windows input level and repeat calibration.')
    width = int(rate*.02)
    threshold = max(.00004, noise*1.8)
    speech = [level for index, level in enumerate(levels)
              if level > threshold and acoustic_speech(samples[index*width:(index+1)*width])]
    if len(speech)*.02 < 3:
        raise ValueError('Not enough clear voice above the room noise. Speak for ten seconds near your laptop microphone, then retry the voice step.')
    speech_rms = float(np.percentile(speech, 65))
    return {'device': device, 'name': name, 'noise_rms': float(noise),
            'speech_rms': speech_rms, 'gain': round(float(np.clip(.035/speech_rms, .5, 16)), 3)}


def validate(profile):
    if profile == {}: return
    if not isinstance(profile, dict) or set(profile) != {'device','name','noise_rms','speech_rms','gain'}:
        raise ValueError('Invalid microphone calibration.')
    if any(not isinstance(profile[k], str) or len(profile[k]) > 512 for k in ('device','name')):
        raise ValueError('Invalid calibration device.')
    for key in ('noise_rms','speech_rms','gain'):
        if type(profile[key]) not in (int,float) or not math.isfinite(profile[key]):
            raise ValueError('Invalid microphone levels.')
    if not (0 <= profile['noise_rms'] < 1 and 0 < profile['speech_rms'] <= 1 and .5 <= profile['gain'] <= 16):
        raise ValueError('Microphone levels are outside the allowed range.')


def gain_for(profile, device):
    try: validate(profile)
    except ValueError: return 1.
    return float(profile['gain']) if profile and profile['device'] == device else 1.
