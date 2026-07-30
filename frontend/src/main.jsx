import React, { useEffect } from "react";
import ReactDOM from "react-dom/client";
import { extend } from "@react-three/fiber";

import App from "./App";
import { SettingsProvider } from "./contexts/SettingsContext";

import PlasmaMaterial from "./engine/rendering/materials/PlasmaMaterial";

import {
  startWakeListener,
  stopWakeListener,
} from "./services/wakeListener";

import { executeCommand } from "./services/commands";
import { speak } from "./services/voice";

import useAIStateStore from "./store/aiStateStore";


extend({
  PlasmaMaterial
});


const API =
  "http://127.0.0.1:8000";



async function saveMemory(text){

  await fetch(

    `${API}/memory/save`,

    {
      method:"POST",

      headers:{
        "Content-Type":"application/json"
      },

      body:JSON.stringify({
        content:text
      })

    }

  );

}




async function searchMemory(query){

  const response =
    await fetch(

      `${API}/memory/search?query=${encodeURIComponent(query)}`

    );


  return await response.json();

}





async function sendCommand(command){

  const response =
    await fetch(

      `${API}/commands/execute`,

      {

        method:"POST",

        headers:{
          "Content-Type":"application/json"
        },


        body:JSON.stringify({

          command

        })

      }

    );


  return await response.json();

}






function AstraRoot(){


  const setAIState =
    useAIStateStore(
      state=>state.setState
    );



  useEffect(()=>{


    startWakeListener(

      async(command)=>{


        console.log(
          "ASTRA COMMAND:",
          command
        );



        const lower =
          command.toLowerCase();



        setAIState(
          "listening"
        );




        // MEMORY SAVE

        if(
          lower.includes("remember")
        ){


          const memory =
            command
            .replace(
              /remember/gi,
              ""
            )
            .trim();



          await saveMemory(
            memory
          );


          setAIState(
            "speaking"
          );


          speak(
            "I will remember that, sir."
          );


          setTimeout(()=>{

            setAIState(
              "idle"
            );

          },2500);


          return;

        }





        // MEMORY SEARCH

const isMemoryQuestion =
  /\bwhat\b/.test(lower) ||
  /\bwho\b/.test(lower) ||
  /\bwhere\b/.test(lower) ||
  /\bdo i have\b/.test(lower);

if (

  isMemoryQuestion &&

  !(
    lower.includes("update") ||
    lower.includes("weather") ||
    lower.includes("system") ||
    lower.includes("cpu") ||
    lower.includes("ram") ||
    lower.includes("battery")
  )

) {


          setAIState(
            "thinking"
          );


          const result =
            await searchMemory(
              command
            );



          if(

            result.results &&

            result.results.length > 0

          ){


            setAIState(
              "speaking"
            );


            speak(

              `I remember ${result.results[0].value}, sir.`

            );


          }
          else{


            setAIState(
              "speaking"
            );


            speak(
              "I do not have that memory yet, sir."
            );


          }



          setTimeout(()=>{

            setAIState(
              "idle"
            );

          },2500);



          return;

        }






        // ALL OTHER COMMANDS GO TO BACKEND

        setAIState(
          "thinking"
        );


        const result =
          await sendCommand(
            command
          );



        setAIState(
          "speaking"
        );


        if(result.message){

          speak(
            result.message
          );

        }
        else{

          speak(
            "I could not complete that command, sir."
          );

        }



        setTimeout(()=>{

          setAIState(
            "idle"
          );

        },3000);



      }

    );



    return ()=>{

      stopWakeListener();

    };


  },[]);





  return (

    <SettingsProvider>

      <App />

    </SettingsProvider>

  );

}





ReactDOM.createRoot(
  document.getElementById("root")
)
.render(

  <AstraRoot />

);