import { useState } from "react";
import "./CommandInput.css";

import { streamMessage } from "../../services/chat";
import { speak } from "../../services/voice";

import useChatStore from "../../store/chatStore";
import useAIStateStore from "../../store/aiStateStore";

import MicrophoneButton from "./MicrophoneButton";


export default function CommandInput() {


  const [text, setText] = useState("");



  const addMessage =
    useChatStore(
      (state) => state.addMessage
    );


  const updateMessage =
    useChatStore(
      (state) => state.updateMessage
    );


  const setTyping =
    useChatStore(
      (state) => state.setTyping
    );


  const setAIState =
    useAIStateStore(
      (state) => state.setState
    );



  async function handleSend(message = text) {


    if(!message.trim())
      return;



    addMessage({

      id: Date.now(),

      role:"user",

      content:message,

    });



    setText("");



    setTyping(true);


    setAIState("thinking");



    const assistantId =
      Date.now()+1;



    addMessage({

      id:assistantId,

      role:"assistant",

      content:"",

    });



    let finalResponse = "";



    try {


      await streamMessage(

        message,

        (partial)=>{


          finalResponse = partial;


          updateMessage(

            assistantId,

            partial

          );


        }

      );



      setTyping(false);



      if(finalResponse.trim()){


        speak(finalResponse);


      }
      else {


        setAIState("idle");


      }



    }

    catch(error){


      console.error(error);



      setTyping(false);



      setAIState("error");



      updateMessage(

        assistantId,

        "Unable to contact Astra backend."

      );



      setTimeout(()=>{

        setAIState("idle");

      },1500);


    }


  }




  return (

    <div className="command-input">


      <input

        value={text}

        onChange={(e)=>{

          setText(e.target.value);


          if(e.target.value.trim()){

            setAIState("listening");

          }

        }}


        onKeyDown={(e)=>{

          if(e.key==="Enter"){

            handleSend();

          }

        }}


        placeholder="Ask Astra anything..."

      />



      <MicrophoneButton

        onTranscript={(transcript)=>{


          setText(transcript);


          setAIState("listening");


        }}



        onComplete={(transcript)=>{


          if(!transcript.trim())
            return;



          setText(transcript);



          setTimeout(()=>{


            handleSend(transcript);


          },150);



        }}

      />



      <button

        onClick={()=>handleSend()}

      >

        Send

      </button>


    </div>

  );

}