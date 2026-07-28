import { useFrame } from "@react-three/fiber";
import { useRef } from "react";

export default function GlowHalo() {
  const halo = useRef();

  useFrame(({ clock }) => {
    if (halo.current) {
      halo.current.scale.setScalar(
        3.4 + Math.sin(clock.getElapsedTime() * 2) * 0.08
      );
    }
  });

  return (
    <mesh ref={halo}>
      <sphereGeometry args={[1.6, 64, 64]} />

      <meshBasicMaterial
        color="#00E5FF"
        transparent
        opacity={0.06}
      />
    </mesh>
  );
}