<template>
  <div id="mesh">
    <nav class="navbar">
      <div class="brand">
        <span class="logo">🕸️</span>
        <span class="brand-name">Mesh Capital</span>
        <span class="brand-sub">One Liquidity Layer · Solana</span>
      </div>
      <div class="nav-links">
        <router-link to="/">Route</router-link>
        <router-link to="/perps">Perps</router-link>
        <router-link to="/vaults">Vaults</router-link>
      </div>
      <div class="status">
        <span class="dot" :class="online ? 'ok' : 'err'"></span>
        <span>{{ online ? "Mesh live" : "Offline" }}</span>
      </div>
    </nav>
    <main class="main"><router-view /></main>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
const online = ref(false);
onMounted(async () => {
  try { await axios.get("/health"); online.value = true; } catch { online.value = false; }
});
</script>

<style>
:root {
  --bg: #070a0e;
  --surface: #0e131a;
  --border: #18212c;
  --accent: #2dd4bf;
  --accent2: #818cf8;
  --good: #34d399;
  --bad: #f43f5e;
  --text: #e6edf3;
  --muted: #4b586a;
  --font: "JetBrains Mono", "Cascadia Code", monospace;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: var(--bg); color: var(--text); font-family: var(--font); font-size: 13px; line-height: 1.6; }
#mesh { min-height: 100vh; display: flex; flex-direction: column; }
.navbar { display: flex; align-items: center; gap: 24px; padding: 12px 24px; background: var(--surface); border-bottom: 1px solid var(--border); position: sticky; top: 0; z-index: 100; }
.brand { display: flex; align-items: center; gap: 8px; }
.logo { font-size: 16px; }
.brand-name { font-size: 16px; font-weight: 700; color: var(--accent); }
.brand-sub { font-size: 11px; color: var(--muted); border-left: 1px solid var(--border); padding-left: 10px; }
.nav-links { display: flex; gap: 16px; margin-left: auto; }
.nav-links a { color: var(--muted); text-decoration: none; font-size: 12px; transition: color 0.2s; }
.nav-links a:hover, .nav-links a.router-link-active { color: var(--accent); }
.status { display: flex; align-items: center; gap: 6px; font-size: 11px; color: var(--muted); }
.dot { width: 7px; height: 7px; border-radius: 50%; }
.dot.ok { background: var(--good); } .dot.err { background: var(--bad); }
.main { flex: 1; padding: 24px; max-width: 1400px; width: 100%; margin: 0 auto; }
</style>
