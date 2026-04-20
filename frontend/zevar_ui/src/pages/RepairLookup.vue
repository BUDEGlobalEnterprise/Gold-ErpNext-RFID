<template>
	<div
		class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800"
	>
		<!-- Header -->
		<header class="bg-white dark:bg-gray-900 shadow-sm">
			<div class="max-w-4xl mx-auto px-4 py-6">
				<div class="flex items-center gap-4">
					<h1 class="text-2xl font-bold text-[#D4AF37]">ZEVAR JEWELERS</h1>
					<span class="text-gray-400">|</span>
					<span class="text-gray-600 dark:text-gray-400">Repair Status Lookup</span>
				</div>
			</div>
		</header>

		<!-- Main Content -->
		<main class="max-w-4xl mx-auto px-4 py-8">
			<!-- Search Section -->
			<div class="bg-white dark:bg-gray-900 rounded-2xl shadow-xl p-6 mb-8">
				<h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">
					Check Your Repair Status
				</h2>
				<p class="text-gray-600 dark:text-gray-400 mb-6">
					Enter your repair number or phone number to check the status of your repair.
				</p>

				<form @submit.prevent="search" class="flex gap-3">
					<div class="flex-1 relative">
						<svg
							class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
							/>
						</svg>
						<input
							v-model="searchQuery"
							type="text"
							placeholder="Enter Repair # (e.g., RPR-2026-00001) or Phone Number"
							class="w-full pl-10 pr-4 py-3 border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800 text-lg focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent"
						/>
					</div>
					<button
						type="submit"
						:disabled="searching || !searchQuery"
						class="px-6 py-3 bg-[#D4AF37] text-black rounded-lg font-bold hover:bg-[#c9a432] disabled:opacity-50 disabled:cursor-not-allowed"
					>
						{{ searching ? 'Searching...' : 'Search' }}
					</button>
				</form>
			</div>

			<!-- Results Section -->
			<div
				v-if="searchResult"
				class="bg-white dark:bg-gray-900 rounded-2xl shadow-xl overflow-hidden"
			>
				<!-- Status Header -->
				<div class="p-6" :class="getStatusHeaderClass(searchResult.status)">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-sm font-medium opacity-80">
								Repair {{ searchResult.name }}
							</p>
							<h3 class="text-3xl font-bold mt-1">{{ searchResult.status }}</h3>
						</div>
						<div class="text-right">
							<p v-if="searchResult.promised_date" class="text-sm opacity-80">
								Expected By
							</p>
							<p v-if="searchResult.promised_date" class="text-xl font-bold">
								{{ formatDate(searchResult.promised_date) }}
							</p>
						</div>
					</div>
				</div>

				<!-- Progress Bar -->
				<div class="px-6 py-4 bg-gray-50 dark:bg-gray-800">
					<div class="flex justify-between mb-2">
						<span
							v-for="step in progressSteps"
							:key="step.status"
							class="text-xs font-medium"
							:class="getStepClass(step.status)"
						>
							{{ step.label }}
						</span>
					</div>
					<div class="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
						<div
							class="h-full bg-[#D4AF37] transition-all duration-500"
							:style="{ width: progressPercent + '%' }"
						></div>
					</div>
				</div>

				<!-- Details -->
				<div class="p-6 space-y-4">
					<div class="grid grid-cols-2 gap-4">
						<div>
							<p class="text-xs text-gray-500 uppercase">Repair Type</p>
							<p class="font-medium">
								{{ searchResult.repair_type_name || searchResult.repair_type }}
							</p>
						</div>
						<div>
							<p class="text-xs text-gray-500 uppercase">Item</p>
							<p class="font-medium">{{ searchResult.item_type || 'Various' }}</p>
						</div>
						<div>
							<p class="text-xs text-gray-500 uppercase">Estimated Cost</p>
							<p class="font-medium">
								${{ formatNum(searchResult.estimated_cost) }}
							</p>
						</div>
						<div>
							<p class="text-xs text-gray-500 uppercase">Received</p>
							<p class="font-medium">{{ formatDate(searchResult.received_date) }}</p>
						</div>
					</div>

					<!-- Estimate Action -->
					<div
						v-if="searchResult.estimate_status === 'Sent'"
						class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4 border border-yellow-100"
					>
						<p class="font-medium text-yellow-800 dark:text-yellow-300">
							Estimate Pending Approval
						</p>
						<p class="text-sm text-yellow-700 dark:text-yellow-400 mt-1">
							Please approve or reject the estimate for your repair.
						</p>
						<div class="flex gap-2 mt-3">
							<a
								:href="estimateApprovalUrl"
								target="_blank"
								class="px-4 py-2 bg-green-500 text-white rounded-lg text-sm font-medium hover:bg-green-600"
							>
								Review & Approve
							</a>
						</div>
					</div>

					<!-- Ready for Pickup -->
					<div
						v-if="searchResult.status === 'Ready for Pickup'"
						class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 border border-green-100"
					>
						<p class="font-medium text-green-800 dark:text-green-300">
							Your Repair is Ready!
						</p>
						<p class="text-sm text-green-700 dark:text-green-400 mt-1">
							Please visit us to pick up your item.
						</p>
						<div v-if="searchResult.balance_due > 0" class="mt-3 p-2 bg-white rounded">
							<p class="text-sm">
								Balance Due:
								<span class="font-bold text-green-600"
									>${{ formatNum(searchResult.balance_due) }}</span
								>
							</p>
						</div>
					</div>

					<!-- Contact Info -->
					<div class="pt-4 border-t border-gray-100 dark:border-gray-800">
						<p class="text-sm text-gray-500">
							Need help? Call us at
							<a href="tel:+15551234567" class="text-[#D4AF37] font-medium"
								>(555) 123-4567</a
							>
						</p>
					</div>
				</div>
			</div>

			<!-- No Results -->
			<div
				v-else-if="searched && !searchResult"
				class="bg-white dark:bg-gray-900 rounded-2xl shadow-xl p-8 text-center"
			>
				<svg
					class="w-16 h-16 text-gray-300 mx-auto mb-4"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="1.5"
						d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
					/>
				</svg>
				<h3 class="text-lg font-bold text-gray-900 dark:text-white mb-2">
					No Repair Found
				</h3>
				<p class="text-gray-600 dark:text-gray-400 mb-4">
					We couldn't find a repair matching that information. Please check your repair
					number or phone number and try again.
				</p>
				<button
					@click="resetSearch"
					class="px-4 py-2 bg-gray-100 dark:bg-gray-800 rounded-lg text-sm font-medium hover:bg-gray-200"
				>
					Search Again
				</button>
			</div>

			<!-- Instructions -->
			<div v-if="!searched" class="mt-8 text-center text-sm text-gray-500">
				<p>
					This is a self-service lookup tool. You can check the status of your repair
					anytime.
				</p>
				<p class="mt-1">For immediate assistance, please call our store.</p>
			</div>
		</main>
	</div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { call } from 'frappe-ui'

