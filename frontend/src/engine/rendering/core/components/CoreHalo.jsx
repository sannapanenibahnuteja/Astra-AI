import { useRef } from "react";
import { useFrame } from "@react-three/fiber";

export default function CoreHalo() {

    const halo = useRef();

    useFrame(({ clock }) => {

        if (!halo.current) return;

        halo.current.rotation.z =
            clock.getElapsedTime() * 0.08;

    });

    return (

        <mesh
            ref={halo}
            rotation={[-Math.PI / 2, 0, 0]}
        >

            <ringGeometry
                args={[0.82,0.86,256]}
            />

            <meshBasicMaterial

                color="#7FF8FF"

                transparent

                opacity={0.06}

                toneMapped={false}

                side={2}

                depthWrite={false}

            />

        </mesh>

    );

}