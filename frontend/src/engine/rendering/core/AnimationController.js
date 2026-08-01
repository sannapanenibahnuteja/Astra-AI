import * as THREE from "three";

export function updateCore(
    material,
    mesh,
    core,
    delta,
    time
){

    if(!material || !mesh)
        return;

    material.uTime = time;

    // Smooth colour transition
    if(material.uColor){

        material.uColor.lerp(

            new THREE.Color(core.color),

            delta * 6

        );

    }

    // Smooth intensity
    if(material.uIntensity !== undefined){

        material.uIntensity +=
            (core.intensity - material.uIntensity) *
            delta * 5;

    }

    // Smooth speed
    if(material.uSpeed !== undefined){

        material.uSpeed +=
            (core.speed - material.uSpeed) *
            delta * 4;

    }

    //---------------------------------------------------
    // Different behaviour for each AI state
    //---------------------------------------------------

    let rotationSpeed = 0.12;
    let pulseSpeed = 1.1;
    let pulseAmount = 0.012;

    switch(core.aiState){

        case "listening":

            rotationSpeed = 0.25;
            pulseSpeed = 2.2;
            pulseAmount = 0.02;
            break;

        case "thinking":

            rotationSpeed = 0.65;
            pulseSpeed = 3.8;
            pulseAmount = 0.05;
            break;

        case "speaking":

            rotationSpeed = 0.35;
            pulseSpeed = 2.8;
            pulseAmount = 0.028;
            break;

        case "executing":

            rotationSpeed = 1.2;
            pulseSpeed = 6.5;
            pulseAmount = 0.07;
            break;

        case "error":

            rotationSpeed = 0.08;
            pulseSpeed = 8.0;
            pulseAmount = 0.09;
            break;

        default:

            rotationSpeed = 0.12;
            pulseSpeed = 1.1;
            pulseAmount = 0.012;

    }

    //---------------------------------------------------
    // Reactor rotation
    //---------------------------------------------------

    mesh.rotation.y +=
        delta * rotationSpeed;

    mesh.rotation.x =
        Math.sin(time * 0.25) * 0.03;

    //---------------------------------------------------
    // Reactor breathing
    //---------------------------------------------------

    const targetScale =

        1 +

        Math.sin(
            time * pulseSpeed
        ) * pulseAmount;

    mesh.scale.lerp(

        new THREE.Vector3(
            targetScale,
            targetScale,
            targetScale
        ),

        delta * 4

    );

}