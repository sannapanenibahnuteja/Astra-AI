import HolographicRing from "./HolographicRing";
import EnergyArc from "./EnergyArc";

const rings = [
  { radius: 1.45, speed: 0.010, rotation: [0, 0, 0] },

  { radius: 1.75, speed: -0.007, rotation: [Math.PI / 3, 0, 0] },

  { radius: 2.05, speed: 0.005, rotation: [0, Math.PI / 3, 0] },

  { radius: 2.35, speed: -0.004, rotation: [Math.PI / 2, 0, 0] },

  { radius: 2.65, speed: 0.003, rotation: [0, Math.PI / 2, 0] },

  { radius: 2.95, speed: -0.0025, rotation: [Math.PI / 4, Math.PI / 4, 0] },

  { radius: 3.25, speed: 0.0018, rotation: [0, Math.PI / 6, Math.PI / 6] },
];

export default function OrbitSystem() {
  return (
    <>
      {rings.map((ring, index) => (
        <group key={index}>
          <HolographicRing {...ring} />

          <EnergyArc
            radius={ring.radius}
            rotation={ring.rotation}
            speed={1 + index * 0.35}
          />
        </group>
      ))}
    </>
  );
}