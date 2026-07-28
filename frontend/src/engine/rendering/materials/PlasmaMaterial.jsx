import { shaderMaterial } from "@react-three/drei";
import * as THREE from "three";

import vertexShader from "../shaders/plasma/plasma.vert?raw";
import fragmentShader from "../shaders/plasma/plasma.frag?raw";

const PlasmaMaterial = shaderMaterial(
  {
    uTime: 0,
    uColor: new THREE.Color("#35F6FF"),
  },
  vertexShader,
  fragmentShader
);

export default PlasmaMaterial;