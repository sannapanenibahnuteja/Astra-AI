import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

import { getCoreParameters } from "../CoreController";

export default function OrbitSystem() {
  const group = useRef();

  const primaryMaterial = useRef();
  const secondaryMaterial = useRef();

  const color = useRef(
    new THREE.Color("#35F6FF")
  );

  useFrame((_, delta) => {
    if (!group.current) return;

    const core = getCoreParameters();

    color.current.set(core.color);

    if (primaryMaterial.current) {
      primaryMaterial.current.color.lerp(
        color.current,
        delta * 4
      );

      primaryMaterial.current.opacity +=
        (
          0.35 * core.intensity -
          primaryMaterial.current.opacity
        ) *
        delta *
        3;
    }


    if (secondaryMaterial.current) {
      secondaryMaterial.current.color.lerp(
        color.current,
        delta * 4
      );

      secondaryMaterial.current.opacity +=
        (
          0.18 * core.intensity -
          secondaryMaterial.current.opacity
        ) *
        delta *
        3;
    }


    group.current.rotation.y +=
      delta *
      core.speed *
      0.35;


    group.current.rotation.x +=
      delta *
      0.08;
  });


  return (
    <group ref={group}>

      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry
          args={[
            1.9,
            0.012,
            16,
            128,
          ]}
        />

        <meshBasicMaterial
          ref={primaryMaterial}
          color="#35F6FF"
          transparent
          opacity={0.35}
          toneMapped={false}
        />
      </mesh>


      <mesh rotation={[0.8, 0.4, 0]}>
        <torusGeometry
          args={[
            2.2,
            0.008,
            16,
            128,
          ]}
        />

        <meshBasicMaterial
          ref={secondaryMaterial}
          color="#2979FF"
          transparent
          opacity={0.18}
          toneMapped={false}
        />
      </mesh>

    </group>
  );
}