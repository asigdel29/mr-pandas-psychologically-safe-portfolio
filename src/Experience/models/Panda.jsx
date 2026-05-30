import React, { useRef, useState, useMemo } from "react";
import { useGLTF } from "@react-three/drei";
import { useKTX2Texture } from "../utils/ktxLoader";
import { useScrollCurve } from "../hooks/useScrollCurve";
import * as THREE from "three";
import { useFrame } from "@react-three/fiber";
import {
  initialPandaPoints,
  PANDA_SHIFT_X_AMOUNT,
  pandaCurve,
} from "../components/curve";

export default function Model({ scrollProgress, cameraScrollCurve, ...props }) {
  const { nodes, materials } = useGLTF("/models/Panda.glb");
  const regular = useKTX2Texture("/textures/regular.ktx2?v=3");
  const samurai = useKTX2Texture("/textures/samurai.ktx2?v=3");
  const pirate = useKTX2Texture("/textures/pirate.ktx2?v=3");
  const desert = useKTX2Texture("/textures/desert.ktx2?v=3");
  const zombie = useKTX2Texture("/textures/zombie.ktx2?v=3");
  const pandaRef = useRef();

  const textureMap = useMemo(
    () => [
      { threshold: 0, texture: regular, name: "regular" },
      { threshold: 0.136, texture: samurai, name: "samurai" },
      { threshold: 0.306, texture: pirate, name: "pirate" },
      { threshold: 0.501, texture: desert, name: "desert" },
      { threshold: 0.603, texture: zombie, name: "zombie" },
      { threshold: 0.705, texture: regular, name: "regular" },
    ],
    [regular, samurai, pirate, desert, zombie]
  );

  const getCurrentTexture = (progress) => {
    let currentTexture = textureMap[0];

    for (let i = textureMap.length - 1; i >= 0; i--) {
      if (progress >= textureMap[i].threshold) {
        currentTexture = textureMap[i];
        break;
      }
    }

    return currentTexture.texture;
  };

  const [randomOffset] = useState(() => ({
    position: new THREE.Vector3(),
    rotation: new THREE.Euler(),
    time: 0,
  }));

  const currentTextureRef = useRef(regular);

  const pandaScrollCurve = useScrollCurve(
    pandaCurve,
    initialPandaPoints,
    PANDA_SHIFT_X_AMOUNT
  );

  useFrame((state, delta) => {
    if (pandaRef.current && scrollProgress && cameraScrollCurve) {
      let currentProgress = scrollProgress.current;
      if (!cameraScrollCurve.transitionCurveActive.current) {
        const newTexture = getCurrentTexture(currentProgress);
        if (newTexture !== currentTextureRef.current) {
          currentTextureRef.current = newTexture;
          if (pandaRef.current) {
            pandaRef.current.material = newTexture;
          }
        }
      }

      if (
        cameraScrollCurve.transitionCurveActive.current !==
        pandaScrollCurve.transitionCurveActive.current
      ) {
        pandaScrollCurve.transitionCurveActive.current =
          cameraScrollCurve.transitionCurveActive.current;

        if (cameraScrollCurve.transitionCurveActive.current) {
          pandaScrollCurve.loopCounter.current =
            cameraScrollCurve.loopCounter.current;
          pandaScrollCurve.initiateTransitionCurve();
        } else {
          const direction =
            cameraScrollCurve.loopCounter.current >
            pandaScrollCurve.loopCounter.current
              ? "forward"
              : "backward";

          pandaScrollCurve.shiftCurvePoints(direction);
          pandaScrollCurve.loopCounter.current =
            cameraScrollCurve.loopCounter.current;
        }
      }

      const pandaPoint = pandaScrollCurve.getCurrentPoint(currentProgress);

      randomOffset.time += delta;

      const positionAmplitude = 0.05;
      const rotationAmplitude = 0.02;

      randomOffset.position.x =
        Math.sin(randomOffset.time * 1.8 + 0.5) * positionAmplitude * 0.3;
      randomOffset.position.y =
        Math.sin(randomOffset.time * 1.8 + 1.2) * positionAmplitude * 0.3 - 0.4;
      randomOffset.position.z =
        Math.sin(randomOffset.time * 1.1 + 2.1) * positionAmplitude * 0.2;

      randomOffset.rotation.x =
        Math.sin(randomOffset.time * 2 + 0.8) * rotationAmplitude * 0.2;
      randomOffset.rotation.y =
        Math.sin(randomOffset.time * 0.9 + 1.5) * rotationAmplitude * 0;
      randomOffset.rotation.z =
        Math.sin(randomOffset.time * 0.6 + 2.3) * rotationAmplitude * 0;

      pandaRef.current.position.x = THREE.MathUtils.lerp(
        pandaRef.current.position.x,
        pandaPoint.x + randomOffset.position.x,
        0.1
      );
      pandaRef.current.position.y = THREE.MathUtils.lerp(
        pandaRef.current.position.y,
        pandaPoint.y + randomOffset.position.y,
        0.1
      );
      pandaRef.current.position.z = THREE.MathUtils.lerp(
        pandaRef.current.position.z,
        pandaPoint.z + randomOffset.position.z,
        0.1
      );

      pandaRef.current.rotation.x = Math.PI + randomOffset.rotation.x;
      pandaRef.current.rotation.y = 0 + randomOffset.rotation.y;
      pandaRef.current.rotation.z = Math.PI + randomOffset.rotation.z;
    }
  });

  return (
    <group {...props} dispose={null}>
      <mesh
        ref={pandaRef}
        geometry={nodes.Mr_Panda004.geometry}
        material={currentTextureRef.current}
        position={[-20.664, -5.242, -1.466]}
        rotation={[Math.PI, 0, Math.PI]}
        scale={[1, 1, 1]}
      />
    </group>
  );
}

useGLTF.preload("/models/Panda.glb");
