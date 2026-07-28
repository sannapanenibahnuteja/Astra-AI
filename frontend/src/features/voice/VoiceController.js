import { startListening, stopListening } from "../../services/speechRecognition";
import { speak, stopSpeaking } from "../../services/voice";

class VoiceController {
  listening = false;

  start(config) {
    stopSpeaking();

    startListening({
      onStart: () => {
        this.listening = true;
        config?.onStart?.();
      },

      onResult: (text) => {
        config?.onTranscript?.(text);
      },

      onComplete: (text) => {
        config?.onComplete?.(text);
      },

      onEnd: () => {
        this.listening = false;
        config?.onEnd?.();
      },

      onError: (error) => {
        this.listening = false;
        config?.onError?.(error);
      },
    });
  }

  stop() {
    stopListening();
    stopSpeaking();
    this.listening = false;
  }

  speak(text) {
    return speak(text);
  }

  interrupt() {
    stopSpeaking();
  }
}

export default new VoiceController();