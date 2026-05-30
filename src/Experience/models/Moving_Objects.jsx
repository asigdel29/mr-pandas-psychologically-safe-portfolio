import React, { useRef, useState } from "react";
import { useGLTF } from "@react-three/drei";
import { useKTX2Texture } from "../utils/ktxLoader";
import { useFrame } from "@react-three/fiber";

import * as THREE from "three";

export default function Model({ scrollProgress, ...props }) {
  const { nodes, materials } = useGLTF("/models/Moving_Extras.glb");

  const material = useKTX2Texture("/textures/Moving_extras.ktx2?v=2");
  const dirtMaterial = useKTX2Texture("/textures/dirt.ktx2");
  const camelGroupRef = useRef();
  const camelFrontRightRef = useRef();
  const camelBackRightRef = useRef();
  const camelFrontLeftRef = useRef();
  const camelBackLeftRef = useRef();
  const bikeGroupRef = useRef();
  const frontWheelRef = useRef();
  const backWheelRef = useRef();
  const bikePedalHolderRef = useRef();
  const gearRef = useRef();
  const bikePedalRef = useRef();
  const shipGroupRef = useRef();
  const skeletonGroupRef = useRef();
  const planeRef = useRef();
  const dirtParticleRef = useRef();

  const [prevScrollProgress] = useState(() => ({ value: 0 }));

  const [randomOffsets] = useState(() => ({
    camel: {
      position: new THREE.Vector3(),
      rotation: new THREE.Euler(),
      time: 0,
      basePosition: new THREE.Vector3(0, 0, 0),
    },
    bike: {
      position: new THREE.Vector3(),
      rotation: new THREE.Euler(),
      time: Math.PI * 0.3,
      basePosition: new THREE.Vector3(0, 0.15, 0),
    },
    ship: {
      position: new THREE.Vector3(),
      rotation: new THREE.Euler(),
      time: Math.PI * 0.7,
      basePosition: new THREE.Vector3(0, 0, -0.2),
    },
    skeleton: {
      position: new THREE.Vector3(),
      rotation: new THREE.Euler(),
      time: Math.PI * 1.2,
      basePosition: new THREE.Vector3(0, 0, -0.2),
    },
  }));

  useFrame((state, delta) => {
    const t = state.clock.elapsedTime;

    planeRef.current.position.y = 0.2 * Math.sin(t * 0.4) + 8.3;
    planeRef.current.rotation.y = 0.02 * Math.sin(t * 0.4);

    randomOffsets.camel.time += delta;
    randomOffsets.bike.time += delta;
    randomOffsets.ship.time += delta;
    randomOffsets.skeleton.time += delta;

    const camelPosAmp = 0.04;
    const camelRotAmp = 0.015;
    randomOffsets.camel.position.x =
      Math.sin(randomOffsets.camel.time * 1.1 + 0.3) * camelPosAmp;
    randomOffsets.camel.position.y =
      Math.sin(randomOffsets.camel.time * 1.4 + 1.1) * camelPosAmp * 1.5;
    randomOffsets.camel.position.z =
      Math.sin(randomOffsets.camel.time * 0.9 + 2.2) * camelPosAmp * 0.3;
    randomOffsets.camel.rotation.x =
      Math.sin(randomOffsets.camel.time * 0.8 + 0.7) * camelRotAmp * 0.1;
    randomOffsets.camel.rotation.y =
      Math.sin(randomOffsets.camel.time * 1.0 + 1.3) * camelRotAmp * 0.1;
    randomOffsets.camel.rotation.z =
      Math.sin(randomOffsets.camel.time * 0.7 + 2.1) * camelRotAmp * 0.1;

    const bikePosAmp = 0.02;
    const bikeRotAmp = 0.01;
    randomOffsets.bike.position.x =
      Math.sin(randomOffsets.bike.time * 2.1 + 0.8) * bikePosAmp * 0.3;
    randomOffsets.bike.position.y =
      Math.sin(randomOffsets.bike.time * 2.3 + 1.5) * bikePosAmp * 0.8;
    randomOffsets.bike.position.z =
      Math.sin(randomOffsets.bike.time * 1.8 + 2.7) * bikePosAmp * 0.1;
    randomOffsets.bike.rotation.x =
      Math.sin(randomOffsets.bike.time * 1.9 + 0.4) * bikeRotAmp * 0.1;
    randomOffsets.bike.rotation.y =
      Math.sin(randomOffsets.bike.time * 1.7 + 1.8) * bikeRotAmp * 0.3;
    randomOffsets.bike.rotation.z =
      Math.sin(randomOffsets.bike.time * 1.5 + 2.9) * bikeRotAmp * 0.1;

    const shipPosAmp = 0.04;
    const shipRotAmp = 0.025;
    randomOffsets.ship.position.x =
      Math.sin(randomOffsets.ship.time * 0.6 + 1.2) * shipPosAmp * 0.6;
    randomOffsets.ship.position.y =
      Math.sin(randomOffsets.ship.time * 0.8 + 0.9) * shipPosAmp * 0.2;
    randomOffsets.ship.position.z =
      Math.sin(randomOffsets.ship.time * 0.5 + 1.8) * shipPosAmp * 0.1;
    randomOffsets.ship.rotation.x =
      Math.sin(randomOffsets.ship.time * 0.7 + 1.1) * shipRotAmp * 0.1;
    randomOffsets.ship.rotation.y =
      Math.sin(randomOffsets.ship.time * 0.4 + 2.3) * shipRotAmp * 0.2;
    randomOffsets.ship.rotation.z =
      Math.sin(randomOffsets.ship.time * 0.6 + 0.6) * shipRotAmp * 0;

    const skeletonPosAmp = 0.05;
    const skeletonRotAmp = 0.02;
    randomOffsets.skeleton.position.x =
      Math.sin(randomOffsets.skeleton.time * 0.9 + 2.1) * skeletonPosAmp * 0.2;
    randomOffsets.skeleton.position.y =
      Math.sin(randomOffsets.skeleton.time * 1.2 + 0.4) * skeletonPosAmp * 0.3;
    randomOffsets.skeleton.position.z =
      Math.sin(randomOffsets.skeleton.time * 0.7 + 1.6) * skeletonPosAmp * 0.1;
    randomOffsets.skeleton.rotation.x =
      Math.sin(randomOffsets.skeleton.time * 0.8 + 1.9) * skeletonRotAmp * 0.1;
    randomOffsets.skeleton.rotation.y =
      Math.sin(randomOffsets.skeleton.time * 1.1 + 0.2) * skeletonRotAmp * 0.1;
    randomOffsets.skeleton.rotation.z =
      Math.sin(randomOffsets.skeleton.time * 0.9 + 2.8) * skeletonRotAmp * 0.1;

    if (
      scrollProgress.current >= 0 &&
      scrollProgress.current <= 0.3 &&
      bikeGroupRef.current
    ) {
      const normalizedProgress = scrollProgress.current / 0.3;
      const targetX = normalizedProgress * 16.89;

      randomOffsets.bike.basePosition.x = THREE.MathUtils.lerp(
        randomOffsets.bike.basePosition.x,
        targetX,
        0.1
      );

      const wheelTargetRotation = normalizedProgress * Math.PI * -16;

      if (frontWheelRef.current) {
        frontWheelRef.current.rotation.y = THREE.MathUtils.lerp(
          frontWheelRef.current.rotation.y,
          wheelTargetRotation,
          0.1
        );
      }

      if (backWheelRef.current) {
        backWheelRef.current.rotation.y = THREE.MathUtils.lerp(
          backWheelRef.current.rotation.y,
          wheelTargetRotation,
          0.1
        );
      }

      const bikePedalTargetRotation = normalizedProgress * Math.PI * 16 * 2;

      if (bikePedalHolderRef.current) {
        bikePedalHolderRef.current.rotation.y = THREE.MathUtils.lerp(
          bikePedalHolderRef.current.rotation.y,
          bikePedalTargetRotation,
          0.1
        );
      }

      if (bikePedalRef.current) {
        bikePedalRef.current.rotation.y = THREE.MathUtils.lerp(
          bikePedalRef.current.rotation.y,
          -bikePedalTargetRotation / 2,
          0.1
        );
      }

      if (gearRef.current) {
        gearRef.current.rotation.y = THREE.MathUtils.lerp(
          gearRef.current.rotation.y,
          bikePedalTargetRotation,
          0.1
        );
      }

      // Dirt Particle Stuff
      const currentBikeX = randomOffsets.bike.basePosition.x;
      const velocity = Math.abs(targetX - currentBikeX);

      const scrollingBackward =
        scrollProgress.current < prevScrollProgress.value;

      const targetScale = scrollingBackward ? 0 : Math.min(velocity * 10, 2);

      if (dirtParticleRef.current) {
        const currentScale = dirtParticleRef.current.scale.x;
        const newScale = THREE.MathUtils.lerp(currentScale, targetScale, 0.1);
        dirtParticleRef.current.scale.set(newScale, newScale, newScale);
      }

      prevScrollProgress.value = scrollProgress.current;
    }

    if (scrollProgress.current < 0 || scrollProgress.current > 0.3) {
      if (dirtParticleRef.current) {
        const currentScale = dirtParticleRef.current.scale.x;
        const newScale = THREE.MathUtils.lerp(currentScale, 0, 0.1);
        dirtParticleRef.current.scale.set(newScale, newScale, newScale);
      }
    }

    if (
      scrollProgress.current >= 0.31 &&
      scrollProgress.current <= 0.49 &&
      shipGroupRef.current
    ) {
      const normalizedProgress =
        (scrollProgress.current - 0.31) / (0.49 - 0.31);

      const targetX = normalizedProgress * 10;
      const targetY = normalizedProgress * 1.5;

      randomOffsets.ship.basePosition.x = THREE.MathUtils.lerp(
        randomOffsets.ship.basePosition.x,
        targetX,
        0.1
      );
      randomOffsets.ship.basePosition.y = THREE.MathUtils.lerp(
        randomOffsets.ship.basePosition.y,
        targetY,
        0.1
      );
    }

    if (
      scrollProgress.current >= 0.508 &&
      scrollProgress.current <= 0.6 &&
      camelGroupRef.current
    ) {
      const normalizedProgress =
        (scrollProgress.current - 0.508) / (0.6 - 0.508);

      const targetX = normalizedProgress * 6.5;
      randomOffsets.camel.basePosition.x = THREE.MathUtils.lerp(
        randomOffsets.camel.basePosition.x,
        targetX,
        0.1
      );

      const oscillationFrequency = 3;
      const maxRotation = THREE.MathUtils.degToRad(35);

      const rightLegOscillation =
        Math.sin(normalizedProgress * Math.PI * 2 * oscillationFrequency) *
        maxRotation;
      const leftLegOscillation =
        Math.sin(
          normalizedProgress * Math.PI * 2 * oscillationFrequency + Math.PI
        ) * maxRotation;

      if (camelFrontRightRef.current) {
        const targetRotation = rightLegOscillation;
        camelFrontRightRef.current.rotation.y = THREE.MathUtils.lerp(
          camelFrontRightRef.current.rotation.y,
          targetRotation,
          0.1
        );
      }

      if (camelBackRightRef.current) {
        const targetRotation = rightLegOscillation;
        camelBackRightRef.current.rotation.y = THREE.MathUtils.lerp(
          camelBackRightRef.current.rotation.y,
          targetRotation,
          0.1
        );
      }

      if (camelFrontLeftRef.current) {
        const targetRotation = leftLegOscillation;
        camelFrontLeftRef.current.rotation.y = THREE.MathUtils.lerp(
          camelFrontLeftRef.current.rotation.y,
          targetRotation,
          0.1
        );
      }

      if (camelBackLeftRef.current) {
        const targetRotation = leftLegOscillation;
        camelBackLeftRef.current.rotation.y = THREE.MathUtils.lerp(
          camelBackLeftRef.current.rotation.y,
          targetRotation,
          0.1
        );
      }
    }

    if (
      scrollProgress.current >= 0.609 &&
      scrollProgress.current <= 0.69 &&
      skeletonGroupRef.current
    ) {
      const normalizedProgress =
        (scrollProgress.current - 0.609) / (0.69 - 0.609);

      const targetX = normalizedProgress * 6.3;
      randomOffsets.skeleton.basePosition.x = THREE.MathUtils.lerp(
        randomOffsets.skeleton.basePosition.x,
        targetX,
        0.1
      );
    }

    if (camelGroupRef.current) {
      camelGroupRef.current.position.set(
        randomOffsets.camel.basePosition.x + randomOffsets.camel.position.x,
        randomOffsets.camel.basePosition.y + randomOffsets.camel.position.y,
        randomOffsets.camel.basePosition.z + randomOffsets.camel.position.z
      );
      camelGroupRef.current.rotation.x = randomOffsets.camel.rotation.x;
      camelGroupRef.current.rotation.y = randomOffsets.camel.rotation.y;
      camelGroupRef.current.rotation.z = randomOffsets.camel.rotation.z;
    }

    if (bikeGroupRef.current) {
      bikeGroupRef.current.position.set(
        randomOffsets.bike.basePosition.x + randomOffsets.bike.position.x,
        randomOffsets.bike.basePosition.y + randomOffsets.bike.position.y,
        randomOffsets.bike.basePosition.z + randomOffsets.bike.position.z - 0.05
      );
      bikeGroupRef.current.rotation.x = randomOffsets.bike.rotation.x;
      bikeGroupRef.current.rotation.y = randomOffsets.bike.rotation.y;
      bikeGroupRef.current.rotation.z = randomOffsets.bike.rotation.z;
    }

    if (shipGroupRef.current) {
      shipGroupRef.current.position.set(
        randomOffsets.ship.basePosition.x + randomOffsets.ship.position.x,
        randomOffsets.ship.basePosition.y + randomOffsets.ship.position.y,
        randomOffsets.ship.basePosition.z + randomOffsets.ship.position.z
      );
      shipGroupRef.current.rotation.x = randomOffsets.ship.rotation.x;
      shipGroupRef.current.rotation.y = randomOffsets.ship.rotation.y;
      shipGroupRef.current.rotation.z = randomOffsets.ship.rotation.z;
    }

    if (skeletonGroupRef.current) {
      skeletonGroupRef.current.position.set(
        randomOffsets.skeleton.basePosition.x +
          randomOffsets.skeleton.position.x,
        randomOffsets.skeleton.basePosition.y +
          randomOffsets.skeleton.position.y,
        randomOffsets.skeleton.basePosition.z +
          randomOffsets.skeleton.position.z
      );
      skeletonGroupRef.current.rotation.x = randomOffsets.skeleton.rotation.x;
      skeletonGroupRef.current.rotation.y = randomOffsets.skeleton.rotation.y;
      skeletonGroupRef.current.rotation.z = randomOffsets.skeleton.rotation.z;
    }
  });

  return (
    <group {...props} dispose={null}>
      <group ref={camelGroupRef}>
        <mesh
          geometry={nodes.Camel_Stick.geometry}
          material={material}
          position={[8.138, 1.997, -1.48]}
          rotation={[Math.PI, 0, Math.PI]}
          scale={[1.523, 1, 1.523]}
        />
        <mesh
          geometry={nodes.Camel_Body.geometry}
          material={material}
          position={[8.226, 2.754, -1.394]}
          rotation={[Math.PI / 2, 0.013, 0]}
          scale={0.849}
        />
        <mesh
          ref={camelFrontRightRef}
          geometry={nodes.front_right_camel.geometry}
          material={material}
          position={[8.434, 2.572, -1.392]}
          rotation={[Math.PI / 2, -0.054, 0]}
        />
        <mesh
          ref={camelBackRightRef}
          geometry={nodes.back_right_camel.geometry}
          material={material}
          position={[7.97, 2.547, -1.392]}
          rotation={[Math.PI / 2, -0.054, 0]}
        />
        <mesh
          ref={camelFrontLeftRef}
          geometry={nodes.front_left_camel.geometry}
          material={material}
          position={[8.392, 2.703, -1.426]}
          rotation={[Math.PI / 2, -0.054, 0]}
        />
        <mesh
          ref={camelBackLeftRef}
          geometry={nodes.back_left_camel.geometry}
          material={material}
          position={[7.97, 2.609, -1.426]}
          rotation={[Math.PI / 2, -0.054, 0]}
        />
      </group>

      <group ref={bikeGroupRef} position={[0, 0, -0.2]}>
        <group
          ref={bikePedalHolderRef}
          position={[-20.535, 0.616, -1.381]}
          rotation={[-Math.PI / 2, 0, -Math.PI]}
        >
          <mesh
            geometry={nodes.Bike_Pedal_Holder.geometry}
            material={material}
          />
          <mesh
            ref={bikePedalRef}
            geometry={nodes.Bike_Pedal.geometry}
            material={material}
            position={[-0.138, 0.002, 0.005]}
            rotation={[0, 0, 0]}
          />
        </group>
        <mesh
          geometry={nodes.Bike_Stick.geometry}
          material={material}
          position={[-20.497, 0.378, -1.48]}
          rotation={[Math.PI, 0, Math.PI]}
          scale={[1.523, 1, 1.523]}
        />
        <mesh
          geometry={nodes.Bike_Body.geometry}
          material={material}
          position={[-20.607, 0.901, -1.391]}
          rotation={[-Math.PI / 2, 0, -Math.PI]}
        />
        <mesh
          ref={backWheelRef}
          geometry={nodes.Bike_Bake_Wheel.geometry}
          material={material}
          position={[-20.918, 0.666, -1.392]}
          rotation={[Math.PI / 2, -0.242, 0]}
        />
        <mesh
          ref={frontWheelRef}
          geometry={nodes.Bike_Front_Wheel.geometry}
          material={material}
          position={[-19.978, 0.664, -1.395]}
          rotation={[Math.PI / 2, -0.242, 0]}
        />
        <mesh
          ref={gearRef}
          geometry={nodes.Plane107.geometry}
          material={material}
          position={[-20.537, 0.615, -1.385]}
          rotation={[-Math.PI / 2, 0, -Math.PI]}
        />
        <mesh
          ref={dirtParticleRef}
          scale={[0, 0, 0]}
          geometry={nodes.dirt_particle.geometry}
          material={dirtMaterial}
          position={[-21.136, 0.514, -1.38]}
          rotation={[-Math.PI / 2, 0, -Math.PI]}
        />
      </group>

      <mesh
        ref={planeRef}
        geometry={nodes.Actual_Plane.geometry}
        material={material}
        position={[-20.812, 8.181, -1.406]}
        rotation={[Math.PI / 2, -0.029, 0]}
      />
      <group position={[-0.2, 0, 0]} ref={skeletonGroupRef}>
        <mesh
          geometry={nodes.Skeleton_Stick.geometry}
          material={material}
          position={[15.013, 1.303, -1.34]}
          rotation={[Math.PI, 0, Math.PI]}
          scale={[1.523, 1, 1.523]}
        />
      </group>

      <group position={[-0.2, 0, 0.2]} ref={shipGroupRef}>
        <mesh
          geometry={nodes.Ship_Stick.geometry}
          material={material}
          position={[-2.512, 0.41, -1.34]}
          rotation={[Math.PI, 0, Math.PI]}
          scale={[1.523, 1, 1.523]}
        />
      </group>
    </group>
  );
}

useGLTF.preload("/models/Moving_Extras.glb");
