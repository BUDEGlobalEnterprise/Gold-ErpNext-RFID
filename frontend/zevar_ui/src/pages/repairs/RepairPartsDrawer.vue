<template>
  <AppLayout>
    <div class="flex flex-col h-full">
      <div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
        <h2 class="premium-title !text-xl sm:!text-2xl">Repair Parts</h2>
        <div class="flex items-center gap-2">
          <select v-model="repairFilter" @change="loadData" class="px-3 py-1.5 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-xs">
            <option value="">All Repairs</option>
            <option value="In Progress">In Progress</option>
            <option value="Pending Parts">Pending Parts</option>
          </select>
        </div>
      </div>

      <!-- Split View: Repairs List + Parts Panel -->
      <div class="flex gap-4 flex-1 overflow-hidden">
        <!-- Left: Repair Orders -->
        <div class="w-1/2 bg-white dark:bg-warm-dark-800 border border-gray-200 dark:border-warm-border rounded-xl overflow-auto">
          <div v-for="ro in repairOrders" :key="ro.name"
            class="p-4 border-b border-gray-100 dark:border-warm-border cursor-pointer hover:bg-gray-50 dark:hover:bg-warm-dark-700 transition-colors"
            :class="{ 'bg-primary-50 dark:bg-primary-900/10 border-l-2 border-l-primary-500': selectedRepair?.name === ro.name }"
            @click="selectRepair(ro)">
            <div class="flex items-center justify-between mb-1">
              <span class="font-mono text-xs font-semibold text-primary-600">{{ ro.name }}</span>
              <span :class="roStatusClass(ro.status)" class="px-2 py-0.5 rounded-full text-xs font-medium">{{ ro.status }}</span>
            </div>
            <div class="text-sm">{{ ro.item_name }}</div>
            <div class="flex items-center justify-between text-xs text-gray-500 mt-1">
              <span>{{ ro.customer_name }}</span>
              <span>{{ ro.parts_consumed_count || 0 }} parts used</span>
            </div>
          </div>
          <div v-if="!repairOrders.length" class="p-8 text-center text-gray-400">
            No repair orders found
          </div>
        </div>

        <!-- Right: Parts Picker for Selected Repair -->
        <div class="w-1/2">
          <div v-if="selectedRepair" class="h-full">
            <PartsConsumptionPicker
              :suggestedParts="suggestedParts"
              :sourceWarehouse="sourceWarehouse"
              :warehouseStock="warehouseStock"
              @consume="onConsumePart"
              @remove="onRemovePart"
              @search="onSearchParts"
              ref="pickerRef"
            />
          </div>
          <div v-else class="h-full flex items-center justify-center bg-white dark:bg-warm-dark-800 border border-gray-200 dark:border-warm-border rounded-xl">
            <div class="text-center text-gray-400">
              <div class="text-3xl mb-2">👈</div>
              <p>Select a repair order to manage parts</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '../../components/AppLayout.vue'
import PartsConsumptionPicker from '../../components/repairs/PartsConsumptionPicker.vue'

const repairFilter = ref('')
const repairOrders = ref([])
const selectedRepair = ref(null)
const suggestedParts = ref([])
const sourceWarehouse = ref('')
const warehouseStock = ref({})
const pickerRef = ref(null)

function roStatusClass(s) {
  const map = { 'In Progress': 'bg-blue-100 text-blue-700', 'Pending Parts': 'bg-amber-100 text-amber-700', 'Completed': 'bg-green-100 text-green-700' }
  return map[s] || 'bg-gray-100 text-gray-600'
}

async function loadData() {
  try {
    const res = await frappe.call({
      method: 'zevar_core.api.repair.get_repair_orders',
      args: { status: repairFilter.value || undefined, limit: 50 }
    })
    repairOrders.value = res?.message || []
  } catch (e) {
    console.error('Failed to load repair orders:', e)
  }
}

async function selectRepair(ro) {
  selectedRepair.value = ro
  try {
    const res = await frappe.call({
      method: 'zevar_core.api.inventory_v2.list_repair_parts_for_repair',
      args: { repair_order: ro.name }
    })
    suggestedParts.value = res?.message?.suggested || []
    warehouseStock.value = res?.message?.stock || {}
    sourceWarehouse.value = res?.message?.source_warehouse || ''
  } catch (e) {
    console.error('Failed to load repair parts:', e)
  }
}

async function onConsumePart(entry) {
  try {
    await frappe.call({
      method: 'zevar_core.api.inventory_v2.consume_repair_part',
      args: { repair_order: selectedRepair.value.name, ...entry }
    })
    frappe.show_alert({ message: `${entry.component_item_name} consumed`, indicator: 'green' })
  } catch (e) {
    frappe.show_alert({ message: `Error: ${e.message}`, indicator: 'red' })
  }
}

async function onRemovePart(entry) {
  /* TODO: call return_repair_part */
}

async function onSearchParts(query) {
  try {
    const res = await frappe.call({
      method: 'frappe.client.get_list',
      args: { doctype: 'Item', filters: { item_group: ['in', ['Findings', 'Melee Diamonds', 'Chain by Foot']], item_name: ['like', `%${query}%`] }, fields: ['item_code', 'item_name', 'stock_uom', 'valuation_rate'], limit: 10 }
    })
    if (pickerRef.value) pickerRef.value.setSearchResults(res?.message || [])
  } catch (e) { console.error(e) }
}

onMounted(loadData)
</script>
