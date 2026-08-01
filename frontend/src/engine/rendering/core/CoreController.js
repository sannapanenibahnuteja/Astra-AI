import { getCoreState } from "./CoreState";
import useAudioStore from "../../../store/audioStore";
import useAIStateStore from "../../../store/aiStateStore";

export function getCoreParameters() {

    const state =
        getCoreState();

    const audioLevel =
        useAudioStore.getState().level;

    const aiState =
        useAIStateStore.getState().state;

    let color =
        state.colour;

    let speed =
        state.speed;

    let intensity =
        state.intensity;

    switch(aiState){

        case "listening":

            color="#00E5FF";
            speed*=1.4;
            intensity*=1.2;
            break;

        case "thinking":

            color="#8A5CFF";
            speed*=2.0;
            intensity*=1.45;
            break;

        case "speaking":

            color="#00FFD5";
            speed*=1.1;
            intensity*=1.3;
            break;

        case "executing":

            color="#FFD400";
            speed*=2.4;
            intensity*=1.7;
            break;

        case "error":

            color="#FF355E";
            speed*=0.8;
            intensity*=1.8;
            break;

        default:

            color="#00E5FF";

    }

    return{

        color,

        speed:
            speed +
            audioLevel*4,

        intensity:
            intensity +
            audioLevel,

        pulse:
            intensity,

        audioLevel,

        aiState,

        active:
            aiState!=="idle" ||
            audioLevel>0.05

    };

}