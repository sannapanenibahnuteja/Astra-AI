import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

import { getCoreParameters } from "../CoreController";

export default function OuterShell() {
  const mesh = useRef();
  const material = useRef();

  const color = useRef(
    new THREE.Color("#35F6FF")
  );

  useFrame(({ clock }, delta) => {
    if (!mesh.current || !material.current) return;

    const core = getCoreParameters();

    color.current.set(core.color);

    material.current.color.lerp(
      color.current,
      delta * 4
    );

    material.current.opacity +=
      ((0.1 * core.intensity) -
        material.current.opacity) *
      delta *
      3;

    mesh.current.rotation.y +=
      delta * 0.15 * core.speed;

    const scale =
      1.35 +
      Math.sin(clock.elapsedTime * core.speed) *
      0.02;

    mesh.current.scale.setScalar(scale);
  });

  return (
    <mesh ref={mesh}>
      <sphereGeometry args={[1, 64, 64]} />

      <meshBasicMaterial
        ref={material}
        transparent
        opacity={0.08}
        color="#35F6FF"
        toneMapped={false}
      />
    </mesh>
  );
}