uniform float uTime;
uniform vec3 uColor;
uniform float uIntensity;

varying vec2 vUv;
varying vec3 vNormal;
varying vec3 vPosition;

void main()
{
    vec3 N = normalize(vNormal);

    // Bright rim
    float fresnel =
        pow(
            1.0 - abs(N.z),
            4.5
        );

    // Slow breathing
    float pulse =
        0.95 +
        sin(uTime * 1.8) * 0.05;

    // Flowing energy
    float flow =
        sin(vUv.y * 35.0 + uTime * 3.0);

    flow +=
        sin(vUv.x * 26.0 - uTime * 2.2);

    flow *= 0.5;

    float energy =
        smoothstep(
            -0.2,
             0.8,
             flow
        );

    vec3 color =

        uColor * 0.06 +

        uColor * fresnel * 1.8 +

        uColor * energy * 0.28 +

        vec3(1.0) * fresnel * 0.08;

    color *= pulse;
    color *= uIntensity;

    gl_FragColor = vec4(color,1.0);
}