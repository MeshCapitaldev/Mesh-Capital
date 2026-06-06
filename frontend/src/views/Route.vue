<template>
  <div class="route-view">
    <div class="page-header">
      <div>
        <h1>Smart Route</h1>
        <p class="sub">One order, split across the mesh for the best blended price.</p>
      </div>
    </div>

    <div class="run-panel">
      <select v-model="market" class="inp">
        <option v-for="m in markets" :key="m" :value="m">{{ m }}</option>
      </select>
      <select v-model="side" class="inp">
        <option value="buy">Buy</option><option value="sell">Sell</option>
      </select>
      <input v-model="size" class="inp" placeholder="Size (base units)" />
      <button class="btn btn-accent" @click="run" :disabled="loading">{{ loading ? "Routing..." : "Route" }}</button>
    </div>

    <div v-if="r" class="result">
      <div class="summary">
        <div class="s"><span class="sl">Blended price</span><span class="sv accent">{{ r.blended_price.toFixed(4) }}</span></div>
        <div class="s"><span class="sl">Price impact</span><span class="sv">{{ r.price_impact_pct.toFixed(2) }}%</span></div>
        <div class="s"><span class="sl">Savings vs best single</span><span class="sv good">{{ r.savings_vs_best_single_pct.toFixed(2) }}%</span></div>
        <div class="s"><span class="sl">Venues used</span><span class="sv">{{ r.route.length }}</span></div>
      </div>

      <div class="split-block">
        <div class="sb-title">Order split across the mesh</div>
        <div class="split-bar">
          <div v-for="(leg, i) in r.route" :key="leg.venue" class="seg" :style="{ width: (leg.fraction*100)+'%', background: color(i) }">
            <span v-if="leg.fraction > 0.08">{{ leg.venue }}</span>
          </div>
        </div>
        <div v-for="(leg, i) in r.route" :key="'r'+leg.venue" class="leg-row">
          <span class="dot-c" :style="{ background: color(i) }"></span>
          <span class="lv-name">{{ leg.venue }}</span>
          <span class="lv-frac">{{ (leg.fraction*100).toFixed(0) }}%</span>
          <span class="lv-price muted">@ {{ leg.price.toFixed(4) }}</span>
          <span class="lv-amt">{{ fmt(leg.base_amount) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { routeQuote } from "@/api/index.js";

const markets = ["SOL-USDC", "BTC-USDC", "ETH-USDC", "WIF-USDC", "JUP-USDC", "JTO-USDC"];
const market = ref("SOL-USDC"), side = ref("buy"), size = ref("10000");
const loading = ref(false), r = ref(null);
const palette = ["#2dd4bf", "#818cf8", "#34d399", "#fbbf24", "#fb7185"];
const color = (i) => palette[i % palette.length];
const fmt = (v) => (v ?? 0).toLocaleString("en", { maximumFractionDigits: 2 });

async function run() {
  if (!size.value) return;
  loading.value = true;
  try { r.value = (await routeQuote({ market: market.value, side: side.value, size: parseFloat(size.value) })).data; }
  catch { r.value = null; }
  finally { loading.value = false; }
}
</script>

<style scoped>
.route-view { display: flex; flex-direction: column; gap: 20px; }
.page-header h1 { font-size: 18px; color: var(--accent); }
.sub { font-size: 11px; color: var(--muted); margin-top: 2px; }
.run-panel { display: flex; gap: 8px; }
.inp { background: var(--surface); border: 1px solid var(--border); color: var(--text); font-family: var(--font); font-size: 12px; padding: 8px 12px; border-radius: 6px; }
.btn { background: var(--surface); border: 1px solid var(--border); color: var(--muted); padding: 8px 16px; border-radius: 6px; cursor: pointer; font-family: var(--font); font-size: 12px; }
.btn-accent { background: var(--accent); border-color: var(--accent); color: #000; font-weight: 700; }
.btn:disabled { opacity: 0.4; cursor: not-allowed; }
.result { display: flex; flex-direction: column; gap: 16px; }
.summary { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.s { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 14px; }
.sl { font-size: 10px; color: var(--muted); text-transform: uppercase; }
.sv { font-size: 18px; font-weight: 700; margin-top: 4px; display: block; }
.accent { color: var(--accent); } .good { color: var(--good); }
.split-block { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 18px; }
.sb-title { font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 14px; }
.split-bar { display: flex; height: 40px; border-radius: 6px; overflow: hidden; margin-bottom: 14px; }
.seg { display: flex; align-items: center; justify-content: center; font-size: 11px; color: #000; font-weight: 700; transition: width 0.4s; }
.leg-row { display: flex; align-items: center; gap: 10px; font-size: 12px; padding: 5px 0; border-bottom: 1px solid var(--border); }
.dot-c { width: 10px; height: 10px; border-radius: 2px; }
.lv-name { min-width: 90px; font-weight: 700; }
.lv-frac { min-width: 44px; }
.lv-price { flex: 1; }
.muted { color: var(--muted); }
.lv-amt { text-align: right; }
</style>
