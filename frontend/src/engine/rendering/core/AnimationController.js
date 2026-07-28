import * as THREE from "three";

const colour = new THREE.Color();

export function updateCore(
  material,
  mesh,
  target,
  delta,
  time
) {
  if (!material || !mesh) return;

  material.uTime = time;

  colour.set(target.colour);

  material.uColor.lerp(colour, delta * 5);

  material.uSpeed +=
    (target.speed - material.uSpeed) *
    delta *
    5;

  material.uIntensity +=
    (target.intensity - material.uIntensity) *
    delta *
    5;

  mesh.rotation.y += delta * 0.4;

  const pulse =
    1 +
    Math.sin(time * material.uSpeed) *
      0.04 *
      material.uIntensity;

  mesh.scale.setScalar(pulse);
}