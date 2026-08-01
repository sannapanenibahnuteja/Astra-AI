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






        // ALL OTHER COMMANDS GO TO BACKEND

        setAIState(
          "thinking"
        );


        const result =
          await executeCommand(
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