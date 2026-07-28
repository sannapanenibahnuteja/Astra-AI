import { useRef } from "react";
import { useFrame } from "@react-three/fiber";

import { getCoreParameters } from "../CoreController";
import { updateCore } from "../AnimationController";


export default function PlasmaCore() {
  const material = useRef();
  const mesh = useRef();


  useFrame(({ clock }, delta) => {
    if (!material.current || !mesh.current) return;


    const core = getCoreParameters();


    updateCore(
      material.current,
      mesh.current,
      core,
      delta,
      clock.getElapsedTime()
    );
  });


  return (
    <mesh ref={mesh}>

      <icosahedronGeometry
        args={[
          1,
          64,
        ]}
      />

      <plasmaMaterial
        ref={material}
      />

    </mesh>
  );
}