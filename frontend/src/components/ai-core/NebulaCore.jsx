import { Float } from "@react-three/drei";

import GlowHalo from "../../engine/rendering/core/components/GlowHalo";
import Shockwave from "../../engine/rendering/core/components/Shockwave";
import OuterShell from "../../engine/rendering/core/components/OuterShell";
import EnergyArcs from "../../engine/rendering/core/components/EnergyArcs";
import EnergyField from "../../engine/rendering/core/components/EnergyField";
import CoreHalo from "../../engine/rendering/core/components/CoreHalo";
import ParticleCloud from "../../engine/rendering/core/components/ParticleCloud";
import OrbitSystem from "../../engine/rendering/core/components/OrbitSystem";
import PlasmaCore from "../../engine/rendering/core/components/PlasmaCore";

export default function NebulaCore() {
  return (
    <Float
      speed={1.4}
      floatIntensity={0.25}
      rotationIntensity={0.18}
    >
      <GlowHalo />

      <Shockwave />

      <OuterShell />

      <EnergyArcs />

      <EnergyField />

      <CoreHalo />

      <ParticleCloud />

      <OrbitSystem />

      <PlasmaCore />
    </Float>
  );
}