import { useRef, useMemo } from "react";
import { useFrame } from "@react-three/fiber";

import useAudioStore from "../../../../store/audioStore";
import { getCoreParameters } from "../CoreController";

export default function ParticleCloud() {

    const points = useRef();

    const audioLevel = useAudioStore(
        (state)=>state.level
    );

    const particleCount = 96;

    const positions = useMemo(()=>{

        const data = new Float32Array(
            particleCount * 3
        );

        for(let i=0;i<particleCount;i++){

            const radius =
                1.9 +
                Math.random()*0.9;

            const theta =
                Math.random() *
                Math.PI * 2;

            const phi =
                Math.acos(
                    2*Math.random()-1
                );

            data[i*3] =
                radius *
                Math.sin(phi) *
                Math.cos(theta);

            data[i*3+1] =
                radius *
                Math.cos(phi);

            data[i*3+2] =
                radius *
                Math.sin(phi) *
                Math.sin(theta);

        }

        return data;

    },[]);



    useFrame(({clock},delta)=>{

        if(!points.current)
            return;

        const core =
            getCoreParameters();

        const pulse =
            1 +
            Math.sin(
                clock.elapsedTime *
                core.speed
            ) *
            0.01;

        const voice =
            1 +
            audioLevel *
            0.03;

        points.current.scale.setScalar(
            pulse * voice
        );

        points.current.rotation.y +=
            delta *
            0.05;

        points.current.rotation.x +=
            delta *
            0.01;

    });

    return(

        <points ref={points}>

            <bufferGeometry>

                <bufferAttribute

                    attach="attributes-position"

                    count={particleCount}

                    array={positions}

                    itemSize={3}

                />

            </bufferGeometry>

            <pointsMaterial

                size={0.012}

                color="#7FF8FF"

                transparent

                opacity={0.22}

                sizeAttenuation

                depthWrite={false}

            />

        </points>

    );

}