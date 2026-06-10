<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<h2 class="premium-title !text-xl sm:!text-2xl">Appraisals</h2>
				<div class="flex items-center gap-2">
					<select
						v-model="statusFilter"
						@change="loadData"
						class="px-3 py-1.5 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-xs"
					>
						<option value="">All Statuses</option>
						<option value="Draft">Draft</option>
						<option value="Completed">Completed</option>
						<option value="Expired">Expired</option>
					</select>
					<select
						v-model="expiryFilter"
						@change="loadData"
						class="px-3 py-1.5 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-xs"
					>
						<option value="">All Expiry</option>
						<option value="30">Expiring in 30 days</option>
						<option value="60">Expiring in 60 days</option>
						<option value="90">Expiring in 90 days</option>
						<option value="expired">Already Expired</option>
					</select>
					<button
						@click="createNew"
						class="px-3 py-1.5 bg-primary-600 text-white rounded-lg text-xs font-semibold hover:bg-primary-700 transition-colors"
					>
						+ New Appraisal
					</button>
				</div>
			</div>

			<!-- Summary Strip -->
			<div class="grid grid-cols-4 gap-3 mb-6">
				<div
					class="bg-white dark:bg-warm-dark-800 border border-gray-200 dark:border-warm-border rounded-xl p-4"
				>
					<div class="text-xs text-gray-500 mb-1">Total Active</div>
					<div class="text-2xl font-bold text-gray-900 dark:text-white">
						{{ summary.active }}
					</div>
				</div>
				<div class="bg-white dark:bg-warm-dark-800 border border-amber-200 rounded-xl p-4">
					<div class="text-xs text-amber-600 mb-1">Expiring Soon (30d)</div>
					<div class="text-2xl font-bold text-amber-600">{{ summary.expiring30 }}</div>
				</div>
				<div class="bg-white dark:bg-warm-dark-800 border border-red-200 rounded-xl p-4">
					<div class="text-xs text-red-500 mb-1">Expired</div>
					<div class="text-2xl font-bold text-red-600">{{ summary.expired }}</div>
				</div>
				<div class="bg-white dark:bg-warm-dark-800 border border-green-200 rounded-xl p-4">
					<div class="text-xs text-green-500 mb-1">Total Value</div>
					<div class="text-2xl font-bold text-green-600">
						${{ formatCurrency(summary.totalValue) }}
					</div>
				</div>
			</div>

			<!-- Appraisals Table -->
			<div
				class="flex-1 bg-white dark:bg-warm-dark-800 border border-gray-200 dark:border-warm-border rounded-xl overflow-auto"
			>
				<table class="w-full text-sm">
					<thead>
						<tr class="bg-gray-50 dark:bg-warm-dark-900 sticky top-0">
							<th
								class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
							>
								Appraisal #
							</th>
							<th
								class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
							>
								Customer
							</th>
							<th
								class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
							>
								Item
							</th>
							<th
								class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
							>
								Type
							</th>
							<th
								class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase"
							>
								Value
							</th>
							<th
								class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
							>
								Date
							</th>
							<th
								class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
							>
								Valid Until
							</th>
							<th
								class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
							>
								Status
							</th>
							<th
								class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
							>
								Cert #
							</th>
							<th
								class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase"
							>
								Actions
							</th>
						</tr>
					</thead>
					<tbody>
						<tr
							v-for="a in appraisals"
							:key="a.name"
							class="border-t border-gray-100 dark:border-warm-border hover:bg-gray-50 dark:hover:bg-warm-dark-700"
						>
							<td class="px-4 py-3 font-mono text-xs text-primary-600">
								<a
									:href="`/app/jewelry-appraisal/${a.name}`"
									class="hover:underline"
									>{{ a.name }}</a
								>
							</td>
							<td class="px-4 py-3">{{ a.customer_name || a.customer }}</td>
							<td class="px-4 py-3 text-xs">{{ a.item_description }}</td>
							<td class="px-4 py-3">
								<span
									class="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs"
									>{{ a.item_type }}</span
								>
							</td>
							<td class="px-4 py-3 text-right font-semibold">
								${{ formatCurrency(a.appraised_value) }}
							</td>
							<td class="px-4 py-3 text-xs text-gray-500">
								{{ formatDate(a.appraisal_date) }}
							</td>
							<td
								class="px-4 py-3 text-xs"
								:class="
									isExpiringSoon(a.valid_until)
										? 'text-amber-600 font-semibold'
										: isExpired(a.valid_until)
										? 'text-red-600 font-semibold'
										: 'text-gray-500'
								"
							>
								{{ formatDate(a.valid_until) || '—' }}
							</td>
							<td class="px-4 py-3">
								<span
									:class="appraisalStatusClass(a.status)"
									class="px-2 py-0.5 rounded-full text-xs font-medium"
									>{{ a.status }}</span
								>
							</td>
							<td class="px-4 py-3 font-mono text-xs">
								{{ a.certificate_number || '—' }}
							</td>
							<td class="px-4 py-3 text-right">
								<button
									@click="reappraise(a)"
									class="text-xs text-primary-600 hover:underline mr-2"
								>
									Re-appraise
								</button>
								<button
									@click="printCert(a)"
									class="text-xs text-gray-500 hover:underline"
								>
									🖨
								</button>
							</td>
						</tr>
						<tr v-if="!appraisals.length">
							<td colspan="10" class="px-4 py-12 text-center text-gray-400">
								No appraisals found
							</td>
						</tr>
					</tbody>
				</table>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'

const statusFilter = ref('')
const expiryFilter = ref('')
const appraisals = ref([])
const summary = ref({ active: 0, expiring30: 0, expired: 0, totalValue: 0 })

function formatCurrency(v) {
	return new Intl.NumberFormat('en-US', {
		minimumFractionDigits: 0,
		maximumFractionDigits: 0,
	}).format(v || 0)
}

function formatDate(d) {
	if (!d) return ''
	return new Date(d).toLocaleDateString('en-US', {
		month: 'short',
		day: 'numeric',
		year: 'numeric',
	})
}

function isExpiringSoon(d) {
	if (!d) return false
	const diff = (new Date(d) - new Date()) / (1000 * 60 * 60 * 24)
	return diff > 0 && diff <= 30
}

function isExpired(d) {
	if (!d) return false
	return new Date(d) < new Date()
}

function appraisalStatusClass(s) {
	const map = {
		Draft: 'bg-gray-100 text-gray-600',
		Completed: 'bg-green-100 text-green-700',
		Expired: 'bg-red-100 text-red-700',
		Cancelled: 'bg-gray-100 text-gray-400',
	}
	return map[s] || 'bg-gray-100 text-gray-600'
}

async function loadData() {
	try {
		const res = await frappe.call({
			method: 'zevar_core.api.inventory_v2.list_expiring_appraisals',
			args: { days_ahead: parseInt(expiryFilter.value) || 90 },
		})
		appraisals.value = res?.message || []
	} catch (e) {
		console.error('Failed to load appraisals:', e)
	}
}

function createNew() {
	window.location.href = '/app/jewelry-appraisal/new'
}
function reappraise(a) {
	/* TODO: navigate to new appraisal with replacement_for = a.name */
}
function printCert(a) {
	/* TODO: open print format */
}

onMounted(loadData)
</script>
