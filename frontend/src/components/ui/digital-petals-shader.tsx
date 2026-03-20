import { useEffect, useRef } from 'react';
import * as THREE from 'three';

const DigitalPetalsShader = () => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    let renderer: THREE.WebGLRenderer | null = null;
    let material: THREE.ShaderMaterial | null = null;
    let geometry: THREE.PlaneGeometry | null = null;
    let animationIdActive = true;

    try {
      renderer = new THREE.WebGLRenderer({
        antialias: true,
        alpha: true,
        powerPreference: 'low-power',
      });

      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      container.appendChild(renderer.domElement);
    } catch (error) {
      console.warn('DigitalPetalsShader: WebGL unavailable, skipping shader.', error);
      return;
    }

    const scene = new THREE.Scene();
    const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    const clock = new THREE.Clock();

    const vertexShader = `
      void main() {
        gl_Position = vec4(position, 1.0);
      }
    `;

    const fragmentShader = `
      precision highp float;
      uniform vec2 iResolution;
      uniform float iTime;
      uniform vec2 iMouse;

      float random(vec2 st) {
        return fract(sin(dot(st.xy, vec2(12.9898, 78.233))) * 43758.5453123);
      }

      void main() {
        vec2 uv = (gl_FragCoord.xy - 0.5 * iResolution.xy) / iResolution.y;
        vec2 mouse = (iMouse - 0.5 * iResolution.xy) / iResolution.y;

        float t = iTime * 0.4;
        float r = length(uv);
        float a = atan(uv.y, uv.x);

        float mouseDist = length(uv - mouse);
        float mouseBloom = smoothstep(0.5, 0.0, mouseDist) * 0.3;

        float bloomPulse = sin(t * 1.5) * 0.5 + 0.5;
        float bloomWave = sin(r * 8.0 - t * 3.0) * 0.5 + 0.5;
        float constantBloom = bloomPulse * bloomWave * 0.4;

        float petals = 6.0 + sin(t * 0.5) * 1.0;
        float petalShape = sin(a * petals + r * 3.0 - t);
        petalShape = pow(abs(petalShape), 0.4);

        float flow = sin(r * 12.0 - t * 2.5) * 0.5 + 0.5;

        float pattern = mix(petalShape, flow, 0.4);
        pattern += constantBloom + mouseBloom;
        pattern = clamp(pattern, 0.0, 1.5);

        vec3 botanicalGreen = vec3(0.176, 0.314, 0.086);
        vec3 petalPink = vec3(0.910, 0.706, 0.722);
        vec3 cream = vec3(0.961, 0.945, 0.910);

        float colorMix = smoothstep(0.3, 0.9, r + sin(t * 0.8) * 0.1);
        vec3 baseColor = mix(botanicalGreen, petalPink, colorMix);

        vec3 finalColor = baseColor * pattern;

        float highlight = pow(pattern, 6.0) * (1.0 + constantBloom + mouseBloom);
        finalColor += cream * highlight * 0.8;

        float vignette = 1.0 - smoothstep(0.5, 1.2, r);
        finalColor *= vignette * 0.9 + 0.1;

        gl_FragColor = vec4(finalColor, 1.0);
      }
    `;

    const uniforms = {
      iTime: { value: 0 },
      iResolution: { value: new THREE.Vector2() },
      iMouse: { value: new THREE.Vector2(window.innerWidth / 2, window.innerHeight / 2) },
    };

    material = new THREE.ShaderMaterial({ vertexShader, fragmentShader, uniforms });
    geometry = new THREE.PlaneGeometry(2, 2);
    const mesh = new THREE.Mesh(geometry, material);
    scene.add(mesh);

    const onResize = () => {
      if (!renderer || !container) return;
      const width = container.clientWidth;
      const height = container.clientHeight;

      if (width === 0 || height === 0) return;

      renderer.setSize(width, height, false);
      uniforms.iResolution.value.set(width, height);
    };

    const onMouseMove = (e: MouseEvent) => {
      uniforms.iMouse.value.set(e.clientX, container.clientHeight - e.clientY);
    };

    window.addEventListener('resize', onResize);
    window.addEventListener('mousemove', onMouseMove);
    onResize();

    renderer.setAnimationLoop(() => {
      if (!renderer || !animationIdActive) return;
      uniforms.iTime.value = clock.getElapsedTime();
      renderer.render(scene, camera);
    });

    return () => {
      animationIdActive = false;
      window.removeEventListener('resize', onResize);
      window.removeEventListener('mousemove', onMouseMove);

      if (renderer) {
        renderer.setAnimationLoop(null);
        const canvas = renderer.domElement;
        if (canvas && canvas.parentNode) {
          canvas.parentNode.removeChild(canvas);
        }
        renderer.dispose();
      }

      material?.dispose();
      geometry?.dispose();
    };
  }, []);

  return (
    <div
      ref={containerRef}
      aria-label="Animated floral background pattern"
      className="absolute inset-0 pointer-events-none"
    />
  );
};

export default DigitalPetalsShader;