<template>
  <div class="parts-picker">
    <div class="picker-header">
      <h4 class="picker-title">🔩 Parts Consumption</h4>
      <span class="parts-count" v-if="consumedParts.length">{{ consumedParts.length }} parts</span>
    </div>

    <!-- Suggested Parts (from BOM) -->
    <div v-if="suggestedParts.length" class="section">
      <label class="section-label">Suggested (from BOM)</label>
      <div
        v-for="(part, idx) in suggestedParts"
        :key="'s-' + idx"
        class="part-row suggested"
        :class="{ consumed: isConsumed(part) }"
      >
        <span class="part-icon">{{ part.component_type === 'Finding' ? '🔗' : '💎' }}</span>
        <span class="part-name">{{ part.component_item_name || part.component_item }}</span>
        <span class="part-qty">× {{ part.qty_per_build || 1 }}</span>
        <div class="stock-indicator" :class="stockLevel(part)">
          {{ stockQty(part) }} avail
        </div>
        <button
          v-if="!isConsumed(part)"
          class="btn-consume"
          @click="consumePart(part)"
          :disabled="stockQty(part) <= 0"
        >
          + Use
        </button>
        <span v-else class="consumed-check">✓</span>
      </div>
    </div>

    <!-- Custom Part Search -->
    <div class="section">
      <label class="section-label">Add Custom Part</label>
      <div class="search-row">
        <input
          v-model="searchQuery"
          class="search-input"
          placeholder="Search findings, melee, chain..."
          @input="debouncedSearch"
        />
      </div>
      <div v-if="searchResults.length" class="search-results">
        <div
          v-for="item in searchResults"
          :key="item.item_code"
          class="search-result-row"
          @click="addCustomPart(item)"
        >
          <span class="result-name">{{ item.item_name }}</span>
          <span class="result-code">{{ item.item_code }}</span>
          <span class="result-stock" :class="item.qty > 0 ? 'in-stock' : 'no-stock'">
            {{ item.qty || 0 }} {{ item.stock_uom }}
          </span>
        </div>
      </div>
    </div>

    <!-- Consumed Parts List -->
    <div v-if="consumedParts.length" class="section">
      <label class="section-label">Consumed</label>
      <div v-for="(cp, idx) in consumedParts" :key="'c-' + idx" class="consumed-row">
        <span class="consumed-name">{{ cp.component_item_name }}</span>
        <input v-model.number="cp.qty" class="qty-input" type="number" min="0.01" step="0.01" />
        <span class="consumed-uom">{{ cp.uom }}</span>
        <span v-if="cp.serial_no" class="consumed-serial">SN: {{ cp.serial_no }}</span>
        <button class="btn-remove" @click="removePart(idx)" title="Remove">&times;</button>
      </div>
      <div class="consumed-total">
        Total cost: <strong>${{ totalCost.toFixed(2) }}</strong>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  suggestedParts: { type: Array, default: () => [] },
  sourceWarehouse: { type: String, default: '' },
  warehouseStock: { type: Object, default: () => ({}) }
})

const emit = defineEmits(['consume', 'remove', 'search'])

const searchQuery = ref('')
const searchResults = ref([])
const consumedParts = ref([])

let searchTimeout = null

function debouncedSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    if (searchQuery.value.length >= 2) {
      emit('search', searchQuery.value)
    } else {
      searchResults.value = []
    }
  }, 300)
}

function stockQty(part) {
  return props.warehouseStock[part.component_item] || 0
}

function stockLevel(part) {
  const qty = stockQty(part)
  if (qty <= 0) return 'stock-empty'
  if (qty <= 5) return 'stock-low'
  return 'stock-ok'
}

function isConsumed(part) {
  return consumedParts.value.some(cp => cp.component_item === part.component_item)
}

function consumePart(part) {
  const entry = {
    component_item: part.component_item,
    component_item_name: part.component_item_name || part.component_item,
    qty: part.qty_per_build || 1,
    uom: part.uom || 'Nos',
    unit_cost: part.valuation_rate || 0,
    source_warehouse: props.sourceWarehouse,
    serial_no: '',
    notes: ''
  }
  consumedParts.value.push(entry)
  emit('consume', entry)
}

