<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<h2 class="premium-title !text-xl sm:!text-2xl">Appraisal Reminders</h2>
				<div class="flex items-center gap-2">
					<select v-model="daysWindow" @change="loadData" class="px-3 py-1.5 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-xs text-gray-900 dark:text-white">
						<option value="30">30 days</option>
						<option value="60">60 days</option>
						<option value="90">90 days</option>
						<option value="180">180 days</option>
					</select>
					<button @click="loadData" class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-warm-dark-700" title="Refresh">
						<svg class="w-4 h-4 text-gray-500" :class="{ 'animate-spin': store.expiringAppraisalsResource.loading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357 2m15.357 2H15" />
						</svg>
					</button>
				</div>
			</div>

			<!-- Summary -->
			<div v-if="store.expiringAppraisals.length" class="mb-4 px-4 py-2 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
				<span class="text-xs font-semibold text-yellow-800 dark:text-yellow-300">
					{{ store.expiringAppraisals.length }} appraisals expiring within {{ daysWindow }} days
				</span>
			</div>

			<!-- Appraisals List -->
			<div class="flex-1 overflow-auto space-y-2">
				<div v-for="a in store.expiringAppraisals" :key="a.name"
					class="bg-white dark:bg-warm-dark-800 border border-gray-200 dark:border-warm-border rounded-xl p-4">
					<div class="flex items-center justify-between">
						<div class="flex items-center gap-3">
							<div>
								<div class="text-sm font-semibold text-gray-900 dark:text-white">{{ a.item_code }}</div>
								<div class="text-xs text-gray-500">
									<span v-if="a.serial_no">Serial: {{ a.serial_no }} &middot; </span>
									<span v-if="a.customer">Customer: {{ a.customer }}</span>
								</div>
							</div>
						</div>
						<div class="text-right">
							<div class="text-sm font-bold text-gray-900 dark:text-white">${{ a.appraised_value }}</div>
							<div class="text-xs" :class="urgencyClass(a.valid_until)">
								Expires: {{ a.valid_until }}
							</div>
						</div>
					</div>
				</div>
			</div>

			<div v-if="!store.expiringAppraisals.length && !store.expiringAppraisalsResource.loading" class="text-center text-gray-400 text-sm py-12">
				No expiring appraisals in this window.
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '../../components/AppLayout.vue'
import { useInventoryV2Store } from '../../stores/inventoryV2'
import { useFormatters } from '../../composables/useFormatters'

const store = useInventoryV2Store()
const { formatDate } = useFormatters()

const daysWindow = ref('90')

function loadData() {
	store.loadExpiringAppraisals(parseInt(daysWindow.value))
}

function urgencyClass(validUntil) {
	if (!validUntil) return 'text-gray-400'
	const daysLeft = Math.floor((new Date(validUntil) - new Date()) / (1000 * 60 * 60 * 24))
	if (daysLeft <= 7) return 'text-red-600 font-bold'
	if (daysLeft <= 30) return 'text-yellow-600 font-semibold'
	return 'text-gray-500'
}

onMounted(() => loadData())
</script>