const searchQuery = ref('')
const searching = ref(false)
const searched = ref(false)
const searchResult = ref(null)

// Check for hash on mount for QR code navigation
const hash = window.location.hash.slice(1)
if (hash) {
	searchQuery.value = hash
	search()
}

const progressSteps = [
	{ status: 'Received', label: 'Received' },
	{ status: 'Estimated', label: 'Estimated' },
	{ status: 'Approved', label: 'Approved' },
	{ status: 'In Progress', label: 'In Progress' },
	{ status: 'Waiting for Parts', label: 'Parts' },
	{ status: 'Quality Check', label: 'Quality Check' },
	{ status: 'Ready for Pickup', label: 'Ready' },
	{ status: 'Delivered', label: 'Delivered' },
]

const progressPercent = computed(() => {
	if (!searchResult.value) return 0
	const idx = progressSteps.findIndex((s) => s.status === searchResult.value.status)
	return idx >= 0 ? ((idx + 1) / progressSteps.length) * 100 : 0
})

const estimateApprovalUrl = computed(() => {
	if (!searchResult.value) return '#'
	return `${window.location.origin}/pos/repair-lookup/${searchResult.value.estimate_token}`
})

async function search() {
	if (!searchQuery.value.trim()) return

	searching.value = true
	searched.value = false

	try {
		// Try as repair number first, then phone
		let result
		if (searchQuery.value.match(/^RPR-/i)) {
			result = await call('zevar_core.api.lookup_repair_by_number', {
				repair_number: searchQuery.value,
			})
		} else {
			result = await call('zevar_core.api.lookup_repair_by_phone', {
				phone: searchQuery.value,
			})
		}

		searchResult.value = result
		searched.value = true
	} catch (e) {
		searchResult.value = null
		searched.value = true
	} finally {
		searching.value = false
	}
}

function resetSearch() {
	searchQuery.value = ''
	searched.value = false
}

function formatNum(n) {
	return n ? Number(n).toFixed(2) : '0.00'
}
function formatDate(d) {
	return d
		? new Date(d).toLocaleDateString('en-US', {
				month: 'short',
				day: 'numeric',
				year: 'numeric',
		  })
		: ''
}

function getStatusHeaderClass(status) {
	const classes = {
		Received: 'bg-blue-100 text-blue-900',
		Estimated: 'bg-yellow-100 text-yellow-900',
		Approved: 'bg-indigo-100 text-indigo-900',
		'In Progress': 'bg-orange-100 text-orange-900',
		'Waiting for Parts': 'bg-purple-100 text-purple-900',
		'Quality Check': 'bg-cyan-100 text-cyan-900',
		'Ready for Pickup': 'bg-green-100 text-green-900',
		Delivered: 'bg-gray-100 text-gray-900',
		Cancelled: 'bg-red-100 text-red-900',
	}
	return classes[status] || 'bg-gray-100 text-gray-900'
}

function getStepClass(stepStatus) {
	if (!searchResult.value) return 'text-gray-400'
	const currentIdx = progressSteps.findIndex((s) => s.status === searchResult.value.status)
	const stepIdx = progressSteps.findIndex((s) => s.status === stepStatus)

	if (stepIdx < currentIdx) return 'text-green-600'
	if (stepIdx === currentIdx) return 'text-[#D4AF37] font-bold'
	return 'text-gray-400'
}
</script>
