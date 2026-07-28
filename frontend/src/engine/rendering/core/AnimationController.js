import * as THREE from "three";


export function updateCore(
  material,
  mesh,
  core,
  delta,
  time
) {


  if (!material || !mesh)
    return;



  console.log(
    "CORE COLOR:",
    core.color
  );



  material.uTime =
    time;



  if(material.uColor){

    material.uColor.lerp(
      new THREE.Color(core.color),
      delta * 10
    );

  }



  if(material.uSpeed !== undefined){

    material.uSpeed =
      core.speed;

  }



  if(material.uIntensity !== undefined){

    material.uIntensity =
      core.intensity;

  }



  mesh.rotation.y +=
    delta * 0.5;



  mesh.scale.setScalar(
    1 +
    Math.sin(time * 3)
    *
    0.05
  );

}