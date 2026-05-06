<template>
	<BaseModal :show="true" max-width="max-w-3xl" scrollable @close="$emit('close')">
		<template #header>
			<div class="flex items-center gap-3">
				<div class="p-2 bg-amber-100 dark:bg-amber-900/30 rounded-lg">
					<svg class="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
					</svg>
				</div>
				<div>
					<h3 class="text-lg font-bold text-gray-900 dark:text-white">Stock Reductions</h3>
					<p class="text-xs text-gray-500">Auto-detected stock reductions from sales (last {{ hours }}h)</p>
				</div>
			</div>
		</template>

		<div class="p-6 pt-4">
			<div class="flex items-center gap-3 mb-4">
				<select
					v-model="hours"
					@change="loadReductions"
					class="px-3 py-1.5 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
				>
					<option :value="1">Last 1 hour</option>
					<option :value="6">Last 6 hours</option>
					<option :value="12">Last 12 hours</option>
					<option :value="24">Last 24 hours</option>
					<option :value="48">Last 48 hours</option>
					<option :value="168">Last 7 days</option>
				</select>
				<span class="text-xs text-gray-500">{{ reductions.length }} reduction(s)</span>
				<button
					@click="loadReductions"
					class="ml-auto p-1.5 hover:bg-gray-100 dark:hover:bg-warm-dark-700 rounded-lg"
					title="Refresh"
				>
					<svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
					</svg>
				</button>
			</div>

			<div v-if="loading" class="text-center py-8 text-sm text-gray-400">Loading...</div>

			<div v-else-if="reductions.length === 0" class="text-center py-8">
				<div class="text-4xl mb-2">-</div>
				<p class="text-sm text-gray-500">No stock reductions detected in the last {{ hours }} hours.</p>
			</div>

			<div v-else class="space-y-2">
				<div
					v-for="r in reductions"
					:key="r.log_id"
					class="flex items-center gap-3 p-3 bg-gray-50 dark:bg-warm-dark-900 rounded-lg border border-gray-100 dark:border-warm-border/30"
				>
					<div class="w-8 h-8 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center shrink-0">
						<svg class="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
						</svg>
					</div>
					<div class="flex-1 min-w-0">
						<div class="flex items-center gap-2">
							<span class="text-xs font-bold text-gray-900 dark:text-white">{{ r.item_code }}</span>
							<span v-if="r.serial_no" class="text-[10px] font-mono bg-gray-200 dark:bg-warm-dark-700 px-1.5 py-0.5 rounded">{{ r.serial_no }}</span>
						</div>
						<div class="text-[10px] text-gray-500 mt-0.5">
							{{ r.item_name || '' }}
							<span v-if="r.warehouse"> &middot; {{ r.warehouse }}</span>
						</div>
					</div>
					<div class="text-right shrink-0">
						<div class="text-xs font-bold text-red-600">-{{ r.qty_reduced || 1 }}</div>
						<div v-if="r.valuation_rate" class="text-[10px] text-gray-500">${{ (r.valuation_rate || 0).toFixed(2) }}</div>
					</div>
					<div class="text-right shrink-0 pl-2 border-l border-gray-200 dark:border-warm-border/30">
						<div class="text-[10px] text-gray-500">
							{{ formatTime(r.reduced_at) }}
						</div>
						<div class="text-[10px] text-gray-400">
							{{ r.invoice || '' }}
						</div>
					</div>
				</div>
			</div>
		</div>

		<template #footer>
			<button
				@click="$emit('close')"
				class="flex-1 py-2 border rounded-lg text-sm font-medium hover:bg-gray-50"
			>
				Close
			</button>
		</template>
	</BaseModal>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { call } from 'frappe-ui'
import BaseModal from './BaseModal.vue'

const emit = defineEmits(['close'])

const reductions = ref([])
const loading = ref(false)
const hours = ref(24)

function formatTime(dt) {
	if (!dt) return ''
	try {
		const d = new Date(dt)
		return d.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })
	} catch { return dt }
}

async function loadReductions() {
	loading.value = true
	try {
		const res = await call('zevar_core.services.stock_reduction.get_recent_reductions', {
			hours: hours.value,
			limit: 100,
		})
		reductions.value = res.reductions || []
	} catch {
		reductions.value = []
	} finally {
		loading.value = false
	}
}

onMounted(() => loadReductions())
</script>
