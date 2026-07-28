import { useRef } from "react";
import { useFrame } from "@react-three/fiber";

import { getCoreState } from "../CoreState";
import { updateCore } from "../AnimationController";

export default function PlasmaCore() {
  const material = useRef();
  const mesh = useRef();

  useFrame(({ clock }, delta) => {
    updateCore(
      material.current,
      mesh.current,
      getCoreState(),
      delta,
      clock.getElapsedTime()
    );
  });

  return (
    <mesh ref={mesh}>
      <icosahedronGeometry args={[1, 64]} />
      <plasmaMaterial ref={material} />
    </mesh>
  );
}