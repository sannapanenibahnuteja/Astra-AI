import "./AICore.css";

import { Canvas } from "@react-three/fiber";
import { OrbitControls, Environment } from "@react-three/drei";
import { EffectComposer, Bloom } from "@react-three/postprocessing";

import { NebulaCore } from "../ai-core";

import SystemHUD from "../hud/SystemHUD";


export default function AICore() {

  return (

    <div className="ai-core-container">


      {/* System Information HUD */}
      <SystemHUD />



      <Canvas

        style={{

          width: "100%",

          height: "100%",

        }}


        camera={{

          position: [0,0,5.2],

          fov:42,

        }}


        gl={{

          alpha:true,

          antialias:true,

          powerPreference:
            "high-performance",

        }}

      >


        {/* Ambient */}

        <ambientLight
          intensity={0.08}
        />



        {/* Main Cyan Light */}

        <pointLight

          position={[5,3,5]}

          intensity={70}

          color="#35F6FF"

        />



        {/* Blue Rim Light */}

        <pointLight

          position={[-5,-3,-5]}

          intensity={30}

          color="#2979FF"

        />



        {/* White Highlight */}

        <pointLight

          position={[0,7,2]}

          intensity={35}

          color="#FFFFFF"

        />



        {/* Bottom Fill */}

        <pointLight

          position={[0,-6,0]}

          intensity={18}

          color="#35F6FF"

        />



        {/* Astra Core */}

        <NebulaCore />



        <Environment
          preset="night"
        />



        <EffectComposer
          multisampling={8}
        >

          <Bloom

            intensity={3.0}

            luminanceThreshold={0.12}

            luminanceSmoothing={0.55}

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