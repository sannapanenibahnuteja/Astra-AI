import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

import { getCoreParameters } from "../CoreController";

export default function EnergyArcs() {
  const group = useRef();
  const material = useRef();

  const color = useRef(
    new THREE.Color("#35F6FF")
  );

  useFrame((_, delta) => {
    if (!group.current || !material.current) return;

    const core = getCoreParameters();

    color.current.set(core.color);

    material.current.color.lerp(
      color.current,
      delta * 5
    );

    material.current.opacity +=
      ((0.25 * core.intensity) -
        material.current.opacity) *
      delta *
      4;

    group.current.rotation.y +=
      delta * core.speed * 0.3;

    group.current.rotation.z +=
      delta * 0.1;
  });

  return (
    <group ref={group}>
      <mesh>
        <torusGeometry
          args={[1.45, 0.015, 16, 128]}
        />

        <meshBasicMaterial
          ref={material}
          color="#35F6FF"
          transparent
          opacity={0.25}
          toneMapped={false}
        />
      </mesh>

      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry
          args={[1.65, 0.008, 16, 128]}
        />

        <meshBasicMaterial
          color="#35F6FF"
          transparent
          opacity={0.12}
          toneMapped={false}
        />
      </mesh>
    </group>
  );
}