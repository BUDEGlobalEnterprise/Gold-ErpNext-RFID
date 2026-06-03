<template>
  <div class="pricing-method-picker">
    <label class="picker-label">Pricing Method</label>
    <div class="method-options">
      <button
        v-for="method in methods"
        :key="method.value"
        class="method-btn"
        :class="{ active: modelValue === method.value }"
        @click="$emit('update:modelValue', method.value)"
        :title="method.description"
      >
        <span class="method-icon">{{ method.icon }}</span>
        <span class="method-name">{{ method.label }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({ modelValue: { type: String, default: 'Fine' } })
defineEmits(['update:modelValue'])

const methods = [
  { value: 'Fine', label: 'Fine', icon: '💎', description: 'Each piece gets its own SKU; serialized tracking' },
  { value: 'Bulk UPC', label: 'Bulk UPC', icon: '📦', description: 'Quantity of identical items by UPC/SKU' },
  { value: 'Bulk IUOM', label: 'Bulk IUOM', icon: '⚖️', description: 'Carried in quantity, sold per measure (melee parcels)' },
  { value: 'Bulk UOM', label: 'Bulk UOM', icon: '📏', description: 'Carried in measure only, sold per measure (gold stock)' },
  { value: 'Bulk Mixed', label: 'Mixed', icon: '🔀', description: 'Group of like items with differing costs but consistent markup' },
]
</script>

<style scoped>
.pricing-method-picker { display: flex; flex-direction: column; gap: 8px; }
.picker-label { font-size: 12px; font-weight: 600; color: var(--text-muted, #64748b); text-transform: uppercase; letter-spacing: 0.05em; }
.method-options { display: flex; gap: 6px; flex-wrap: wrap; }
.method-btn { display: flex; align-items: center; gap: 4px; padding: 6px 12px; border: 1px solid var(--border-color, #e2e8f0); border-radius: 6px; background: white; cursor: pointer; font-size: 12px; transition: all 0.15s; }
.method-btn:hover { border-color: var(--primary, #3b82f6); background: var(--primary-50, #eff6ff); }
.method-btn.active { border-color: var(--primary, #3b82f6); background: var(--primary-50, #eff6ff); color: var(--primary, #3b82f6); font-weight: 600; box-shadow: 0 0 0 1px var(--primary, #3b82f6); }
.method-icon { font-size: 14px; }
</style>
