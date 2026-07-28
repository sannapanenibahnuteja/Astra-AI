import { getCoreState } from "./CoreState";
import useAudioStore from "../../../store/audioStore";


export function getCoreParameters() {

  const state =
    getCoreState();


  const audioLevel =
    useAudioStore.getState().level;



  return {

    color: state.colour,

    speed:
      state.speed +
      audioLevel * 5,


    intensity:
      state.intensity +
      audioLevel * 1.5,


    pulse:
      state.intensity *
      state.speed,


    audioLevel,


    active:
      state.speed > 1 ||
      audioLevel > 0.1,

  };

}