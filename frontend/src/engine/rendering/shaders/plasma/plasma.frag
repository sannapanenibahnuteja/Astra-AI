uniform float uTime;
uniform vec3 uColor;
uniform float uIntensity;

varying vec3 vNormal;


void main()
{

    float pulse =
        0.8 +
        sin(uTime * 4.0) * 0.2;


    vec3 finalColor =
        uColor *
        uIntensity *
        pulse;


    gl_FragColor =
        vec4(
            finalColor,
            1.0
        );

}