import { useEffect, useRef } from 'react';
import * as THREE from 'three';

const DigitalPetalsShader = () => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    // Renderer, Scene, Camera, Clock
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    const scene = new THREE.Scene();
    const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    const clock = new THREE.Clock();

    // Vertex Shader
    const vertexShader = `
      void main() {
        gl_Position = vec4(position, 1.0);
      }
    `;

    // Fragment Shader with Calyx Colors and constant blooming
    const fragmentShader = `
      precision highp float;
      uniform vec2 iResolution;
      uniform float iTime;
      uniform vec2 iMouse;

      float random(vec2 st) {
        return fract(sin(dot(st.xy, vec2(12.9898, 78.233))) * 43758.5453123);
      }

      void main() {
        // Normalize coords around center, scale by height
        vec2 uv = (gl_FragCoord.xy - 0.5 * iResolution.xy) / iResolution.y;
        vec2 mouse = (iMouse - 0.5 * iResolution.xy) / iResolution.y;

        float t = iTime * 0.4;

        float r = length(uv);
        float a = atan(uv.y, uv.x);

        // Mouse bloom effect
        float mouseDist = length(uv - mouse);
        float mouseBloom = smoothstep(0.5, 0.0, mouseDist) * 0.3;

        // Continuous blooming animation - petals pulse outward
        float bloomPulse = sin(t * 1.5) * 0.5 + 0.5;
        float bloomWave = sin(r * 8.0 - t * 3.0) * 0.5 + 0.5;
        float constantBloom = bloomPulse * bloomWave * 0.4;

        // Petal shape calculation with animated count
        float petals = 6.0 + sin(t * 0.5) * 1.0;
        float petalShape = sin(a * petals + r * 3.0 - t);
        petalShape = pow(abs(petalShape), 0.4);

        // Flowing ripple effect
        float flow = sin(r * 12.0 - t * 2.5) * 0.5 + 0.5;
        
        // Combine patterns with bloom
        float pattern = mix(petalShape, flow, 0.4);
        pattern += constantBloom + mouseBloom;
        pattern = clamp(pattern, 0.0, 1.5);

        // CALYX COLOR SCHEME
        vec3 botanicalGreen = vec3(0.176, 0.314, 0.086);
        vec3 petalPink = vec3(0.910, 0.706, 0.722);
        vec3 cream = vec3(0.961, 0.945, 0.910);
        
        // Color mixing based on radius and time
        float colorMix = smoothstep(0.3, 0.9, r + sin(t * 0.8) * 0.1);
        vec3 baseColor = mix(botanicalGreen, petalPink, colorMix);
        
        vec3 finalColor = baseColor * pattern;

        // Add cream highlights on bloom peaks
        float highlight = pow(pattern, 6.0) * (1.0 + constantBloom + mouseBloom);
        finalColor += cream * highlight * 0.8;

        // Subtle vignette
        float vignette = 1.0 - smoothstep(0.5, 1.2, r);
        finalColor *= vignette * 0.9 + 0.1;

        gl_FragColor = vec4(finalColor, 1.0);
      }
    `;

    // Uniforms, Material, Mesh
    const uniforms = {
      iTime: { value: 0 },
      iResolution: { value: new THREE.Vector2() },
      iMouse: { value: new THREE.Vector2(window.innerWidth / 2, window.innerHeight / 2) }
    };

    const material = new THREE.ShaderMaterial({ vertexShader, fragmentShader, uniforms });
    const geometry = new THREE.PlaneGeometry(2, 2);
    const mesh = new THREE.Mesh(geometry, material);
    scene.add(mesh);

    // Resize handler
    const onResize = () => {
      const width = container.clientWidth;
      const height = container.clientHeight;
      renderer.setSize(width, height);
      uniforms.iResolution.value.set(width, height);
    };
    window.addEventListener('resize', onResize);
    onResize();

    // Mouse handler
    const onMouseMove = (e: MouseEvent) => {
      uniforms.iMouse.value.set(e.clientX, container.clientHeight - e.clientY);
    };
    window.addEventListener('mousemove', onMouseMove);

    // Animation loop
    renderer.setAnimationLoop(() => {
      uniforms.iTime.value = clock.getElapsedTime();
      renderer.render(scene, camera);
    });

    // Cleanup
    return () => {
      window.removeEventListener('resize', onResize);
      window.removeEventListener('mousemove', onMouseMove);
      renderer.setAnimationLoop(null);

      const canvas = renderer.domElement;
      if (canvas && canvas.parentNode) {
        canvas.parentNode.removeChild(canvas);
      }

      material.dispose();
      geometry.dispose();
      renderer.dispose();
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
