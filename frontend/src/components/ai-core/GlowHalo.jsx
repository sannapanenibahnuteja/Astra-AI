export default function GlowHalo() {
  return (
    <mesh scale={1.35}>
      <sphereGeometry args={[1.72,1.82,256]} />

      <meshBasicMaterial
        color="#00E5FF"
        transparent
        opacity={0.002}
      />
    </mesh>
  );
}