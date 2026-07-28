export function speak(text) {
  speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);

  utterance.rate = 1;
  utterance.pitch = 1;
  utterance.volume = 1;

  const voices = speechSynthesis.getVoices();

  const preferred =
    voices.find((v) => v.name.includes("Google")) ||
    voices.find((v) => v.lang.startsWith("en"));

  if (preferred) {
    utterance.voice = preferred;
  }

  speechSynthesis.speak(utterance);

  return utterance;
}

export function stopSpeaking() {
  speechSynthesis.cancel();
}