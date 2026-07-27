import { Canvas } from "@react-three/fiber";
import { OrbitControls, Environment } from "@react-three/drei";
import { EffectComposer, Bloom } from "@react-three/postprocessing";

import EnergySphere from "../core3d/EnergySphere";

export default function AICore() {
  return (
    <div
      style={{
        width: "520px",
        height: "520px",
      }}
    >
      <Canvas
        camera={{ position: [0, 0, 6], fov: 50 }}
        gl={{
          alpha: true,
          antialias: true,
          powerPreference: "high-performance",
        }}
      >
        <ambientLight intensity={0.4} />

        <pointLight
          position={[4, 4, 4]}
          intensity={25}
          color="#00E5FF"
        />

        <pointLight
          position={[-4, -4, -4]}
          intensity={15}
          color="#0099FF"
        />

        <EnergySphere />

        <Environment preset="night" />

        <EffectComposer>
          <Bloom
            intensity={2}
            luminanceThreshold={0}
            luminanceSmoothing={0.8}
          />
        </EffectComposer>

        <OrbitControls
          enableZoom={false}
          enablePan={false}
          autoRotate
          autoRotateSpeed={0.35}
        />
      </Canvas>
    </div>
  );
}