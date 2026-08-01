varying vec2 vUv;
varying vec3 vNormal;
varying vec3 vPosition;

void main()
{
    vUv = uv;

    // World-space normal
    vNormal = normalize(normalMatrix * normal);

    // View-space position
    vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
    vPosition = mvPosition.xyz;

    gl_Position =
        projectionMatrix *
        mvPosition;
}