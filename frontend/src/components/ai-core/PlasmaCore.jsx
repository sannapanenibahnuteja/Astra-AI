import { Float, MeshDistortMaterial } from "@react-three/drei";
import { useMemo } from "react";
import useAIStateStore from "../../../../store/aiStateStore";

export default function PlasmaCore() {
  const state = useAIStateStore((s) => s.state);

  const config = useMemo(() => {
    switch (state) {
      case "thinking":
        return {
          color: "#C026FF",
          emissive: 8,
          distort: 0.45,
          speed: 5.5,
          shellOpacity: 0.18,
          shellScale: 1.35,
        };

      case "speaking":
        return {
          color: "#FF9800",
          emissive: 8,
          distort: 0.30,
          speed: 3.2,
          shellOpacity: 0.16,
          shellScale: 1.28,
        };

      case "listening":
        return {
          color: "#2979FF",
          emissive: 7,
          distort: 0.25,
          speed: 2.2,
          shellOpacity: 0.12,
          shellScale: 1.22,
        };

      case "error":
        return {
          color: "#FF3030",
          emissive: 10,
          distort: 0.60,
          speed: 9,
          shellOpacity: 0.22,
          shellScale: 1.45,
        };

      default:
        return {
          color: "#35F6FF",
          emissive: 5,
          distort: 0.18,
          speed: 2,
          shellOpacity: 0.08,
          shellScale: 1.18,
        };
    }
  }, [state]);

  return (
    <Float
      speed={1.2}
      floatIntensity={0.2}
      rotationIntensity={0.15}
    >
      {/* Outer Energy Shell */}
      <mesh scale={config.shellScale}>
        <sphereGeometry args={[1, 64, 64]} />

        <meshBasicMaterial
          color={config.color}
          transparent
          opacity={config.shellOpacity}
          toneMapped={false}
        />
      </mesh>

      {/* Secondary Glow */}
      <mesh scale={config.shellScale + 0.18}>
        <sphereGeometry args={[1, 64, 64]} />

        <meshBasicMaterial
          color={config.color}
          transparent
          opacity={config.shellOpacity * 0.45}
          toneMapped={false}
        />
      </mesh>

      {/* Plasma */}
      <mesh>
        <icosahedronGeometry args={[0.95, 64]} />

        <MeshDistortMaterial
          color={config.color}
          emissive={config.color}
          emissiveIntensity={config.emissive}
          distort={config.distort}
          speed={config.speed}
          roughness={0}
          metalness={0}
          clearcoat={1}
          transparent
          opacity={0.94}
        />
      </mesh>

      {/* Bright Inner Core */}
      <mesh scale={0.22}>
        <sphereGeometry args={[1, 64, 64]} />

        <meshBasicMaterial
          color="#FFFFFF"
          toneMapped={false}
        />
      </mesh>
    </Float>
  );
}