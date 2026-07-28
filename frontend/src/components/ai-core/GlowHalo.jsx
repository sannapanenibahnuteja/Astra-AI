export default function GlowHalo() {
  return (
    <mesh scale={1.35}>
      <sphereGeometry args={[1, 32, 32]} />

      <meshBasicMaterial
        color="#00E5FF"
        transparent
        opacity={0.08}
      />
    </mesh>
  );
}