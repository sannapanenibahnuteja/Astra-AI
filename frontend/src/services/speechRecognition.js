let recognition = null;

export function startListening({
  onStart,
  onResult,
  onComplete,
  onEnd,
  onError,
}) {
  const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    alert("Your browser doesn't support Speech Recognition.");
    return;
  }

  recognition = new SpeechRecognition();

  recognition.lang = "en-US";
  recognition.continuous = false;
  recognition.interimResults = true;
  recognition.maxAlternatives = 1;

  let finalTranscript = "";

  recognition.onstart = () => {
    onStart?.();
  };

  recognition.onresult = (event) => {
    let interim = "";

    for (let i = event.resultIndex; i < event.results.length; i++) {
      const transcript = event.results[i][0].transcript;

      if (event.results[i].isFinal) {
        finalTranscript += transcript;
      } else {
        interim += transcript;
      }
    }

    onResult?.(finalTranscript + interim);
  };

  recognition.onend = () => {
    onComplete?.(finalTranscript.trim());
    onEnd?.();
  };

  recognition.onerror = (error) => {
    onError?.(error);
  };

  recognition.start();
}

export function stopListening() {
  recognition?.stop();
}