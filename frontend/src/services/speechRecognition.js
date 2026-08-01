let recognition = null;


export function startListening({
  onStart,
  onResult,
  onComplete,
  onEnd,
  onError,
}) {


  console.log("START LISTENING CALLED");


  const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;



  if (!SpeechRecognition) {

    console.error(
      "Speech Recognition API unavailable"
    );

    return;

  }



  recognition =
    new SpeechRecognition();



  recognition.lang = "en-US";

  recognition.continuous = true;

  recognition.interimResults = false;

  recognition.maxAlternatives = 1;



  let transcript = "";



  recognition.onstart = () => {

    console.log(
      "RECOGNITION STARTED"
    );

    onStart?.();

  };



  recognition.onaudiostart = () => {

    console.log(
      "AUDIO STARTED"
    );

  };



  recognition.onspeechstart = () => {

    console.log(
      "SPEECH DETECTED"
    );

  };



recognition.onresult = (event) => {

    let finalTranscript = transcript;

    for (let i = event.resultIndex; i < event.results.length; i++) {

        const result = event.results[i];

        if (result.isFinal) {

            finalTranscript += result[0].transcript + " ";

        } else {

            onResult?.(result[0].transcript);

        }

    }

    transcript = finalTranscript.trim();

    console.log("TEXT:", transcript);

};



  recognition.onerror = (event) => {


    console.error(
      "RECOGNITION ERROR",
      event
    );


    onError?.(event);

  };



  recognition.onend = () => {
    console.log("WHY DID IT END?");
    console.log("Transcript:", transcript);


    console.log(
      "RECOGNITION ENDED",
      transcript
    );


    if(transcript.trim()){


      onComplete?.(
        transcript.trim()
      );


    }



    onEnd?.();

  };



  recognition.start();

}





export function stopListening(){


  console.log(
    "STOP LISTENING"
  );


  if(recognition){

    recognition.stop();

    recognition=null;

  }

}