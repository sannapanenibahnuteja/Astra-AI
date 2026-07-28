import { useRef } from "react";
import { useFrame } from "@react-three/fiber";

import useAudioStore from "../../../../store/audioStore";
import { getCoreParameters } from "../CoreController";

export default function ParticleCloud() {
  const points = useRef();

  const audioLevel = useAudioStore(
    (state) => state.level
  );

  const particleCount = 1000;


  const positions = useRef(
    new Float32Array(particleCount * 3)
  );


  if (positions.current.every((v) => v === 0)) {
    for (let i = 0; i < particleCount; i++) {

      const radius =
        1.8 + Math.random() * 1.8;

      const angle =
        Math.random() * Math.PI * 2;


      positions.current[i * 3] =
        Math.cos(angle) * radius;


      positions.current[i * 3 + 1] =
        (Math.random() - 0.5) * 2;


      positions.current[i * 3 + 2] =
        Math.sin(angle) * radius;
    }
  }


  useFrame(({ clock }, delta) => {
    if (!points.current) return;


    const core = getCoreParameters();


    const voiceBoost =
      audioLevel * 2;


    const pulse =
      1 +
      Math.sin(
        clock.elapsedTime *
        core.speed *
        2
      ) *
      0.03 *
      core.intensity;


    const finalScale =
      pulse +
      voiceBoost * 0.08;


    points.current.scale.setScalar(
      finalScale
    );


    points.current.rotation.y +=
      delta *
      core.speed *
      0.08;
  });


  return (
    <points ref={points}>

      <bufferGeometry>

        <bufferAttribute
          attach="attributes-position"
          count={particleCount}
          array={positions.current}
          itemSize={3}
        />

      </bufferGeometry>


      <pointsMaterial
        size={0.025}
        color="#35F6FF"
        transparent
        opacity={0.65}
        sizeAttenuation
      />

    </points>
  );
}