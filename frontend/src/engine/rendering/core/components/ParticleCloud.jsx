import { useRef, useMemo } from "react";
import { useFrame } from "@react-three/fiber";

export default function ParticleCloud() {
  const points = useRef();

  const particles = useMemo(() => {
    const positions = [];

    for (let i = 0; i < 5000; i++) {
      const r =
  Math.random() < 0.6
    ? 1.2 + Math.random() * 1.6
    : 3 + Math.random() * 2.5;

      const theta = Math.random() * Math.PI * 2;
      const phi = Math.random() * Math.PI;

      positions.push(
        r * Math.sin(phi) * Math.cos(theta),
        r * Math.sin(phi) * Math.sin(theta),
        r * Math.cos(phi)
      );
    }

    return new Float32Array(positions);
  }, []);

  useFrame(({ clock }) => {
    if (!points.current) return;

    const t = clock.getElapsedTime();

    points.current.rotation.y = t * 0.03;
    points.current.rotation.x = Math.sin(t * 0.2) * 0.15;

    // Breathing effect
    const scale = 1 + Math.sin(t * 1.5) * 0.03;
    points.current.scale.set(scale, scale, scale);
  });

  return (
    <points ref={points}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={particles.length / 3}
          array={particles}
          itemSize={3}
        />
      </bufferGeometry>

      <pointsMaterial
        color="#6EF7FF"
        size={0.02}
        transparent
        opacity={0.9}
        sizeAttenuation
        depthWrite={false}
      />
    </points>
  );
}