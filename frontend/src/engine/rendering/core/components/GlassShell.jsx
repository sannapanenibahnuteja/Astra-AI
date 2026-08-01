import { useFrame } from "@react-three/fiber";
import { useRef } from "react";

export default function GlassShell() {

    const shell = useRef();

    useFrame(({ clock }) => {

        if (!shell.current) return;

        shell.current.rotation.y =
            clock.getElapsedTime() * 0.05;

        shell.current.rotation.x =
            Math.sin(clock.getElapsedTime() * 0.25) * 0.05;

    });

    return (

        <mesh ref={shell}>

            <icosahedronGeometry args={[1.08,96]} />

            <meshPhysicalMaterial

                transparent

                transmission={1}

                thickness={0.45}

                roughness={0.02}

                metalness={0}

                clearcoat={1}

                clearcoatRoughness={0.02}

                opacity={0.04}

                color="#A8F8FF"

                emissive="#00E5FF"

                emissiveIntensity={0.05}

            />

        </mesh>

    );

}