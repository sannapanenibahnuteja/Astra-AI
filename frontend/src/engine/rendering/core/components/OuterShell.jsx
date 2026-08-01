import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

import { getCoreParameters } from "../CoreController";

export default function OuterShell() {

    const mesh = useRef();
    const material = useRef();

    const color = useRef(
        new THREE.Color("#00E5FF")
    );

    useFrame(({ clock }, delta) => {

        if(!mesh.current || !material.current)
            return;

        const core =
            getCoreParameters();

        color.current.set(core.color);

        material.current.color.lerp(
            color.current,
            delta * 6
        );

        material.current.opacity +=
            (
                (0.025 * core.intensity)
                -
                material.current.opacity
            ) *
            delta *
            4;

        mesh.current.rotation.y +=
            delta *
            0.05;

        mesh.current.rotation.x =
            Math.sin(
                clock.elapsedTime * 0.15
            ) *
            0.05;

        const scale =
            1.08 +
            Math.sin(
                clock.elapsedTime * 0.8
            ) *
            0.005;

        mesh.current.scale.setScalar(scale);

    });

    return(

        <mesh ref={mesh}>

            <icosahedronGeometry
                args={[1.02,96]}
            />

            <meshPhysicalMaterial

                ref={material}

                transmission={1}

                thickness={0.12}

                roughness={0.02}

                clearcoat={1}

                clearcoatRoughness={0}

                transparent

                opacity={0.02}

                color="#D8FFFF"

                metalness={0}

                toneMapped={false}

                depthWrite={false}

            />

        </mesh>

    );

}