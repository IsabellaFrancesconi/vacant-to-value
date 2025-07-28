import React, { useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";

function StarfieldBackground() {
  const starCount = 4000;

  const positions = useMemo(() => {
    const arr = new Float32Array(starCount * 3);
    for (let i = 0; i < starCount * 3; i++) {
      arr[i] = (Math.random() - 0.5) * 1000;
    }
    return arr;
  }, []);

  const velocities = useMemo(() => {
    const arr = new Float32Array(starCount);
    for (let i = 0; i < starCount; i++) {
      arr[i] = Math.random() * 0.2 + 0.02;
    }
    return arr;
  }, []);

  const ref = useRef();

  useFrame(() => {
    const pos = ref.current.geometry.attributes.position.array;
    for (let i = 0; i < starCount; i++) {
      pos[i * 3 + 2] += velocities[i];
      if (pos[i * 3 + 2] > 500) {
        pos[i * 3 + 2] = -500;
      }
    }
    ref.current.geometry.attributes.position.needsUpdate = true;
  });

  return (
    <points ref={ref}>
      <bufferGeometry attach="geometry">
        <bufferAttribute
          attach="attributes-position"
          count={positions.length / 3}
          array={positions}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial color="#ffffff" size={1} sizeAttenuation />
    </points>
  );
}

export default function Starfield() {
  return (
    <div style={{ position: "fixed", inset: 0, zIndex: -1 }}>
      <Canvas camera={{ position: [0, 0, 1] }}>
        <StarfieldBackground />
      </Canvas>
    </div>
  );
}
