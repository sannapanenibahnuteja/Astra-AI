import { useState } from "react";
import { Mic, MicOff } from "lucide-react";

import {
  startListening,
  stopListening,
} from "../../services/speechRecognition";

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
      setListening(false);
      return;
    }

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
        setListening(false);
      },

      onError(error) {
        console.error(error);
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