function addCustomPart(item) {
  const entry = {
    component_item: item.item_code,
    component_item_name: item.item_name,
    qty: 1,
    uom: item.stock_uom || 'Nos',
    unit_cost: item.valuation_rate || 0,
    source_warehouse: props.sourceWarehouse,
    serial_no: '',
    notes: ''
  }
  consumedParts.value.push(entry)
  searchQuery.value = ''
  searchResults.value = []
  emit('consume', entry)
}

function removePart(idx) {
  const removed = consumedParts.value.splice(idx, 1)[0]
  emit('remove', removed)
}

const totalCost = computed(() =>
  consumedParts.value.reduce((sum, cp) => sum + cp.qty * cp.unit_cost, 0)
)

defineExpose({ consumedParts, setSearchResults: (r) => { searchResults.value = r } })
</script>

<style scoped>
.parts-picker { border: 1px solid var(--border-color, #e2e8f0); border-radius: 8px; overflow: hidden; }
.picker-header { display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; background: var(--bg-light, #f8fafc); border-bottom: 1px solid #e2e8f0; }
.picker-title { font-size: 14px; font-weight: 700; margin: 0; }
.parts-count { font-size: 12px; color: #64748b; background: #e2e8f0; padding: 2px 8px; border-radius: 10px; }
.section { padding: 12px 16px; border-bottom: 1px solid #f1f5f9; }
.section-label { font-size: 11px; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; display: block; margin-bottom: 8px; }
.part-row { display: flex; align-items: center; gap: 8px; padding: 8px; border-radius: 6px; transition: background 0.15s; }
.part-row:hover { background: #f8fafc; }
.part-row.consumed { opacity: 0.6; }
.part-icon { font-size: 14px; }
.part-name { flex: 1; font-size: 13px; }
.part-qty { color: #64748b; font-size: 12px; }
.stock-indicator { font-size: 11px; padding: 2px 6px; border-radius: 4px; font-weight: 600; }
.stock-ok { background: #dcfce7; color: #166534; }
.stock-low { background: #fef3c7; color: #92400e; }
.stock-empty { background: #fef2f2; color: #991b1b; }
.btn-consume { padding: 4px 10px; border: 1px solid #3b82f6; border-radius: 4px; background: white; color: #3b82f6; font-size: 11px; font-weight: 600; cursor: pointer; transition: all 0.15s; }
.btn-consume:hover:not(:disabled) { background: #3b82f6; color: white; }
.btn-consume:disabled { opacity: 0.4; cursor: not-allowed; }
.consumed-check { color: #22c55e; font-weight: 700; }
.search-row { margin-bottom: 8px; }
.search-input { width: 100%; padding: 8px 12px; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 13px; }
.search-input:focus { outline: none; border-color: #3b82f6; }
.search-results { max-height: 160px; overflow-y: auto; border: 1px solid #e2e8f0; border-radius: 6px; }
.search-result-row { display: flex; align-items: center; gap: 8px; padding: 8px 12px; cursor: pointer; border-bottom: 1px solid #f1f5f9; font-size: 12px; }
.search-result-row:hover { background: #eff6ff; }
.result-name { flex: 1; }
.result-code { color: #94a3b8; }
.in-stock { color: #16a34a; }
.no-stock { color: #dc2626; }
.consumed-row { display: flex; align-items: center; gap: 8px; padding: 6px 0; border-bottom: 1px solid #f1f5f9; }
.consumed-name { flex: 1; font-size: 13px; }
.qty-input { width: 60px; padding: 4px 8px; border: 1px solid #e2e8f0; border-radius: 4px; font-size: 12px; text-align: center; }
.consumed-uom { color: #94a3b8; font-size: 11px; }
.consumed-serial { font-size: 11px; color: #6366f1; background: #eef2ff; padding: 2px 6px; border-radius: 3px; }
.btn-remove { background: none; border: none; color: #ef4444; font-size: 18px; cursor: pointer; padding: 0 4px; }
.consumed-total { text-align: right; padding: 8px 0; font-size: 13px; color: #475569; }
</style>
