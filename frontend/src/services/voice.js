import useVoiceStore from "../store/voiceStore";

let currentUtterance = null;

export function speak(text) {
  const {
    enabled,
    voice,
    rate,
    pitch,
    volume,
  } = useVoiceStore.getState();

  if (!enabled) return null;

  speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);

  utterance.rate = rate;
  utterance.pitch = pitch;
  utterance.volume = volume;

  const voices = speechSynthesis.getVoices();

  if (voice) {
    const selected = voices.find((v) => v.name === voice);

    if (selected) {
      utterance.voice = selected;
    }
  } else {
    const preferred =
      voices.find((v) => v.name.includes("Google")) ||
      voices.find((v) => v.lang.startsWith("en"));

    if (preferred) {
      utterance.voice = preferred;
    }
  }

  currentUtterance = utterance;

  speechSynthesis.speak(utterance);

  return utterance;
}

export function stopSpeaking() {
  speechSynthesis.cancel();
}

export function isSpeaking() {
  return speechSynthesis.speaking;
}