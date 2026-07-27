import { MeshDistortMaterial } from "@react-three/drei";
import OrbitRing from "./OrbitRing";

export default function EnergySphere() {
  return (
    <>
      {/* Glow Halo */}
      <mesh scale={1.45}>
        <sphereGeometry args={[1, 64, 64]} />
        <meshBasicMaterial
          color="#00E5FF"
          transparent
          opacity={0.08}
        />
      </mesh>

      {/* Energy Core */}
      <mesh>
        <icosahedronGeometry args={[1, 64]} />

        <MeshDistortMaterial
          color="#00E5FF"
          emissive="#00E5FF"
          emissiveIntensity={8}
          distort={0.22}
          speed={2}
          roughness={0}
          metalness={0}
        />
      </mesh>

      {/* Orbit Rings */}
      <OrbitRing
        radius={1.55}
        speed={0.012}
      />

      <OrbitRing
        radius={1.95}
        speed={-0.008}
        rotation={[Math.PI / 2, 0, 0]}
      />

      <OrbitRing
        radius={2.35}
        speed={0.006}
        rotation={[0, Math.PI / 2, 0]}
      />
    </>
  );
}