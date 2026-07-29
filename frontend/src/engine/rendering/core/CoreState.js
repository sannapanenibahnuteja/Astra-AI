import useAIStateStore from "../../../store/aiStateStore";


export function getCoreState() {

  const state =
    useAIStateStore.getState().state;


  


  switch(state) {


    case "thinking":

      return {
        colour: "#920303",
        speed: 3.5,
        intensity: 1.7,
      };


    case "speaking":

      return {
        colour: "#4b0000",
        speed: 4,
        intensity: 2,
      };


    case "listening":

      return {
        colour: "#00FFAA",
        speed: 1.5,
        intensity: 1.4,
      };


    case "error":

      return {
        colour: "#FF1744",
        speed: 8,
        intensity: 3,
      };


    default:

      return {
        colour: "#007e85",
        speed: 1,
        intensity: 1,
      };

  }

}