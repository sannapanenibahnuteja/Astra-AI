import { useRef } from "react";
import { useFrame } from "@react-three/fiber";

import { getCoreParameters } from "../CoreController";
import { updateCore } from "../AnimationController";
import useAudioStore from "../../../../store/audioStore";


export default function PlasmaCore() {

  const material = useRef();
  const mesh = useRef();


  const updateLevel =
    useAudioStore(
      (s)=>s.updateLevel
    );



  useFrame(
    ({clock}, delta)=>{


      if(
        !material.current ||
        !mesh.current
      )
        return;



      updateLevel();



      const core =
        getCoreParameters();



      updateCore(
        material.current,
        mesh.current,
        core,
        delta,
        clock.getElapsedTime()
      );


    }
  );



  return (

    <mesh ref={mesh}>

      <icosahedronGeometry
        args={[0.92,96]}
      />


      <plasmaMaterial
        ref={material}
      />


    </mesh>

  );

}