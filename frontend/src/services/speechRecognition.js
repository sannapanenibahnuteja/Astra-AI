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

  recognition.continuous = false;

  recognition.interimResults = true;



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


    console.log(
      "RAW RESULT",
      event
    );



    let text = "";



    for(
      let i = event.resultIndex;
      i < event.results.length;
      i++
    ){

      text +=
        event.results[i][0].transcript;

    }



    transcript = text;



    console.log(
      "TEXT:",
      transcript
    );



    onResult?.(transcript);

  };



  recognition.onerror = (event) => {


    console.error(
      "RECOGNITION ERROR",
      event
    );


    onError?.(event);

  };



  recognition.onend = () => {


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