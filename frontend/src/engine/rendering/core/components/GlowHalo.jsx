import { useRef } from "react";
import { useFrame } from "@react-three/fiber";

export default function GlowHalo() {

    const halo = useRef();

    useFrame(({ clock }) => {

        if(!halo.current) return;

        const t = clock.getElapsedTime();

        halo.current.scale.setScalar(

            1.02 +

            Math.sin(t * 0.8) * 0.004

        );

    });

    return(

        <mesh ref={halo}>

            <sphereGeometry
                args={[0.76,64,64]}
            />

            <meshBasicMaterial

                color="#7FF8FF"

                transparent

                opacity={0.015}

                depthWrite={false}

                toneMapped={false}

            />

        </mesh>

    );

}