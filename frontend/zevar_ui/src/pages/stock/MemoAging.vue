<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<h2 class="premium-title !text-xl sm:!text-2xl">Memo Aging Dashboard</h2>
				<div class="flex items-center gap-2">
					<select v-model="memoClass" @change="loadData" class="px-3 py-1.5 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-xs text-gray-900 dark:text-white">
						<option value="">All Classes</option>
						<option value="Vendor">Vendor Memos</option>
						<option value="Customer">Customer Memos</option>
					</select>
					<button @click="loadData" class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-warm-dark-700" title="Refresh">
						<svg class="w-4 h-4 text-gray-500" :class="{ 'animate-spin': store.memoAgingResource.loading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357 2m15.357 2H15" />
						</svg>
					</button>
				</div>
			</div>

			<!-- Summary Cards -->
			<div class="grid grid-cols-4 gap-3 mb-6">
				<div v-for="(bucket, key) in buckets" :key="key" class="bg-white dark:bg-warm-dark-800 border rounded-xl p-4"
					:class="bucketBorderClass(key)">
					<div class="text-xs text-gray-500 mb-1">{{ key }} days</div>
					<div class="text-2xl font-bold" :class="bucketTextClass(key)">{{ bucket.length }}</div>
					<div class="text-[10px] text-gray-400 mt-1">open memos</div>
				</div>
			</div>

			<!-- Bucket Tables -->
			<div v-for="(bucket, key) in buckets" :key="key" class="mb-4">
				<div v-if="bucket.length" class="mb-3">
					<h3 class="text-xs font-bold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wider">
						{{ key }} Days Out {{ key === '30+' ? '(Critical)' : '' }}
					</h3>
					<div class="space-y-2">
						<div v-for="memo in bucket" :key="memo.memo_contract"
							class="bg-white dark:bg-warm-dark-800 border border-gray-200 dark:border-warm-border rounded-lg p-3 flex items-center justify-between">
							<div class="flex items-center gap-3">
								<div>
									<span class="text-sm font-semibold text-gray-900 dark:text-white">{{ memo.memo_contract }}</span>
									<span class="ml-2 px-1.5 py-0.5 rounded text-[10px] font-bold"
										:class="memo.memo_class === 'Vendor' ? 'bg-blue-100 text-blue-700' : 'bg-purple-100 text-purple-700'">
										{{ memo.memo_class }}
									</span>
								</div>
								<div class="text-xs text-gray-500">
									{{ memo.memo_class === 'Customer' ? memo.customer : memo.vendor }}
								</div>
							</div>
							<div class="flex items-center gap-4">
								<div class="text-right">
									<div class="text-xs font-bold text-gray-900 dark:text-white">{{ memo.open_items }} items</div>
									<div class="text-[10px] text-gray-400">{{ memo.days_out }}d out</div>
								</div>
								<button @click="openMemoActions(memo)" class="px-2 py-1 text-[10px] font-bold text-[#D4AF37] border border-[#D4AF37] rounded hover:bg-[#D4AF37]/10">
									Actions
								</button>
							</div>
						</div>
					</div>
				</div>
			</div>

			<div v-if="!hasData && !store.memoAgingResource.loading" class="text-center text-gray-400 text-sm py-12">
				No open memos found.
			</div>

			<!-- Memo Actions Modal -->
			<BaseModal v-if="showActions" @close="showActions = false" :title="`Memo ${activeMemo?.memo_contract}`">
				<div class="p-4 space-y-3">
					<div class="text-xs text-gray-500">
						{{ activeMemo?.memo_class }} memo for {{ activeMemo?.memo_class === 'Customer' ? activeMemo?.customer : activeMemo?.vendor }}
						&mdash; {{ activeMemo?.days_out }} days out, {{ activeMemo?.open_items }} open items
					</div>
					<div class="space-y-2">
						<div>
							<label class="text-xs font-semibold text-gray-700 dark:text-gray-300">Item Code</label>
							<input v-model="actionItemCode" type="text" class="mt-1 w-full px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 rounded-lg text-xs" placeholder="Item code" />
						</div>
						<div>
							<label class="text-xs font-semibold text-gray-700 dark:text-gray-300">Serial No (optional)</label>
							<input v-model="actionSerial" type="text" class="mt-1 w-full px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 rounded-lg text-xs" />
						</div>
					</div>
					<div class="flex gap-2 pt-2">
						<button @click="doMarkSold" class="flex-1 px-3 py-2 bg-green-600 text-white rounded-lg text-xs font-bold hover:bg-green-700">Mark Sold</button>
						<button @click="doMarkReturned" class="flex-1 px-3 py-2 bg-blue-600 text-white rounded-lg text-xs font-bold hover:bg-blue-700">Mark Returned</button>
					</div>
				</div>
			</BaseModal>
		</div>
	</AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '../../components/AppLayout.vue'
import BaseModal from '../../components/BaseModal.vue'
import { useInventoryV2Store } from '../../stores/inventoryV2'

const store = useInventoryV2Store()

const memoClass = ref('')
const showActions = ref(false)
const activeMemo = ref(null)
const actionItemCode = ref('')
const actionSerial = ref('')

const buckets = computed(() => store.memoAging?.buckets || { '0-7': [], '8-14': [], '15-30': [], '30+': [] })
const hasData = computed(() => store.memoAging?.total_open > 0)

function loadData() {
	store.loadMemoAging(memoClass.value || undefined)
}

function bucketBorderClass(key) {
	if (key === '30+') return 'border-red-300 dark:border-red-800'
	if (key === '15-30') return 'border-yellow-300 dark:border-yellow-800'
	return 'border-gray-200 dark:border-warm-border'
}

function bucketTextClass(key) {
	if (key === '30+') return 'text-red-600'
	if (key === '15-30') return 'text-yellow-600'
	return 'text-gray-900 dark:text-white'
}

function openMemoActions(memo) {
	activeMemo.value = memo
	actionItemCode.value = ''
	actionSerial.value = ''
	showActions.value = true
}

async function doMarkSold() {
	if (!activeMemo.value || !actionItemCode.value) return
	try {
		await store.markMemoSold(activeMemo.value.memo_contract, actionItemCode.value, actionSerial.value || undefined)
		showActions.value = false
		loadData()
	} catch (e) { alert(`Error: ${e.message}`) }
}

async function doMarkReturned() {
	if (!activeMemo.value || !actionItemCode.value) return
	try {
		await store.markMemoReturned(activeMemo.value.memo_contract, actionItemCode.value, actionSerial.value || undefined)
		showActions.value = false
		loadData()
	} catch (e) { alert(`Error: ${e.message}`) }
}

onMounted(() => loadData())
</script>
