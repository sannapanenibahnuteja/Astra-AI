import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { DoubleSide } from "three";

export default function EnergyField() {

    const field = useRef();

    useFrame(({ clock }) => {

        if (!field.current) return;

        const t = clock.getElapsedTime();

        field.current.rotation.z = t * 0.025;

        const scale =
            1 +
            Math.sin(t * 0.6) * 0.01;

        field.current.scale.setScalar(scale);

    });

    return (

        <mesh
            ref={field}
            rotation={[-Math.PI / 2, 0, 0]}
        >

            <ringGeometry args={[2.15, 2.35, 256]} />

            <meshBasicMaterial

                color="#00E5FF"

                transparent

                opacity={0.022}

                side={DoubleSide}

                depthWrite={false}

                toneMapped={false}

            />

        </mesh>

    );

}