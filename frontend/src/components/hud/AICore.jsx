import "./AICore.css";

import { Canvas } from "@react-three/fiber";
import { OrbitControls, Environment } from "@react-three/drei";
import { EffectComposer, Bloom } from "@react-three/postprocessing";

import { NebulaCore } from "../ai-core";




export default function AICore() {

  return (

    <div className="ai-core-container">


      {/* System Information HUD */}
      



<Canvas

    style={{

        width: "100%",

        height: "100%",

    }}

    camera={{

        position: [0, 0, 5.2],

        fov: 42,

    }}

    gl={{

        alpha: true,

        antialias: true,

        powerPreference: "high-performance",

    }}

    onCreated={({ gl }) => {

        gl.setClearColor("#000000", 0);

    }}

>


        {/* Ambient */}

        <ambientLight
          intensity={0.02}
        />



        {/* Main Cyan Light */}

        <pointLight

          position={[5,3,5]}

          intensity={28}

          color="#35F6FF"

        />



        {/* Blue Rim Light */}

        <pointLight

          position={[-5,-3,-5]}

          intensity={12}

          color="#2979FF"

        />



        {/* White Highlight */}

        <pointLight

          position={[0,7,2]}

          intensity={14}

          color="#FFFFFF"

        />



        {/* Bottom Fill */}

        <pointLight

          position={[0,-6,0]}

          intensity={8}

          color="#35F6FF"

        />



        {/* Astra Core */}

        <NebulaCore />





        <EffectComposer
          multisampling={8}
        >

          <Bloom

            intensity={0.18}

            luminanceThreshold={0.60}

            luminanceSmoothing={0.95}

            mipmapBlur

          />

        </EffectComposer>



        <OrbitControls

          enableZoom={false}

          enablePan={false}

          autoRotate

          autoRotateSpeed={0.02}

          minPolarAngle={
            Math.PI / 2.2
          }

          maxPolarAngle={
            Math.PI / 1.8
          }

        />


      </Canvas>


    </div>

  );

}