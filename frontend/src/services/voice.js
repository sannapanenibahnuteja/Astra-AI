import useVoiceStore from "../store/voiceStore";
import useAIStateStore from "../store/aiStateStore";
import useAudioStore from "../store/audioStore";

let currentUtterance = null;
let audioInterval = null;


function startVoiceAnimation() {
  const setLevel =
    useAudioStore.getState().setLevel;

  audioInterval = setInterval(() => {
    const level =
      0.3 +
      Math.random() * 0.7;

    setLevel(level);

  }, 100);
}


function stopVoiceAnimation() {
  const setLevel =
    useAudioStore.getState().setLevel;

  if (audioInterval) {
    clearInterval(audioInterval);
    audioInterval = null;
  }

  setLevel(0);
}


export function speak(text) {

  const {
    enabled,
    voice,
    rate,
    pitch,
    volume,
  } = useVoiceStore.getState();


  if (!enabled) return;


  const setAIState =
    useAIStateStore.getState().setState;


  speechSynthesis.cancel();


  const utterance =
    new SpeechSynthesisUtterance(text);


  utterance.rate = rate;
  utterance.pitch = pitch;
  utterance.volume = volume;


  const voices =
    speechSynthesis.getVoices();


  if (voice) {

    const selected =
      voices.find(
        (v) => v.name === voice
      );

    if (selected) {
      utterance.voice = selected;
    }

  }


  utterance.onstart = () => {

    // IMPORTANT
    setAIState("speaking");

    startVoiceAnimation();
  };


  utterance.onend = () => {

    stopVoiceAnimation();

    setAIState("idle");
  };


  utterance.onerror = () => {

    stopVoiceAnimation();

    setAIState("idle");
  };


  currentUtterance = utterance;


  speechSynthesis.speak(utterance);

}


export function stopSpeaking() {

  speechSynthesis.cancel();

  stopVoiceAnimation();

  useAIStateStore
    .getState()
    .setState("idle");
}


export function isSpeaking() {

  return speechSynthesis.speaking;

}