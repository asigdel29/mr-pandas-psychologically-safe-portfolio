import React, { useRef, useMemo } from "react";
import { useGLTF, useKTX2 } from "@react-three/drei";
import { useKTX2Texture } from "../utils/ktxLoader";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

export default function Model(props) {
  const { nodes, materials } = useGLTF("/models/scene_1.glb");

  const mrsPandaRef = useRef();

  const dragonHead = useRef();
  const dragonLegFrontLeft = useRef();
  const dragonLegBackLeft = useRef();
  const dragonLegFrontRight = useRef();
  const dragonLegBackRight = useRef();

  const waterfall = useRef();
  const waterfallFoam = useRef();

  const grass1 = useRef();
  const grass2 = useRef();
  const grass3 = useRef();
  const grass4 = useRef();
  const grass5 = useRef();
  const grass6 = useRef();
  const grass7 = useRef();
  const grass8 = useRef();
  const grass9 = useRef();
  const grass10 = useRef();
  const grass11 = useRef();

  const introRef = useRef();
  const aboutRef = useRef();
  const introHovered = useRef(false);
  const aboutHovered = useRef(false);
  const introOriginalZ = -2.752;
  const aboutOriginalZ = -2.752;
  const introHoverZ = introOriginalZ + 3;
  const aboutHoverZ = aboutOriginalZ + 3;

  const mrsPandaHovered = useRef(false);
  const mrsPandaOriginalRotY = -0.42;
  const mrsPandaHoverRotY = mrsPandaOriginalRotY - 0.3;

  const lerpFactor = 0.08;

  const waterfallone = useKTX2Texture("/textures/waterfall_one.ktx2");
  const waterfalltwo = useKTX2Texture("/textures/waterfall_two.ktx2");
  const not_waterfall = useKTX2Texture(
    "/textures/not_waterfall.ktx2?v=9",
    true,
    0.6,
    "double"
  );
  const scene_1_bg = useKTX2Texture("/textures/scene_1_bg.ktx2?v=3");
  const scene_1 = useKTX2Texture("/textures/scene_1.ktx2?v=7");
  // The old Chinese dragon is hidden (see the dragon meshes below); a Tibetan
  // prayer-flag garland takes its place across the sky.
  const prayerFlags = useKTX2Texture(
    "/textures/prayer_flags.ktx2?v=3",
    true,
    0.5,
    "double"
  );
  // Himalayan range across the backdrop, behind the scenery.
  const mountains = useKTX2Texture(
    "/textures/mountains.ktx2?v=1",
    true,
    0.5,
    "double"
  );

  useFrame((state) => {
    const t = state.clock.elapsedTime;

    dragonHead.current.rotation.y = 0.2 * Math.sin(t * 0.8);
    dragonLegFrontLeft.current.rotation.y = 0.3 * Math.sin(t + Math.PI);
    dragonLegBackLeft.current.rotation.y = 0.3 * Math.sin(t * 0.9 + Math.PI);
    dragonLegFrontRight.current.rotation.y = 0.2 * Math.sin(t);
    dragonLegBackRight.current.rotation.y = 0.2 * Math.sin(t + Math.PI);

    const useAlt = Math.sin(t * 4) > 0;
    const mat = useAlt ? waterfalltwo : waterfallone;

    if (waterfall.current) {
      waterfall.current.material = mat;
    }

    if (waterfallFoam.current) {
      waterfallFoam.current.material = mat;
    }

    if (introRef.current) {
      const targetZ = introHovered.current ? introHoverZ : introOriginalZ;
      introRef.current.position.z +=
        (targetZ - introRef.current.position.z) * lerpFactor;
    }

    if (grass1.current) {
      grass1.current.scale.z = 0.1 * Math.sin(t * 2.98) + 0.9;
      grass2.current.scale.z = 0.1 * Math.sin(t * 3.12) + 0.9;
      grass3.current.scale.z = 0.1 * Math.sin(t * 2.95) + 0.9;
      grass4.current.scale.z = 0.1 * Math.sin(t * 3.01) + 0.9;
      grass5.current.scale.z = 0.1 * Math.sin(t * 3.02) + 0.9;
      grass6.current.scale.z = 0.1 * Math.sin(t * 3.05) + 0.9;
      grass7.current.scale.z = 0.1 * Math.sin(t * 2.89) + 0.9;
      grass8.current.scale.z = 0.1 * Math.sin(t * 2.99) + 0.9;
      grass9.current.scale.z = 0.1 * Math.sin(t * 3) + 0.9;
      grass10.current.scale.z = 0.1 * Math.sin(t * 2.9) + 0.9;
      grass11.current.scale.z = 0.1 * Math.sin(t * 2.998) + 0.9;
    }

    if (aboutRef.current) {
      const targetZ = aboutHovered.current ? aboutHoverZ : aboutOriginalZ;
      aboutRef.current.position.z +=
        (targetZ - aboutRef.current.position.z) * lerpFactor;
    }

    if (mrsPandaRef.current) {
      const targetRotY = mrsPandaHovered.current
        ? mrsPandaHoverRotY
        : mrsPandaOriginalRotY;
      mrsPandaRef.current.rotation.y +=
        (targetRotY - mrsPandaRef.current.rotation.y) * lerpFactor;
    }
  });

  return (
    <group {...props} dispose={null}>
      {/* Chinese dragon -> hidden, replaced by the prayer-flag garland below */}
      <mesh
        visible={false}
        geometry={nodes.Plane029.geometry}
        material={scene_1}
        position={[-3.042, 3.941, -2.322]}
        rotation={[Math.PI / 2, 0, 0]}
      />
      <mesh
        ref={dragonHead}
        visible={false}
        geometry={nodes.Plane037.geometry}
        material={scene_1}
        position={[-5.243, 4.082, -2.267]}
        rotation={[Math.PI / 2, -0.082, 0]}
      />
      <mesh
        ref={dragonLegFrontLeft}
        visible={false}
        geometry={nodes.Plane089.geometry}
        material={scene_1}
        position={[-3.93, 3.518, -2.266]}
        rotation={[Math.PI / 2, 0.065, 0]}
      />
      <mesh
        ref={dragonLegFrontRight}
        visible={false}
        geometry={nodes.Plane090.geometry}
        material={scene_1}
        position={[-3.974, 3.587, -2.409]}
        rotation={[Math.PI / 2, -0.19, 0]}
      />
      {/* Tibetan prayer-flag garland strung left-to-right across the range.
          scale-y is flipped because KTX2 textures sample inverted on a raw
          planeGeometry. */}
      <mesh
        material={prayerFlags}
        position={[-6, 2.8, -2.5]}
        scale={[1, -1, 1]}
      >
        <planeGeometry args={[12, 1.9]} />
      </mesh>
      <mesh
        ref={mrsPandaRef}
        visible={false}
        geometry={nodes.Plane116.geometry}
        material={scene_1}
        position={[-5.746, 0.854, -2.671]}
        rotation={[-1.501, mrsPandaOriginalRotY, -3.093]}
        onPointerEnter={() => (mrsPandaHovered.current = true)}
        onPointerLeave={() => (mrsPandaHovered.current = false)}
      />
      <mesh
        geometry={nodes.Plane124.geometry}
        material={scene_1}
        position={[-9.272, 0.977, -1.861]}
        rotation={[Math.PI / 2, -0.102, 0]}
      />
      <mesh
        ref={dragonLegBackLeft}
        visible={false}
        geometry={nodes.Plane129.geometry}
        material={scene_1}
        position={[-2.078, 3.564, -2.266]}
        rotation={[Math.PI / 2, 0.272, 0]}
      />
      <mesh
        ref={dragonLegBackRight}
        visible={false}
        geometry={nodes.Plane130.geometry}
        material={scene_1}
        position={[-2.121, 3.596, -2.451]}
        rotation={[Math.PI / 2, 0.781, 0]}
      />
      <mesh
        ref={grass11}
        geometry={nodes.Plane019.geometry}
        material={scene_1}
        position={[-7.18, 0.6, -0.032]}
        rotation={[Math.PI / 2, -0.102, 0]}
      />
      <mesh
        ref={grass10}
        geometry={nodes.Plane021.geometry}
        material={scene_1}
        position={[-8.939, 0.6, -0.632]}
        rotation={[Math.PI / 2, -0.102, 0]}
      />
      <mesh
        ref={grass1}
        geometry={nodes.Plane035.geometry}
        material={scene_1}
        position={[-10.407, 0.6, -0.18]}
        rotation={[Math.PI / 2, -0.102, 0]}
      />
      <mesh
        ref={grass9}
        geometry={nodes.Plane044.geometry}
        material={scene_1}
        position={[-5.758, 0.567, -0.294]}
        rotation={[Math.PI / 2, -0.102, 0]}
      />
      <mesh
        ref={grass8}
        geometry={nodes.Plane051.geometry}
        material={scene_1}
        position={[-16.072, 0.543, -0.242]}
        rotation={[Math.PI / 2, -0.102, 0]}
      />
      <mesh
        ref={grass2}
        geometry={nodes.Plane067.geometry}
        material={scene_1}
        position={[-17.956, 0.6, -0.18]}
        rotation={[Math.PI / 2, -0.102, 0]}
      />
      <mesh
        ref={grass7}
        geometry={nodes.Plane097.geometry}
        material={scene_1}
        position={[-14.164, 0.565, -2.277]}
        rotation={[Math.PI / 2, -0.102, 0]}
      />
      <mesh
        ref={grass3}
        geometry={nodes.Plane098.geometry}
        material={scene_1}
        position={[-18.584, 0.576, -2.295]}
        rotation={[Math.PI / 2, -0.102, 0]}
      />
      <mesh
        geometry={nodes.Plane099.geometry}
        material={scene_1}
        position={[-12.503, 0.574, -2.199]}
        rotation={[Math.PI / 2, -0.102, 0]}
      />
      <mesh
        ref={grass6}
        geometry={nodes.Plane100.geometry}
        material={scene_1}
        position={[-14.476, 0.585, -0.393]}
        rotation={[Math.PI / 2, -0.102, 0]}
      />
      <mesh
        ref={grass5}
        geometry={nodes.Plane101.geometry}
        material={scene_1}
        position={[-16.49, 0.655, -1.962]}
        rotation={[Math.PI / 2, -0.102, 0]}
      />
      <mesh
        ref={grass4}
        geometry={nodes.Plane102.geometry}
        material={scene_1}
        position={[-5.192, 0.585, -0.816]}
        rotation={[Math.PI / 2, -0.102, 0]}
      />
      {/* Himalayan backdrop range, behind the scenery. scale-y flipped (KTX2
          samples inverted on a raw planeGeometry). */}
      <mesh
        material={mountains}
        position={[-7, 1.1, -2.71]}
        scale={[1, -1, 1]}
        renderOrder={-1}
      >
        <planeGeometry args={[20, 5]} />
      </mesh>
      <mesh
        geometry={nodes["First_Scene_-_Bg"].geometry}
        material={scene_1_bg}
        position={[-21.188, 0.605, -0.262]}
      />
      <mesh
        geometry={nodes["First_Scene_-_Bg001"].geometry}
        material={scene_1_bg}
        position={[-21.188, 0.605, -0.262]}
      />
      <mesh
        geometry={nodes.not_waterfall.geometry}
        material={not_waterfall}
        position={[-7.867, 2.012, -2.444]}
        rotation={[Math.PI / 2, 0.025, 0]}
      />
      <mesh
        ref={introRef}
        geometry={nodes.intro.geometry}
        material={not_waterfall}
        position={[-17.941, 2.096, introOriginalZ]}
        rotation={[Math.PI / 2, 0.025, 0]}
        onPointerEnter={() => (introHovered.current = true)}
        onPointerLeave={() => (introHovered.current = false)}
      />
      <mesh
        ref={aboutRef}
        geometry={nodes.about.geometry}
        material={not_waterfall}
        position={[-15.7, 1.987, aboutOriginalZ]}
        rotation={[Math.PI / 2, 0.025, 0]}
        onPointerEnter={() => (aboutHovered.current = true)}
        onPointerLeave={() => (aboutHovered.current = false)}
      />
      <mesh
        ref={waterfall}
        geometry={nodes.Waterfall001.geometry}
        material={waterfallone}
        position={[-10.609, 1.507, -2.46]}
        rotation={[-Math.PI / 2, 0, -Math.PI]}
      />
      <mesh
        ref={waterfallFoam}
        geometry={nodes.Waterfall_Foam001.geometry}
        material={waterfallone}
        position={[-10.711, 0.873, -2.351]}
        rotation={[-Math.PI / 2, 0.134, -Math.PI]}
      />
    </group>
  );
}

useGLTF.preload("/models/scene_1.glb");
