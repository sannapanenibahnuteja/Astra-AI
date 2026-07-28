import GlowHalo from "../../engine/rendering/core/components/GlowHalo";
import CoreHalo from "../../engine/rendering/core/components/CoreHalo";
import EnergyField from "../../engine/rendering/core/components/EnergyField";
import ParticleCloud from "../../engine/rendering/core/components/ParticleCloud";
import OrbitSystem from "../../engine/rendering/core/components/OrbitSystem";
import PlasmaCore from "../../engine/rendering/core/components/PlasmaCore";

export default function NebulaCore() {
  return (
    <>
      <GlowHalo />

      <EnergyField />

      <CoreHalo />

      <ParticleCloud />

      <OrbitSystem />

      <PlasmaCore />
    </>
  );
}