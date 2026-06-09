<template>
  <AppLayout>
    <div class="flex flex-col h-full">
      <div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
        <h2 class="premium-title !text-xl sm:!text-2xl">Customer Memos</h2>
        <button @click="showCreate = true" class="px-3 py-1.5 bg-primary-600 text-white rounded-lg text-xs font-semibold hover:bg-primary-700 transition-colors">
          + New Customer Memo
        </button>
      </div>

      <!-- Cards Grid -->
      <div v-if="memos.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 overflow-auto">
        <div v-for="memo in memos" :key="memo.name" class="bg-white dark:bg-warm-dark-800 border border-gray-200 dark:border-warm-border rounded-xl p-4 hover:shadow-md transition-shadow">
          <!-- Card Header -->
          <div class="flex items-center justify-between mb-3">
            <span class="text-sm font-semibold">{{ memo.customer_name }}</span>
            <span :class="dispositionClass(memo.final_disposition)" class="px-2 py-0.5 rounded-full text-xs font-medium">
              {{ memo.final_disposition }}
            </span>
          </div>

          <!-- Items Thumbnails -->
          <div class="flex gap-2 mb-3 overflow-x-auto pb-1">
            <div v-for="(item, idx) in memo.items?.slice(0, 4)" :key="idx"
              class="flex-shrink-0 w-14 h-14 bg-gray-100 dark:bg-warm-dark-700 rounded-lg flex items-center justify-center text-xs text-gray-500 border">
              {{ item.item_code?.slice(-4) || '—' }}
            </div>
            <div v-if="(memo.items?.length || 0) > 4"
              class="flex-shrink-0 w-14 h-14 bg-gray-50 dark:bg-warm-dark-700 rounded-lg flex items-center justify-center text-xs text-gray-400 border">
              +{{ memo.items.length - 4 }}
            </div>
          </div>

          <!-- Meta -->
          <div class="flex items-center justify-between text-xs text-gray-500 mb-3">
            <span>Hold until: <strong :class="isOverdue(memo.due_date) ? 'text-red-500' : ''">{{ formatDate(memo.due_date) }}</strong></span>
            <span>{{ memo.items?.length || 0 }} items</span>
          </div>

          <!-- Signed Slip -->
          <div v-if="memo.customer_signed_return_slip" class="flex items-center gap-2 text-xs text-green-600 mb-3">
            <span>📎</span> Signed slip attached
          </div>

          <!-- Actions -->
          <div class="flex gap-2 pt-2 border-t border-gray-100 dark:border-warm-border">
            <button @click="extendMemo(memo)" class="flex-1 text-xs py-1.5 border border-gray-200 rounded-lg hover:bg-gray-50 dark:hover:bg-warm-dark-700 transition-colors">
              📅 Extend
            </button>
            <button @click="convertToSale(memo)" class="flex-1 text-xs py-1.5 border border-green-200 text-green-700 rounded-lg hover:bg-green-50 transition-colors">
              💰 Sell
            </button>
            <button @click="recordReturn(memo)" class="flex-1 text-xs py-1.5 border border-blue-200 text-blue-700 rounded-lg hover:bg-blue-50 transition-colors">
              ↩ Return
            </button>
          </div>
        </div>
      </div>

      <div v-else class="flex-1 flex items-center justify-center">
        <div class="text-center text-gray-400">
          <div class="text-4xl mb-3">📋</div>
          <p class="text-lg font-medium">No active customer memos</p>
          <p class="text-sm">Customer take-home approvals will appear here</p>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'

const showCreate = ref(false)
const memos = ref([])

function dispositionClass(d) {
  const map = { 'Open': 'bg-blue-100 text-blue-700', 'Sold': 'bg-green-100 text-green-700', 'Returned': 'bg-gray-100 text-gray-600', 'Partial Return': 'bg-amber-100 text-amber-700' }
  return map[d] || 'bg-gray-100 text-gray-600'
}

function isOverdue(date) {
  if (!date) return false
  return new Date(date) < new Date()
}

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

async function loadData() {
  try {
    const res = await frappe.call({
      method: 'zevar_core.api.inventory_v2.get_memo_aging_dashboard',
      args: { memo_class: 'Customer' }
    })
    memos.value = res?.message?.memos || []
  } catch (e) {
    console.error('Failed to load customer memos:', e)
  }
}

function extendMemo(memo) { /* TODO */ }
function convertToSale(memo) { /* TODO */ }
function recordReturn(memo) { /* TODO */ }

onMounted(loadData)
</script>
