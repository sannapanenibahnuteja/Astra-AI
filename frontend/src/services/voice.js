import useVoiceStore from "../store/voiceStore";
import useAIStateStore from "../store/aiStateStore";
import useAudioStore from "../store/audioStore";


let audioInterval = null;

let speaking = false;





function startVoiceAnimation() {


  const setLevel =
    useAudioStore.getState().setLevel;



  audioInterval =
    setInterval(() => {


      const level =
        0.25 +
        Math.random() *
        0.75;


      setLevel(level);


    }, 120);


}







function stopVoiceAnimation() {


  if(audioInterval){


    clearInterval(audioInterval);


    audioInterval = null;


  }



  useAudioStore
    .getState()
    .resetLevel();


}








export function speak(text){



  const {

    enabled,

    voice,

    rate,

    pitch,

    volume,


  } = useVoiceStore.getState();





  if(!enabled) return;





  const setAIState =

    useAIStateStore
      .getState()
      .setState;





  speechSynthesis.cancel();




  speaking = true;





  const utterance =

    new SpeechSynthesisUtterance(text);






  utterance.rate = rate;

  utterance.pitch = pitch;

  utterance.volume = volume;






  const voices =

    speechSynthesis.getVoices();






  if(voice){



    const selected =

      voices.find(

        (v)=>v.name === voice

      );




    if(selected){

      utterance.voice = selected;

    }


  }








  utterance.onstart = ()=>{


    speaking = true;



    setAIState(
      "speaking"
    );



    startVoiceAnimation();


  };









  utterance.onend = ()=>{


    speaking = false;



    stopVoiceAnimation();



    setAIState(
      "idle"
    );



    // Tell wake listener Astra finished talking

    window.dispatchEvent(

      new Event(
        "astraFinishedSpeaking"
      )

    );


  };









  utterance.onerror = ()=>{


    speaking = false;



    stopVoiceAnimation();



    setAIState(
      "idle"
    );



    window.dispatchEvent(

      new Event(
        "astraFinishedSpeaking"
      )

    );


  };








  speechSynthesis.speak(
    utterance
  );



}









export function stopSpeaking(){



  speechSynthesis.cancel();



  speaking = false;



  stopVoiceAnimation();



  useAIStateStore

    .getState()

    .setState("idle");



  window.dispatchEvent(

    new Event(
      "astraFinishedSpeaking"
    )

  );


}









export function isSpeaking(){



  return (

    speaking ||

    speechSynthesis.speaking

  );


}