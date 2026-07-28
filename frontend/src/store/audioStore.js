import { create } from "zustand";


const useAudioStore = create((set) => ({

  level: 0,


  targetLevel: 0,


  setLevel: (level) =>
    set({
      targetLevel: level,
    }),


  updateLevel: () =>
    set((state) => {

      const smooth =
        state.level +
        (
          state.targetLevel -
          state.level
        )
        *
        0.15;


      return {
        level: smooth,
      };

    }),


  resetLevel: () =>
    set({
      level: 0,
      targetLevel: 0,
    }),

}));


export default useAudioStore;