<template>
	<div class="premium-card !p-5">
		<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-4">What-If Price Simulator</h3>

		<!-- Input Form -->
		<div class="flex flex-col sm:flex-row items-start sm:items-end gap-3 mb-5">
			<div class="flex-1 w-full">
				<label class="block text-[10px] font-medium text-gray-500 dark:text-gray-400 mb-1">Item Code</label>
				<input
					v-model="itemCode"
					type="text"
					placeholder="e.g. RING-GOLD-001"
					class="w-full px-3 py-2 text-xs border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-1 focus:ring-indigo-400"
				/>
			</div>
			<div class="w-full sm:w-36">
				<label class="block text-[10px] font-medium text-gray-500 dark:text-gray-400 mb-1">New Price ($)</label>
				<input
					v-model.number="newPrice"
					type="number"
					step="0.01"
					min="0"
					placeholder="0.00"
					class="w-full px-3 py-2 text-xs border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-1 focus:ring-indigo-400"
				/>
			</div>
			<button
				@click="simulate"
				:disabled="!itemCode || !newPrice || simulating"
				class="px-4 py-2 text-xs font-medium rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors whitespace-nowrap"
			>
				<span v-if="simulating" class="flex items-center gap-1">
					<span class="animate-spin rounded-full h-3 w-3 border-b border-white"></span>
					Simulating...
				</span>
				<span v-else>Simulate</span>
			</button>
		</div>

		<!-- Simulation Error -->
		<div
			v-if="simError"
			class="mb-4 p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800"
		>
			<p class="text-[10px] text-red-600 dark:text-red-400">{{ simError }}</p>
		</div>

		<!-- Results -->
		<div v-if="result" class="space-y-4">
			<!-- Comparison Grid -->
			<div class="grid grid-cols-2 gap-3">
				<div class="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-3">
					<p class="text-[10px] text-gray-500 dark:text-gray-400 mb-1">Current Price</p>
					<p class="text-base font-bold text-gray-900 dark:text-white">{{ fmtCurrency(result.current_price) }}</p>
				</div>
				<div class="bg-indigo-50 dark:bg-indigo-900/20 rounded-xl p-3">
					<p class="text-[10px] text-indigo-500 mb-1">New Price</p>
					<p class="text-base font-bold text-indigo-700 dark:text-indigo-300">{{ fmtCurrency(result.new_price) }}</p>
				</div>
				<div class="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-3">
					<p class="text-[10px] text-gray-500 dark:text-gray-400 mb-1">Current Margin</p>
					<p class="text-base font-bold text-gray-900 dark:text-white">{{ fmtPct(result.current_margin_pct) }}</p>
				</div>
				<div
					class="rounded-xl p-3"
					:class="
						result.projected_margin_pct > result.current_margin_pct
							? 'bg-emerald-50 dark:bg-emerald-900/20'
							: 'bg-red-50 dark:bg-red-900/20'
					"
				>
					<p
						class="text-[10px] mb-1"
						:class="
							result.projected_margin_pct > result.current_margin_pct
								? 'text-emerald-500'
								: 'text-red-500'
						"
					>
						Projected Margin
					</p>
					<p
						class="text-base font-bold"
						:class="
							result.projected_margin_pct > result.current_margin_pct
								? 'text-emerald-700 dark:text-emerald-300'
								: 'text-red-700 dark:text-red-300'
						"
					>
						{{ fmtPct(result.projected_margin_pct) }}
					</p>
				</div>
			</div>

			<!-- Annual Projection -->
			<div class="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-3">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-[10px] text-gray-500 dark:text-gray-400">Annual Profit Projection</p>
						<p class="text-lg font-bold text-gray-900 dark:text-white">
							{{ fmtCurrency(result.annual_profit_projection) }}
						</p>
					</div>
					<div
						v-if="result.profit_change_pct !== undefined"
						class="text-right"
					>
						<p class="text-[10px] text-gray-400">Change</p>
						<p
							class="text-sm font-bold"
							:class="result.profit_change_pct >= 0 ? 'text-emerald-500' : 'text-red-500'"
						>
							{{ result.profit_change_pct >= 0 ? '+' : '' }}{{ result.profit_change_pct.toFixed(1) }}%
						</p>
					</div>
				</div>
			</div>

			<!-- Save as Recommendation -->
			<div class="flex justify-end">
				<button
					@click="createRecommendation"
					:disabled="saving"
					class="px-4 py-2 text-xs font-medium rounded-lg bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-50 transition-colors"
				>
					{{ saving ? 'Saving...' : 'Create Recommendation' }}
				</button>
			</div>
		</div>

		<!-- Placeholder -->
		<div v-if="!result && !simError" class="py-6 text-center">
			<span class="material-symbols-outlined !text-2xl text-gray-300 dark:text-gray-600">calculate</span>
			<p class="text-[10px] text-gray-400 mt-1">Enter an item code and price to simulate margin impact</p>
		</div>
	</div>
</template>

<script setup>
import { ref } from 'vue'
import { useProfitStore } from '@/stores/profit'
import { useFormatters } from '@/composables/useFormatters'

const store = useProfitStore()
const { formatCurrency, formatPercentage } = useFormatters()

const itemCode = ref('')
const newPrice = ref(null)
const simulating = ref(false)
const simError = ref(null)
const result = ref(null)
const saving = ref(false)

function fmtCurrency(v) {
	if (!v && v !== 0) return '$0.00'
	return formatCurrency(v)
}

function fmtPct(v) {
	if (!v && v !== 0) return '0%'
	return formatPercentage(v)
}

async function simulate() {
	if (!itemCode.value || !newPrice.value) return

	simulating.value = true
	simError.value = null
	result.value = null

	try {
		const res = await frappe.call({
			method: 'zevar_core.rag.tools.pricing_tools.simulate_price_change',
			args: {
				item_code: itemCode.value.trim(),
				new_price: newPrice.value,
			},
		})

		const data = res?.message || res
		if (data && data.error) {
			simError.value = data.error
		} else {
			result.value = data
		}
	} catch (err) {
		simError.value = err?.message || 'Simulation failed. Check item code and try again.'
	} finally {
		simulating.value = false
	}
}

async function createRecommendation() {
	if (!result.value) return

	saving.value = true
	try {
		await frappe.call({
			method: 'zevar_core.api.profit_intelligence.create_recommendation',
			args: {
				item_code: itemCode.value.trim(),
				new_price: newPrice.value,
				simulation_data: JSON.stringify(result.value),
			},
		})
		result.value = null
		itemCode.value = ''
		newPrice.value = null
		store.loadRecommendations()
	} catch (err) {
		simError.value = err?.message || 'Failed to create recommendation'
	} finally {
		saving.value = false
	}
}
</script>
