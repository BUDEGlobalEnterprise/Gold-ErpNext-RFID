<template>
	<div class="premium-card !p-5">
		<div class="flex items-center justify-between mb-4">
			<h3 class="text-sm font-bold text-gray-900 dark:text-white">Pricing Recommendations</h3>
			<div class="flex items-center gap-2">
				<select
					v-model="statusFilter"
					@change="loadFiltered"
					class="px-2 py-1 text-[10px] border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
				>
					<option value="Pending Review">Pending Review</option>
					<option value="Approved">Approved</option>
					<option value="Rejected">Rejected</option>
					<option value="">All</option>
				</select>
				<span class="text-[10px] text-gray-400">{{ recommendations.length }} items</span>
			</div>
		</div>

		<!-- Table -->
		<div v-if="recommendations.length" class="overflow-x-auto">
			<table class="w-full text-[10px] border-collapse min-w-[700px]">
				<thead>
					<tr class="border-b border-gray-200 dark:border-gray-700">
						<th class="text-left p-2 font-bold text-gray-500 dark:text-gray-400">Item</th>
						<th class="text-left p-2 font-bold text-gray-500 dark:text-gray-400">Type</th>
						<th class="text-right p-2 font-bold text-gray-500 dark:text-gray-400">Current</th>
						<th class="text-right p-2 font-bold text-gray-500 dark:text-gray-400">Recommended</th>
						<th class="text-right p-2 font-bold text-gray-500 dark:text-gray-400">Change</th>
						<th class="text-center p-2 font-bold text-gray-500 dark:text-gray-400">Confidence</th>
						<th class="text-center p-2 font-bold text-gray-500 dark:text-gray-400">Actions</th>
					</tr>
				</thead>
				<tbody>
					<tr
						v-for="rec in recommendations"
						:key="rec.name"
						class="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50"
					>
						<td class="p-2">
							<p class="font-medium text-gray-900 dark:text-white truncate max-w-[150px]">
								{{ rec.item_name || rec.item_code }}
							</p>
							<p v-if="rec.item_name" class="text-gray-400 truncate max-w-[150px]">{{ rec.item_code }}</p>
						</td>
						<td class="p-2">
							<span
								class="inline-block px-1.5 py-0.5 rounded text-[8px] font-bold"
								:class="typeBadgeClass(rec.recommendation_type)"
							>
								{{ rec.recommendation_type || 'Price' }}
							</span>
						</td>
						<td class="p-2 text-right text-gray-900 dark:text-white font-medium">
							{{ fmtCurrency(rec.current_price) }}
						</td>
						<td class="p-2 text-right text-gray-900 dark:text-white font-bold">
							{{ fmtCurrency(rec.recommended_price) }}
						</td>
						<td class="p-2 text-right">
							<span
								:class="changePercent(rec) >= 0 ? 'text-emerald-500' : 'text-red-500'"
								class="font-bold"
							>
								{{ changePercent(rec) >= 0 ? '+' : '' }}{{ changePercent(rec).toFixed(1) }}%
							</span>
						</td>
						<td class="p-2 text-center">
							<div class="flex items-center justify-center gap-1">
								<div class="w-12 bg-gray-200 dark:bg-gray-700 rounded-full h-1.5 overflow-hidden">
									<div
										class="h-full rounded-full"
										:class="confidenceColor(rec.confidence)"
										:style="{ width: (rec.confidence || 0) + '%' }"
									></div>
								</div>
								<span class="text-gray-500 dark:text-gray-400">{{ (rec.confidence || 0).toFixed(0) }}%</span>
							</div>
						</td>
						<td class="p-2">
							<div v-if="rec.status === 'Pending Review'" class="flex items-center justify-center gap-1">
								<button
									@click="handleReview(rec.name, 'Approved')"
									:disabled="reviewing === rec.name"
									class="px-2 py-1 rounded text-[8px] font-bold bg-emerald-500 text-white hover:bg-emerald-600 disabled:opacity-50 transition-colors"
								>
									Approve
								</button>
								<button
									@click="handleReject(rec.name)"
									:disabled="reviewing === rec.name"
									class="px-2 py-1 rounded text-[8px] font-bold bg-red-500 text-white hover:bg-red-600 disabled:opacity-50 transition-colors"
								>
									Reject
								</button>
							</div>
							<span v-else :class="statusClass(rec.status)" class="text-[9px] font-medium">
								{{ rec.status }}
							</span>
						</td>
					</tr>
				</tbody>
			</table>
		</div>

		<!-- Empty -->
		<div v-else class="py-8 text-center">
			<span class="material-symbols-outlined !text-3xl text-gray-300 dark:text-gray-600">price_check</span>
			<p class="text-xs text-gray-400 mt-2">No pricing recommendations found</p>
		</div>

		<!-- Reject Notes Modal -->
		<div
			v-if="rejectingName"
			class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4"
			@click.self="rejectingName = null"
		>
			<div class="bg-white dark:bg-gray-900 rounded-xl p-5 w-full max-w-md space-y-3 shadow-2xl">
				<h4 class="text-sm font-bold text-gray-900 dark:text-white">Reject Recommendation</h4>
				<textarea
					v-model="rejectNotes"
					rows="3"
					placeholder="Optional reason for rejection..."
					class="w-full px-3 py-2 text-xs border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-1 focus:ring-indigo-400 resize-none"
				></textarea>
				<div class="flex justify-end gap-2">
					<button
						@click="rejectingName = null"
						class="px-3 py-1.5 text-xs text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100"
					>
						Cancel
					</button>
					<button
						@click="confirmReject"
						class="px-3 py-1.5 text-xs font-medium rounded-lg bg-red-600 text-white hover:bg-red-700 transition-colors"
					>
						Confirm Reject
					</button>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useProfitStore } from '@/stores/profit'
import { useFormatters } from '@/composables/useFormatters'

const store = useProfitStore()
const { formatCurrency } = useFormatters()

const statusFilter = ref('Pending Review')
const reviewing = ref(null)
const rejectingName = ref(null)
const rejectNotes = ref('')

const recommendations = computed(() => store.recommendations || [])

function fmtCurrency(v) {
	if (!v && v !== 0) return '$0.00'
	return formatCurrency(v)
}

function changePercent(rec) {
	if (!rec.current_price || rec.current_price === 0) return 0
	return ((rec.recommended_price - rec.current_price) / rec.current_price) * 100
}

function typeBadgeClass(type) {
	const t = (type || '').toLowerCase()
	if (t.includes('increase')) return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
	if (t.includes('decrease')) return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
	return 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
}

function confidenceColor(c) {
	if (!c) return 'bg-gray-400'
	if (c >= 80) return 'bg-emerald-500'
	if (c >= 60) return 'bg-amber-500'
	return 'bg-red-500'
}

function statusClass(status) {
	if (status === 'Approved') return 'text-emerald-500'
	if (status === 'Rejected') return 'text-red-500'
	return 'text-amber-500'
}

async function handleReview(name, action) {
	reviewing.value = name
	await store.reviewRecommendation(name, action)
	reviewing.value = null
}

function handleReject(name) {
	rejectingName.value = name
	rejectNotes.value = ''
}

async function confirmReject() {
	await store.reviewRecommendation(rejectingName.value, 'Rejected', rejectNotes.value)
	rejectingName.value = null
	rejectNotes.value = ''
}

function loadFiltered() {
	store.loadRecommendations(statusFilter.value || undefined)
}
</script>
