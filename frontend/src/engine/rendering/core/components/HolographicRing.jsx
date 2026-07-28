import { useRef } from "react";
import { useFrame } from "@react-three/fiber";

export default function HolographicRing({
  radius,
  rotation = [0, 0, 0],
  speed = 0.002,
}) {
  const ring = useRef();

  useFrame(({ clock }) => {
    if (!ring.current) return;

    const t = clock.getElapsedTime();

    ring.current.rotation.z += speed;
    ring.current.rotation.x = Math.sin(t * 0.25) * 0.03;
    ring.current.rotation.y = Math.cos(t * 0.18) * 0.02;
  });

  const segments = 48;

  return (
    <group ref={ring} rotation={rotation}>
      {Array.from({ length: segments }).map((_, i) => {
        // Create gaps
        if (i % 5 === 0) return null;

        const angle = (i / segments) * Math.PI * 2;

        const length =
          i % 12 === 0
            ? 0.28
            : i % 5 === 0
            ? 0.20
            : 0.13;

        const thickness =
          i % 12 === 0
            ? 0.028
            : 0.02;

        const color =
          i % 12 === 0
            ? "#FFFFFF"
            : i % 5 === 0
            ? "#7EFFFF"
            : "#35F6FF";

        return (
          <mesh
            key={i}
            position={[
              Math.cos(angle) * radius,
              Math.sin(angle) * radius,
              0,
            ]}
            rotation={[0, 0, angle]}
          >
            <boxGeometry
              args={[
                length,
                thickness,
                0.015,
              ]}
            />

            <meshBasicMaterial
              color={color}
              transparent
              opacity={0.75}
              toneMapped={false}
            />
          </mesh>
        );
      })}
    </group>
  );
}