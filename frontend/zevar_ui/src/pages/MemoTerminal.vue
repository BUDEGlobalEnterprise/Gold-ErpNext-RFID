<template>
	<div class="h-full flex flex-col">
		<div class="flex items-center justify-between px-4 py-3 border-b dark:border-warm-dark-600">
			<div class="flex items-center gap-3">
				<div class="p-2 bg-indigo-100 dark:bg-indigo-900/30 rounded-lg">
					<svg class="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
							d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
					</svg>
				</div>
				<div>
					<h1 class="text-lg font-bold text-gray-900 dark:text-white">Memo Contracts</h1>
					<p class="text-xs text-gray-500">Vendor consignment tracking with aging &amp; dunning</p>
				</div>
			</div>
			<div class="flex gap-2">
				<button
					@click="loadAging"
					class="px-3 py-2 border rounded-lg text-sm font-medium hover:bg-gray-50 dark:hover:bg-warm-dark-700"
				>
					Aging Summary
				</button>
			</div>
		</div>

		<!-- Filter tabs -->
		<div class="flex gap-1 px-4 py-2 bg-gray-50 dark:bg-warm-dark-800 border-b dark:border-warm-dark-600">
			<button
				v-for="tab in ['All', 'Active', 'Overdue', 'Partial Settlement', 'Settled', 'Returned']"
				:key="tab"
				@click="filterStatus = tab === 'All' ? null : tab"
				class="px-3 py-1 rounded-full text-xs font-medium"
				:class="activeTab === tab
					? 'bg-indigo-600 text-white'
					: 'bg-white dark:bg-warm-dark-700 text-gray-600 hover:bg-gray-100'"
			>
				{{ tab }}
			</button>
		</div>

		<!-- List -->
		<div class="flex-1 overflow-y-auto p-4">
			<div v-if="loading" class="text-center py-8 text-gray-400">Loading...</div>
			<div v-else-if="memos.length === 0" class="text-center py-8">
				<p class="text-gray-400">No memo contracts found</p>
			</div>
			<div v-else class="space-y-2">
				<div
					v-for="m in memos"
					:key="m.name"
					class="border rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-warm-dark-700"
				>
					<div class="flex justify-between">
						<div>
							<span class="font-mono text-sm text-indigo-600">{{ m.name }}</span>
							<span class="text-gray-400 text-xs ml-2">{{ m.supplier_name }}</span>
						</div>
						<div class="text-right">
							<div class="font-bold">{{ fmtCurrency(m.total_memo_value) }}</div>
							<div v-if="m.balance_due > 0" class="text-xs text-red-500">
								Balance: {{ fmtCurrency(m.balance_due) }}
							</div>
						</div>
					</div>
					<div class="flex gap-2 mt-1">
						<span
							class="px-2 py-0.5 text-xs rounded-full"
							:class="statusClass(m.status)"
						>
							{{ m.status }}
						</span>
						<span v-if="m.aging_days > 0" class="text-xs text-red-500">
							{{ m.aging_days }}d overdue
						</span>
						<span class="text-xs text-gray-400">
							{{ m.items_sold || 0 }}/{{ m.item_count || 0 }} sold
						</span>
						<span class="text-xs text-gray-400">
							Due: {{ formatDate(m.due_date) }}
						</span>
					</div>
				</div>
			</div>
		</div>

		<!-- Aging Modal -->
		<BaseModal v-if="showAging" max-width="max-w-3xl" @close="showAging = false">
			<template #header>
				<h3 class="text-lg font-bold">Memo Aging Summary</h3>
			</template>
			<div class="p-6 space-y-4">
				<div v-for="(group, cat) in aging.detail" :key="cat">
					<div class="flex justify-between items-center py-2 border-b">
						<span class="font-medium">{{ cat }}</span>
						<span class="text-sm text-gray-500">
							{{ aging.totals[cat]?.count || 0 }} contracts,
							{{ fmtCurrency(aging.totals[cat]?.value || 0) }}
						</span>
					</div>
					<div v-if="group.length === 0" class="py-2 text-sm text-gray-400">None</div>
					<div v-for="m in group" :key="m.name" class="py-1 text-sm flex justify-between">
						<span>{{ m.name }} — {{ m.supplier_name }}</span>
						<span class="font-mono">{{ fmtCurrency(m.balance_due) }}</span>
					</div>
				</div>
			</div>
		</BaseModal>
	</div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { call, toast } from 'frappe-ui'
import BaseModal from '../components/BaseModal.vue'

const memos = ref([])
const loading = ref(true)
const filterStatus = ref(null)
const showAging = ref(false)
const aging = ref({ detail: {}, totals: {} })

const activeTab = computed(() => filterStatus.value || 'All')

async function loadMemos() {
	loading.value = true
	try {
		const filters = {}
		if (filterStatus.value) {
			filters.status = filterStatus.value
		}
		memos.value = await call('zevar_core.api.memo.get_memo_contracts', { filters, limit: 50 })
	} catch (e) {
		toast({ title: 'Error', message: String(e), intent: 'error' })
	} finally {
		loading.value = false
	}
}

async function loadAging() {
	try {
		aging.value = await call('zevar_core.api.memo.get_memo_aging_summary')
		showAging.value = true
	} catch (e) {
		toast({ title: 'Error', message: String(e), intent: 'error' })
	}
}

function statusClass(status) {
	const map = {
		Active: 'bg-green-100 text-green-700',
		Overdue: 'bg-red-100 text-red-700',
		'Partial Settlement': 'bg-yellow-100 text-yellow-700',
		Settled: 'bg-blue-100 text-blue-700',
		Returned: 'bg-gray-100 text-gray-600',
		Draft: 'bg-gray-100 text-gray-500',
	}
	return map[status] || 'bg-gray-100 text-gray-500'
}

function formatDate(dt) {
	if (!dt) return '--'
	return new Date(dt).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function fmtCurrency(val) {
	return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val || 0)
}

onMounted(loadMemos)
</script>
