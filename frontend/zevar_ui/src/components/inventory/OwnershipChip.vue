<template>
  <span class="ownership-chip" :class="chipClass" :title="tooltipText">
    <span class="chip-dot"></span>
    <span class="chip-label">{{ label }}</span>
    <span v-if="ownerName" class="chip-owner">{{ ownerName }}</span>
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  ownershipType: { type: String, default: 'Owned' }, // Owned | Memo | Consigned | Customer-Owned
  ownerName: { type: String, default: '' }
})

const label = computed(() => {
  const map = { 'Owned': 'Owned', 'Memo': 'Memo', 'Consigned': 'Consigned', 'Customer-Owned': 'Cust.' }
  return map[props.ownershipType] || props.ownershipType
})

const chipClass = computed(() => {
  const map = { 'Owned': 'chip-owned', 'Memo': 'chip-memo', 'Consigned': 'chip-consigned', 'Customer-Owned': 'chip-customer' }
  return map[props.ownershipType] || 'chip-owned'
})

const tooltipText = computed(() => {
  if (props.ownerName) return `${props.ownershipType} — ${props.ownerName}`
  return props.ownershipType
})
</script>

<style scoped>
.ownership-chip { display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; white-space: nowrap; }
.chip-dot { width: 6px; height: 6px; border-radius: 50%; }
.chip-owner { font-weight: 400; opacity: 0.8; max-width: 80px; overflow: hidden; text-overflow: ellipsis; }
.chip-owned { background: #dcfce7; color: #166534; }
.chip-owned .chip-dot { background: #22c55e; }
.chip-memo { background: #fef3c7; color: #92400e; }
.chip-memo .chip-dot { background: #f59e0b; }
.chip-consigned { background: #e0e7ff; color: #3730a3; }
.chip-consigned .chip-dot { background: #6366f1; }
.chip-customer { background: #fce7f3; color: #9d174d; }
.chip-customer .chip-dot { background: #ec4899; }
</style>
