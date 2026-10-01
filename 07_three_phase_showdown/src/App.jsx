import { useEffect, useRef, useState } from "react";
import * as THREE from "three";

const MAX_HP = 300;

function phaseFor(hp) {
  const pct = hp / MAX_HP;
  if (pct > 0.66) return 1;
  if (pct > 0.33) return 2;
  return 3;
}

export default function App() {
  const mount = useRef(null);
  const [report, setReport] = useState(null);
  const [hud, setHud] = useState({ hp: MAX_HP, phase: 1, combo: 0, player: 100 });

  useEffect(() => {
    const root = mount.current;
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x101820);
    const camera = new THREE.PerspectiveCamera(70, root.clientWidth / 420, 0.1, 100);
    camera.position.set(0, 6, 10);
    camera.lookAt(0, 0, 0);
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(root.clientWidth, 420);
    root.appendChild(renderer.domElement);

    scene.add(new THREE.HemisphereLight(0xb7d4ff, 0x223022, 0.8));
    const sun = new THREE.DirectionalLight(0xfff0d0, 1);
    sun.position.set(4, 8, 2);
    scene.add(sun);

    const floor = new THREE.Mesh(
      new THREE.CircleGeometry(8, 40),
      new THREE.MeshStandardMaterial({ color: 0x3d4a38 })
    );
    floor.rotation.x = -Math.PI / 2;
    scene.add(floor);

    const boss = {
      hp: MAX_HP,
      phase: 1,
      mesh: new THREE.Mesh(
        new THREE.BoxGeometry(1.6, 2.4, 1.6),
        new THREE.MeshStandardMaterial({ color: 0x4aa3ff })
      ),
    };
    boss.mesh.position.y = 1.2;
    scene.add(boss.mesh);

    const player = { x: 0, z: 4.5, hp: 100, combo: 0, mesh: new THREE.Mesh(new THREE.SphereGeometry(0.35), new THREE.MeshStandardMaterial({ color: 0xffe08a })) };
    player.mesh.position.set(player.x, 0.35, player.z);
    scene.add(player.mesh);

    const keys = new Set();
    const onDown = (e) => keys.add(e.key.toLowerCase());
    const onUp = (e) => keys.delete(e.key.toLowerCase());
    window.addEventListener("keydown", onDown);
    window.addEventListener("keyup", onUp);

    let raf;
    let finished = false;
    const loop = () => {
      if (keys.has("a")) player.x -= 0.06;
      if (keys.has("d")) player.x += 0.06;
      if (keys.has("w")) player.z -= 0.06;
      if (keys.has("s")) player.z += 0.06;
      player.x = Math.max(-6, Math.min(6, player.x));
      player.z = Math.max(-6, Math.min(6, player.z));
      player.mesh.position.set(player.x, 0.35, player.z);

      boss.phase = phaseFor(boss.hp);
      boss.mesh.rotation.y += 0.01 * boss.phase;
      const colors = [0x4aa3ff, 0xf0b429, 0xe15b4a];
      boss.mesh.material.color.setHex(colors[boss.phase - 1]);
      if (boss.hp > 0 && player.hp > 0) {
        const dx = player.x - boss.mesh.position.x;
        const dz = player.z - boss.mesh.position.z;
        boss.mesh.position.x += Math.sign(dx) * 0.01 * boss.phase;
        boss.mesh.position.z += Math.sign(dz) * 0.01 * boss.phase;
        if (Math.hypot(dx, dz) < 1.4) player.hp = Math.max(0, player.hp - 0.08 * boss.phase);
      }
      setHud({ hp: Math.round(boss.hp), phase: boss.phase, combo: player.combo, player: Math.round(player.hp) });
      if (!finished && (boss.hp <= 0 || player.hp <= 0)) {
        finished = true;
        setReport({
          result: boss.hp <= 0 ? "Victory" : "Try again",
          bossHpLeft: Math.max(0, Math.round(boss.hp)),
          playerHpLeft: Math.round(player.hp),
          combo: player.combo,
          phaseReached: boss.phase,
        });
      }
      renderer.render(scene, camera);
      raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);

    const strike = (e) => {
      if (e.key.toLowerCase() !== " ") return;
      const dist = Math.hypot(player.x - boss.mesh.position.x, player.z - boss.mesh.position.z);
      if (dist < 2.2 && boss.hp > 0) {
        player.combo = Math.min(3, player.combo + 1);
        boss.hp = Math.max(0, boss.hp - 12 * player.combo);
      } else {
        player.combo = 0;
      }
    };
    window.addEventListener("keydown", strike);

    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("keydown", onDown);
      window.removeEventListener("keyup", onUp);
      window.removeEventListener("keydown", strike);
      renderer.dispose();
      root.removeChild(renderer.domElement);
    };
  }, []);

  return (
    <div style={{ fontFamily: "Arial, sans-serif", background: "#0e141b", color: "white", minHeight: "100vh", padding: 20 }}>
      <h1>Three-Phase Showdown</h1>
      <p>WASD moves. Space is a combo attack. Boss phase changes at 66% and 33% health.</p>
      <p>Boss HP {hud.hp} · Phase {hud.phase} · Combo x{hud.combo} · Your HP {hud.player}</p>
      <div ref={mount} />
      {report && (
        <section>
          <h2>Victory report</h2>
          <pre>{JSON.stringify(report, null, 2)}</pre>
        </section>
      )}
    </div>
  );
}
