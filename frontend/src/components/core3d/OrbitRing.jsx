import { useFrame } from "@react-three/fiber";
import { useRef } from "react";

export default function OrbitRing({
  radius,
  speed,
  rotation = [0, 0, 0],
  color = "#00E5FF",
}) {
  const ref = useRef();

  useFrame(() => {
    if (ref.current) {
      ref.current.rotation.z += speed;
    }
  });

  return (
    <mesh ref={ref} rotation={rotation}>
      <torusGeometry args={[radius, 0.008, 32, 240]} />

      <meshStandardMaterial
        color={color}
        emissive={color}
        emissiveIntensity={6}
        toneMapped={false}
      />
    </mesh>
  );
}