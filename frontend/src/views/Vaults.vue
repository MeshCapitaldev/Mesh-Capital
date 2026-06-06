<template>
  <div class="vaults-view">
    <div class="page-header">
      <h1>Compound Vaults</h1>
      <p class="sub">Park capital. It auto-compounds on-chain.</p>
    </div>
    <div class="vault-grid">
      <div v-for="v in vaults" :key="v.vault" class="vault-card">
        <div class="vc-name">{{ v.vault }}</div>
        <div class="vc-apy">{{ (v.apy*100).toFixed(1) }}%<span class="vc-apy-l"> APY</span></div>
        <div class="vc-apr">base APR {{ (v.apr*100).toFixed(1) }}%</div>
        <div class="vc-deposit">
          <input v-model="amounts[v.vault]" class="inp" placeholder="amount" />
          <button class="btn-dep" @click="deposit(v.vault)">Deposit</button>
        </div>
        <span v-if="msg[v.vault]" class="msg">{{ msg[v.vault] }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { listVaults, depositVault } from "@/api/index.js";

const vaults = ref([]), amounts = ref({}), msg = ref({});
const wallet = "demo-wallet";

async function load() { try { vaults.value = (await listVaults()).data.vaults; } catch {} }
async function deposit(vault) {
  const amt = parseFloat(amounts.value[vault]);
  if (!amt) return;
  try { const r = await depositVault({ wallet, vault, amount: amt });
    msg.value[vault] = `✓ Deposited — APY ${(r.data.apy*100).toFixed(1)}%`; }
  catch (e) { msg.value[vault] = e.response?.data?.error || e.message; }
}
onMounted(load);
</script>

<style scoped>
.vaults-view { display: flex; flex-direction: column; gap: 16px; }
.page-header h1 { font-size: 18px; color: var(--accent); }
.sub { font-size: 11px; color: var(--muted); margin-top: 2px; }
.vault-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px; }
.vault-card { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 18px; display: flex; flex-direction: column; gap: 8px; }
.vc-name { font-size: 13px; font-weight: 700; color: var(--text); }
.vc-apy { font-size: 28px; font-weight: 700; color: var(--good); }
.vc-apy-l { font-size: 12px; color: var(--muted); font-weight: 400; }
.vc-apr { font-size: 11px; color: var(--muted); }
.vc-deposit { display: flex; gap: 6px; margin-top: 6px; }
.inp { flex: 1; background: var(--bg); border: 1px solid var(--border); color: var(--text); font-family: var(--font); font-size: 12px; padding: 8px 10px; border-radius: 6px; }
.btn-dep { background: var(--accent); border: none; color: #000; font-weight: 700; padding: 8px 14px; border-radius: 6px; cursor: pointer; font-family: var(--font); font-size: 12px; }
.msg { font-size: 11px; color: var(--good); }
</style>
