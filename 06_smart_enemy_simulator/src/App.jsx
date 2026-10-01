import { useEffect, useRef, useState } from "react";

const SAVE_KEY = "temple-enemy-sim";
const W = 800;
const H = 520;

const startState = () => ({
  player: { x: 400, y: 260, hp: 100, potions: 2, facing: 1 },
  enemies: [
    { id: 1, x: 160, y: 140, homeX: 160, homeY: 140, hp: 40, state: "patrol", dir: 1 },
    { id: 2, x: 640, y: 180, homeX: 640, homeY: 180, hp: 40, state: "patrol", dir: -1 },
    { id: 3, x: 500, y: 400, homeX: 500, homeY: 400, hp: 50, state: "patrol", dir: 1 },
  ],
  score: 0,
  message: "Patrol, chase, attack. Stay sharp.",
});

function loadState() {
  try {
    const raw = localStorage.getItem(SAVE_KEY);
    return raw ? JSON.parse(raw) : startState();
  } catch {
    return startState();
  }
}

export default function App() {
  const [snap, setSnap] = useState(loadState);
  const keys = useRef(new Set());
  const attack = useRef(false);

  useEffect(() => {
    const down = (e) => {
      keys.current.add(e.key.toLowerCase());
      if (e.key === " ") attack.current = true;
      if (e.key.toLowerCase() === "h") {
        setSnap((s) => {
          if (s.player.potions <= 0 || s.player.hp >= 100) return { ...s, message: "No potion to use." };
          return { ...s, player: { ...s.player, hp: Math.min(100, s.player.hp + 30), potions: s.player.potions - 1 }, message: "Potion used. +30 HP." };
        });
      }
    };
    const up = (e) => keys.current.delete(e.key.toLowerCase());
    window.addEventListener("keydown", down);
    window.addEventListener("keyup", up);
    return () => {
      window.removeEventListener("keydown", down);
      window.removeEventListener("keyup", up);
    };
  }, []);

  useEffect(() => {
    const id = setInterval(() => {
      setSnap((s) => {
        if (s.player.hp <= 0) return s;
        const p = { ...s.player };
        const speed = 4;
        if (keys.current.has("a") || keys.current.has("arrowleft")) { p.x -= speed; p.facing = -1; }
        if (keys.current.has("d") || keys.current.has("arrowright")) { p.x += speed; p.facing = 1; }
        if (keys.current.has("w") || keys.current.has("arrowup")) p.y -= speed;
        if (keys.current.has("s") || keys.current.has("arrowdown")) p.y += speed;
        p.x = Math.max(20, Math.min(W - 20, p.x));
        p.y = Math.max(20, Math.min(H - 20, p.y));

        let score = s.score;
        let message = s.message;
        const enemies = s.enemies.map((e) => {
          if (e.hp <= 0) return e;
          const next = { ...e };
          const dist = Math.hypot(p.x - e.x, p.y - e.y);
          if (dist < 36) next.state = "attack";
          else if (dist < 140) next.state = "chase";
          else next.state = "patrol";

          if (next.state === "patrol") {
            next.x += next.dir * 1.4;
            if (Math.abs(next.x - next.homeX) > 70) next.dir *= -1;
          } else if (next.state === "chase") {
            next.x += Math.sign(p.x - e.x) * 2.1;
            next.y += Math.sign(p.y - e.y) * 2.1;
          } else if (next.state === "attack") {
            p.hp = Math.max(0, p.hp - 0.6);
            message = "An enemy is too close.";
          }

          if (attack.current && dist < 56 && Math.sign(e.x - p.x || p.facing) === p.facing) {
            next.hp = Math.max(0, next.hp - 12);
            score += next.hp === 0 ? 25 : 1;
            message = next.hp === 0 ? "Enemy cleared." : "Hit landed.";
          }
          return next;
        });
        attack.current = false;
        if (p.hp <= 0) message = "You need a rest. Load the save or reset.";
        return { ...s, player: p, enemies, score, message };
      });
    }, 40);
    return () => clearInterval(id);
  }, []);

  const save = () => {
    localStorage.setItem(SAVE_KEY, JSON.stringify(snap));
    setSnap((s) => ({ ...s, message: "Saved to localStorage." }));
  };
  const load = () => setSnap({ ...loadState(), message: "Save loaded." });
  const reset = () => {
    localStorage.removeItem(SAVE_KEY);
    setSnap(startState());
  };

  return (
    <div style={{ fontFamily: "Arial, sans-serif", background: "#10161c", color: "#eef5ff", minHeight: "100vh", padding: 20 }}>
      <h1 style={{ marginTop: 0 }}>Smart Enemy Simulator</h1>
      <p>WASD move · Space attack · H potion · enemies patrol, chase, then attack.</p>
      <p>HP {Math.round(snap.player.hp)} · Potions {snap.player.potions} · Score {snap.score} · {snap.message}</p>
      <button onClick={save}>Save</button> <button onClick={load}>Load</button> <button onClick={reset}>Reset</button>
      <svg viewBox={`0 0 ${W} ${H}`} width="100%" style={{ maxWidth: 800, background: "#243226", borderRadius: 12, marginTop: 12 }}>
        <rect x="330" y="180" width="140" height="90" fill="#6d5a42" />
        <circle cx={snap.player.x} cy={snap.player.y} r="14" fill="#7ec8ff" />
        {snap.enemies.filter((e) => e.hp > 0).map((e) => (
          <g key={e.id}>
            <circle cx={e.x} cy={e.y} r="12" fill={e.state === "attack" ? "#e25b4a" : e.state === "chase" ? "#e0a15a" : "#c9d46a"} />
            <text x={e.x - 18} y={e.y - 16} fontSize="11" fill="#fff">{e.state}</text>
          </g>
        ))}
      </svg>
    </div>
  );
}
