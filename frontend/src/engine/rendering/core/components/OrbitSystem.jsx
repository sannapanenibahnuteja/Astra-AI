import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

import { getCoreParameters } from "../CoreController";

export default function OrbitSystem() {

    const group = useRef();

    const ring1 = useRef();
    const ring2 = useRef();
    const ring3 = useRef();

    const color = useRef(
        new THREE.Color("#00E5FF")
    );

    useFrame((_, delta) => {

        if (!group.current) return;

        const core = getCoreParameters();

        color.current.set(core.color);

        const materials = [
            ring1.current,
            ring2.current,
            ring3.current
        ];

        materials.forEach((mat, index) => {

            if (!mat) return;

            mat.color.lerp(
                color.current,
                delta * 5
            );

            const targetOpacity =
                (0.10 + index * 0.04) *
                core.intensity;

            mat.opacity +=
                (targetOpacity - mat.opacity) *
                delta * 4;

        });

        group.current.rotation.y +=
            delta *
            core.speed *
            0.18;

        group.current.rotation.z +=
            delta *
            0.05;

    });

    return (

        <group ref={group}>

            {/* Horizontal Ring */}

            <mesh rotation={[Math.PI / 2,0,0]}>

                <torusGeometry
                    args={[1.45,0.004,16,256]}
                />

                <meshBasicMaterial

                    ref={ring1}

                    color="#00E5FF"

                    transparent

                    opacity={0.12}

                    toneMapped={false}

                />

            </mesh>

            {/* Tilted Ring */}

            <mesh rotation={[0.7,0.3,0]}>

                <torusGeometry
                    args={[1.72,0.0035,16,256]}
                />

                <meshBasicMaterial

                    ref={ring2}

                    color="#00E5FF"

                    transparent

                    opacity={0.08}

                    toneMapped={false}

                />

            </mesh>

            {/* Vertical Ring */}

            <mesh rotation={[0,Math.PI/2,0]}>

                <torusGeometry
                    args={[1.58,0.0035,16,256]}
                />

                <meshBasicMaterial

                    ref={ring3}

                    color="#00E5FF"

                    transparent

                    opacity={0.06}

                    toneMapped={false}

                />

            </mesh>

        </group>

    );

}