import { useRef } from "react";
import { useFrame } from "@react-three/fiber";

export default function EnergyField() {
  const field = useRef();

  useFrame(({ clock }) => {
    if (!field.current) return;

    const t = clock.getElapsedTime();

    field.current.rotation.z = t * 0.05;

    const scale = 1 + Math.sin(t * 0.8) * 0.02;
    field.current.scale.set(scale, scale, scale);
  });

  return (
    <mesh
      ref={field}
      rotation={[-Math.PI / 2, 0, 0]}
    >
      <ringGeometry args={[3.4, 3.7, 256]} />

      <meshBasicMaterial
        color="#35F6FF"
        transparent
        opacity={0.08}
        side={2}
        toneMapped={false}
      />
    </mesh>
  );
}