import useAIStateStore from "../../../store/aiStateStore";
import CoreConfig from "../config/CoreConfig";

export function getCoreState() {
  const state = useAIStateStore.getState().state;

  switch (state) {
    case "thinking":
      return {
        colour: CoreConfig.colours.thinking,
        speed: 3.5,
        intensity: 1.4,
      };

    case "speaking":
      return {
        colour: CoreConfig.colours.speaking,
        speed: 2.0,
        intensity: 1.2,
      };

    case "listening":
      return {
        colour: CoreConfig.colours.listening,
        speed: 0.8,
        intensity: 1.0,
      };

    case "error":
      return {
        colour: CoreConfig.colours.error,
        speed: 7.0,
        intensity: 2.0,
      };

    default:
      return {
        colour: CoreConfig.colours.idle,
        speed: 1.0,
        intensity: 0.8,
      };
  }
}