import { useRef } from "react";
import { useFrame } from "@react-three/fiber";

export default function PlasmaCore() {
  const material = useRef();
  const mesh = useRef();

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();

    if (material.current) {
      material.current.uTime = t;
    }

    if (mesh.current) {
      mesh.current.rotation.y += 0.003;

      const s = 1 + Math.sin(t * 2.0) * 0.04;

      mesh.current.scale.set(s, s, s);
    }
  });

  return (
    <mesh ref={mesh}>
      <icosahedronGeometry args={[1, 64]} />

      <plasmaMaterial ref={material} />
    </mesh>
  );
}