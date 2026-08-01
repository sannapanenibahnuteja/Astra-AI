import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

import { getCoreParameters } from "../CoreController";

export default function Shockwave() {

    const mesh = useRef();
    const material = useRef();

    const color = useRef(
        new THREE.Color("#00E5FF")
    );

    const scale = useRef(1);
    const opacity = useRef(0);

    const lastColor = useRef("");

    useFrame((_, delta) => {

        if (!mesh.current || !material.current)
            return;

        const core = getCoreParameters();

        color.current.set(core.color);

        if(lastColor.current !== core.color){

            scale.current = 1;

            opacity.current = 0.10;

            lastColor.current = core.color;

        }

        scale.current +=
            delta *
            0.45;

        opacity.current -=
            delta *
            0.12;

        if(scale.current > 2.0){

            scale.current = 1;

            opacity.current = 0;

        }

        mesh.current.scale.setScalar(
            scale.current
        );

        material.current.opacity =
            Math.max(opacity.current,0);

        material.current.color.lerp(
            color.current,
            delta * 6
        );

    });

    return(

        <mesh
            ref={mesh}
            rotation={[-Math.PI/2,0,0]}
        >

            <ringGeometry
                args={[0.95,0.98,256]}
            />

            <meshBasicMaterial

                ref={material}

                color="#00E5FF"

                transparent

                opacity={0}

                side={THREE.DoubleSide}

                depthWrite={false}

                toneMapped={false}

            />

        </mesh>

    );

}