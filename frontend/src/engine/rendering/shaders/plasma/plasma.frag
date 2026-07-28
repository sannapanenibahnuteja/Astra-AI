uniform float uTime;
uniform vec3 uColor;

varying vec2 vUv;

void main()
{
    vec2 uv = vUv - 0.5;

    float r = length(uv);

    float wave =
        sin(12.0*r - uTime*3.0);

    float glow =
        0.12/(r+0.08);

    float pulse =
        0.5 + 0.5*sin(uTime*2.0);

    vec3 color =
        uColor * glow *
        (1.0 + 0.4*wave) *
        pulse;

    gl_FragColor =
        vec4(color,1.0);
}