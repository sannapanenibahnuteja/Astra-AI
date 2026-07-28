import { useFrame } from "@react-three/fiber";
import { useRef } from "react";

export default function EnergyArc({

    radius,

    speed = 1,

    rotation = [0,0,0]

}){

    const group = useRef();

    useFrame(({clock})=>{

        const t = clock.getElapsedTime()*speed;

        if(group.current){

            group.current.position.x =
                Math.cos(t)*radius;

            group.current.position.y =
                Math.sin(t)*radius;

        }

    });

    return(

        <group
            ref={group}
            rotation={rotation}
        >

            <mesh>

                <sphereGeometry
                    args={[0.05,16,16]}
                />

                <meshBasicMaterial
    color="#FFFFFF"
    toneMapped={false}
/>

            </mesh>

        </group>

    );

}