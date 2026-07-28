import useAudioStore from "../store/audioStore";

let animationFrame;

export async function startAudioLevel() {
  const stream = await navigator.mediaDevices.getUserMedia({
    audio: true,
  });

  const context = new AudioContext();

  const analyser = context.createAnalyser();

  analyser.fftSize = 256;

  const source = context.createMediaStreamSource(stream);

  source.connect(analyser);

  const data = new Uint8Array(analyser.frequencyBinCount);

  function update() {
    analyser.getByteFrequencyData(data);

    const average =
      data.reduce((a, b) => a + b, 0) / data.length;

    useAudioStore
      .getState()
      .setLevel(average / 255);

    animationFrame =
      requestAnimationFrame(update);
  }

  update();

  return () => {
    cancelAnimationFrame(animationFrame);

    stream.getTracks().forEach((track) => track.stop());

    context.close();
  };
}