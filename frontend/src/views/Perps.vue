<template>
  <div class="perps-view">
    <div class="page-header">
      <h1>Perps</h1>
      <p class="sub">Routed to the venue with the best mark and funding, every time.</p>
    </div>

    <div class="grid-2">
      <div class="panel">
        <h2>Open position</h2>
        <input v-model="form.wallet" class="inp" placeholder="Wallet address" />
        <select v-model="form.market" class="inp">
          <option v-for="m in markets" :key="m" :value="m">{{ m }}</option>
        </select>
        <select v-model="form.side" class="inp">
          <option value="LONG">LONG</option><option value="SHORT">SHORT</option>
        </select>
        <input v-model="form.size_usd" class="inp" placeholder="Size USD" />
        <input v-model="form.leverage" class="inp" placeholder="Leverage" />
        <button class="btn-accent" @click="open" :disabled="busy">{{ busy ? "Routing..." : "Open (routed)" }}</button>
        <span v-if="err" class="err">{{ err }}</span>
      </div>

      <div class="panel">
        <div class="panel-hdr"><h2>Your positions</h2><button class="btn" @click="load">Load</button></div>
        <input v-model="form.wallet" class="inp" placeholder="wallet to load" />
        <div v-if="positions.length === 0" class="empty">No positions.</div>
        <div v-for="p in positions" :key="p.id" class="pos" :class="p.side.toLowerCase()">
          <div class="ph">
            <span class="p-market">{{ p.market }}</span>
            <span class="p-side" :class="p.side.toLowerCase()">{{ p.side }}</span>
            <span class="p-venue">{{ p.venue }}</span>
            <span class="p-status" :class="p.status">{{ p.status }}</span>
          </div>
          <div class="pstats">
            <span>${{ fmt(p.size_usd) }} · {{ p.leverage }}x</span>
            <span>entry {{ p.entry_price?.toFixed(2) }}</span>
            <span v-if="p.unrealized_pnl_usd !== undefined" :class="p.unrealized_pnl_usd>=0?'good':'bad'">uPnL ${{ fmt(p.unrealized_pnl_usd) }}</span>
            <span v-if="p.realized_pnl_usd !== null && p.realized_pnl_usd !== undefined" :class="p.realized_pnl_usd>=0?'good':'bad'">PnL ${{ fmt(p.realized_pnl_usd) }}</span>
          </div>
          <button v-if="p.status === 'open'" class="btn-close" @click="close(p.id)">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { openPerp, closePerp, listPerps } from "@/api/index.js";

const markets = ["SOL-USDC", "BTC-USDC", "ETH-USDC", "WIF-USDC", "JUP-USDC", "JTO-USDC"];
const form = ref({ wallet: "", market: "SOL-USDC", side: "LONG", size_usd: "1000", leverage: "5" });
const positions = ref([]), busy = ref(false), err = ref(null);
const fmt = (v) => (v ?? 0).toLocaleString("en", { maximumFractionDigits: 2 });

async function open() {
  busy.value = true; err.value = null;
  try {
    await openPerp({ wallet: form.value.wallet, market: form.value.market, side: form.value.side,
      size_usd: parseFloat(form.value.size_usd), leverage: parseFloat(form.value.leverage) });
    await load();
  } catch (e) { err.value = e.response?.data?.error || e.message; }
  finally { busy.value = false; }
}
async function close(id) { try { await closePerp(id); await load(); } catch {} }
async function load() { if (!form.value.wallet) return; try { positions.value = (await listPerps(form.value.wallet)).data.positions; } catch {} }
</script>

<style scoped>
.perps-view { display: flex; flex-direction: column; gap: 20px; }
.page-header h1 { font-size: 18px; color: var(--accent); }
.sub { font-size: 11px; color: var(--muted); margin-top: 2px; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.panel { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 18px; display: flex; flex-direction: column; gap: 10px; }
.panel-hdr { display: flex; justify-content: space-between; align-items: center; }
.panel h2 { font-size: 14px; }
.inp { background: var(--bg); border: 1px solid var(--border); color: var(--text); font-family: var(--font); font-size: 12px; padding: 8px 12px; border-radius: 6px; }
.btn { background: var(--surface); border: 1px solid var(--border); color: var(--muted); padding: 6px 14px; border-radius: 6px; cursor: pointer; font-family: var(--font); font-size: 12px; }
.btn-accent { background: var(--accent); border: none; color: #000; font-weight: 700; padding: 9px; border-radius: 6px; cursor: pointer; font-family: var(--font); font-size: 12px; }
.btn:disabled, .btn-accent:disabled { opacity: 0.4; cursor: not-allowed; }
.err { color: var(--bad); font-size: 11px; }
.empty { color: var(--muted); text-align: center; padding: 20px 0; font-size: 12px; }
.pos { background: var(--bg); border: 1px solid var(--border); border-radius: 6px; padding: 12px; display: flex; flex-direction: column; gap: 8px; }
.pos.long { border-left: 3px solid var(--good); } .pos.short { border-left: 3px solid var(--bad); }
.ph { display: flex; align-items: center; gap: 10px; font-size: 12px; }
.p-market { font-weight: 700; }
.p-side { font-size: 10px; padding: 1px 6px; border-radius: 3px; }
.p-side.long { background: rgba(52,211,153,0.1); color: var(--good); }
.p-side.short { background: rgba(244,63,94,0.1); color: var(--bad); }
.p-venue { font-size: 11px; color: var(--accent2); }
.p-status { margin-left: auto; font-size: 10px; text-transform: uppercase; color: var(--muted); }
.pstats { display: flex; gap: 16px; font-size: 11px; flex-wrap: wrap; }
.good { color: var(--good); } .bad { color: var(--bad); }
.btn-close { align-self: flex-start; background: transparent; border: 1px solid var(--border); color: var(--muted); padding: 4px 12px; border-radius: 4px; cursor: pointer; font-family: var(--font); font-size: 11px; }
</style>
