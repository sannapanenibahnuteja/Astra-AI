import { getCoreState } from "./CoreState";

export function getCoreParameters() {
  const state = getCoreState();

  return {
    color: state.colour,

    speed: state.speed,

    intensity: state.intensity,

    pulse:
      state.intensity *
      state.speed,

    active:
      state.speed > 1,
  };
}