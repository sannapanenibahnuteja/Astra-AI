import { isSpeaking } from "./voice";


let recognition = null;

let running = false;

let paused = false;

let conversationMode = false;

let conversationTimer = null;

let commandBuffer = "";

let commandTimer = null;

let ignoreUntil = 0;



const CONVERSATION_TIMEOUT = 60000;



const WAKE_WORDS = [
    "bob",
    "hey bob",
    "hi bob",
    "hello bob",
    "heybob",
    "hibob",
    "hellobob"
];





const IGNORED_PHRASES = [

    "would you like me to install them",

    "would you like to know what they are",

    "i don't know how to do that yet sir",

    "i do not know how to do that yet sir",

    "i need administrator permission",

    "please approve the windows permission prompt",

    "your cpu usage",

    "cpu usage",

    "ram usage",

    "battery is",

    "system status",

    "your system",

    "percent",

    "percentage",

    "sir",

    "opening",

    "installing",

    "i found",

    "updates available"

];





window.addEventListener(
    "astraFinishedSpeaking",
    ()=>{

        ignoreUntil =
            Date.now() + 2500;

    }
);







export function pauseWakeListener() {

    paused = true;

    running = false;

    clearTimeout(conversationTimer);
    clearTimeout(commandTimer);

    if (recognition) {

        try {

            recognition.onend = null;
            recognition.onerror = null;

            recognition.stop();

        } catch (e) {}

        recognition = null;

    }

}






export function resumeWakeListener() {

    paused = false;

    if (!running) {

        running = true;

        setTimeout(() => {

            if (running && window.astraWakeCallback) {

                startWakeListener(window.astraWakeCallback);

            }

        }, 500);

    }

}







function resetConversationTimer(){


    clearTimeout(
        conversationTimer
    );


    conversationTimer =
        setTimeout(()=>{


            conversationMode = false;


            console.log(
                "BOB CONVERSATION ENDED"
            );


        }, CONVERSATION_TIMEOUT);


}







function cleanCommand(text){


    let cleaned =
        text
        .toLowerCase()
        .replace(/[.,!?]/g,"")
        .trim();



    for(
        const phrase of IGNORED_PHRASES
    ){

        cleaned =
            cleaned.replace(
                phrase,
                ""
            );

    }



    return cleaned.trim();

}








function extractCommand(text){


    let cleaned =
        cleanCommand(text);





    for(
        const word of WAKE_WORDS
    ){


        if(cleaned.includes(word)){


            conversationMode = true;


            resetConversationTimer();



            return cleaned
                .replace(word,"")
                .trim();


        }

    }





    if(conversationMode){


        resetConversationTimer();



        return cleaned;


    }





    return null;

}









export function startWakeListener(callback){



    const SpeechRecognition =

        window.SpeechRecognition ||

        window.webkitSpeechRecognition;





    if(!SpeechRecognition){


        console.error(
            "Speech recognition unavailable"
        );


        return;

    }






    recognition =
        new SpeechRecognition();





    recognition.continuous = true;

    recognition.interimResults = true;

    recognition.lang = "en-US";





    running = true;








    recognition.onresult = (event)=>{



        if(paused)
            return;





        if(

            isSpeaking()

            ||

            Date.now() < ignoreUntil

        ){


            console.log(
                "IGNORING ASTRA VOICE"
            );


            return;

        }






        let text = "";





        for(

            let i = event.resultIndex;

            i < event.results.length;

            i++

        ){


            text +=

            event.results[i][0].transcript;


        }







        text =
            text.toLowerCase();






        console.log(

            "WAKE LISTENER:",

            text

        );







        let command =

            extractCommand(text);






        if(command !== null){



            commandBuffer =

                command;






            clearTimeout(
                commandTimer
            );







            commandTimer =

                setTimeout(()=>{





                    if(commandBuffer.trim()){


                        callback(

                            commandBuffer

                        );


                    }





                    commandBuffer = "";





                },1200);



        }



    };









    recognition.onerror = (error)=>{


        console.error(

            "Wake listener error:",

            error

        );


    };









    recognition.onend = ()=>{



        if(running){


            try{


                recognition.start();


            }

            catch(e){}



        }



    };







    recognition.start();


}









export function stopWakeListener(){



    running = false;



    conversationMode = false;



    clearTimeout(
        conversationTimer
    );




    if(recognition){


        recognition.stop();



        recognition = null;


    }



}