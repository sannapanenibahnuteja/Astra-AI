export default function CoreHalo() {
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]}>
      <ringGeometry args={[1.15, 1.35, 128]} />

      <meshBasicMaterial
        color="#35F6FF"
        transparent
        opacity={0.2}
        toneMapped={false}
        side={2}
      />
    </mesh>
  );
}