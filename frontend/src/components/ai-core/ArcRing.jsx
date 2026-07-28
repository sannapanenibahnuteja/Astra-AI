import { useFrame } from "@react-three/fiber";
import { useRef } from "react";

export default function ArcRing({
  radius,
  speed,
  rotation = [0, 0, 0],
}) {
  const ref = useRef();

  useFrame(() => {
    if (ref.current) {
      ref.current.rotation.z += speed;
    }
  });

  return (
    <mesh ref={ref} rotation={rotation}>

      <torusGeometry
        args={[
          radius,
          0.018,
          32,
          180,
          Math.PI * 1.45,
        ]}
      />

      <meshBasicMaterial
        color="#00E5FF"
        transparent
        opacity={0.95}
        toneMapped={false}
      />

    </mesh>
  );
}