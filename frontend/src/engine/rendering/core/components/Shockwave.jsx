import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

import { getCoreParameters } from "../CoreController";

export default function Shockwave() {
  const mesh = useRef();
  const material = useRef();

  const color = useRef(
    new THREE.Color("#35F6FF")
  );

  const scale = useRef(1);
  const opacity = useRef(0);

  const lastColor = useRef("");


  useFrame((_, delta) => {
    if (!mesh.current || !material.current) return;

    const core = getCoreParameters();

    color.current.set(core.color);


    // Trigger new wave when state colour changes
    if (lastColor.current !== core.color) {
      scale.current = 1;
      opacity.current = 0.45;

      lastColor.current = core.color;
    }


    scale.current +=
      delta *
      (1.5 + core.speed * 0.3);


    opacity.current -=
      delta *
      0.5;


    mesh.current.scale.setScalar(
      scale.current
    );


    material.current.opacity =
      Math.max(opacity.current, 0);


    material.current.color.lerp(
      color.current,
      delta * 5
    );
  });


  return (
    <mesh ref={mesh} rotation={[-Math.PI / 2, 0, 0]}>

      <ringGeometry
        args={[
          1.1,
          1.15,
          128,
        ]}
      />

      <meshBasicMaterial
        ref={material}
        color="#35F6FF"
        transparent
        opacity={0}
        side={THREE.DoubleSide}
        toneMapped={false}
      />

    </mesh>
  );
}