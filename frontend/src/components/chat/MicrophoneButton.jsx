import { useState } from "react";
import { Mic, MicOff } from "lucide-react";

import {
  startListening,
  stopListening,
} from "../../services/speechRecognition";

import {
  pauseWakeListener,
  resumeWakeListener,
} from "../../services/wakeListener";

import { stopSpeaking } from "../../services/voice";

export default function MicrophoneButton({
  onTranscript,
  onComplete,
}) {
  const [listening, setListening] = useState(false);

  function handleClick() {
    // Interrupt Astra immediately if it's speaking
    stopSpeaking();

    if (listening) {
      stopListening();
      resumeWakeListener();
      setListening(false);
      return;
    }
    // Pause wake listener while using push-to-talk
    pauseWakeListener();

    startListening({
      onStart() {
        setListening(true);
      },

      onResult(text) {
        onTranscript?.(text);
      },

      onComplete(text) {
        onComplete?.(text);
      },

      onEnd() {
        resumeWakeListener();
        setListening(false);
      },

      onError(error) {
        console.error(error);
        resumeWakeListener();
        setListening(false);
      },
    });
  }

  return (
    <button
      className={`mic-button ${listening ? "listening" : ""}`}
      onClick={handleClick}
      title={listening ? "Stop Listening" : "Voice Input"}
    >
      {listening ? <MicOff size={20} /> : <Mic size={20} />}
    </button>
  );
}