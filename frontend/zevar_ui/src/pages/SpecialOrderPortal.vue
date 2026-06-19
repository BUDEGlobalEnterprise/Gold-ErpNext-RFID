<template>
	<div class="min-h-[100dvh] bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
		<!-- Header -->
		<header class="bg-white dark:bg-warm-dark-900 shadow-sm sticky top-0 z-50">
			<div class="max-w-6xl mx-auto px-4 py-4">
				<div class="flex items-center justify-between">
					<div class="flex items-center gap-3">
						<h1 class="text-xl font-bold text-[#D4AF37]">ZEVAR JEWELERS</h1>
						<span class="text-gray-400">|</span>
						<span class="text-gray-600 dark:text-gray-400 hidden sm:inline">Order Tracker</span>
					</div>
				</div>
			</div>
		</header>

		<!-- Main Content -->
		<main class="max-w-md mx-auto px-4 py-12">
			<div class="bg-white dark:bg-warm-dark-900 rounded-2xl shadow-xl p-8">
				<div class="text-center mb-8">
					<div class="w-16 h-16 bg-[#D4AF37]/10 rounded-full flex items-center justify-center mx-auto mb-4">
						<svg class="w-8 h-8 text-[#D4AF37]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
						</svg>
					</div>
					<h2 class="text-2xl font-bold text-gray-900 dark:text-white">Track Your Order</h2>
					<p class="text-gray-600 dark:text-gray-400 mt-2">Enter your Special Order ID to check its current status.</p>
				</div>

				<!-- Lookup Form -->
				<form @submit.prevent="trackOrder" v-if="!orderDetails">
					<div class="space-y-4">
						<div>
							<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Order ID</label>
							<input
								v-model="orderId"
								type="text"
								placeholder="e.g. SPO-0001"
								class="w-full px-4 py-3 border border-gray-200 dark:border-warm-border rounded-lg bg-gray-50 dark:bg-warm-dark-900 focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent uppercase"
							/>
						</div>
						<button
							type="submit"
							:disabled="loading || !orderId"
							class="w-full py-3 bg-[#D4AF37] text-[#1E2022] rounded-lg font-bold hover:bg-[#c9a432] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
						>
							{{ loading ? 'Searching...' : 'Track Order' }}
						</button>
					</div>
					
					<div v-if="error" class="mt-4 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-100 dark:border-red-800">
						<p class="text-sm text-red-800 dark:text-red-300 text-center">{{ error }}</p>
					</div>
				</form>

				<!-- Results -->
				<div v-if="orderDetails" class="space-y-6">
					<div class="p-4 bg-gray-50 dark:bg-warm-dark-800 rounded-xl border border-gray-100 dark:border-warm-border text-center">
						<p class="text-xs text-gray-500 uppercase tracking-widest mb-1">Status</p>
						<span class="inline-block px-4 py-1.5 rounded-full text-sm font-bold bg-[#D4AF37]/20 text-[#D4AF37]">
							{{ orderDetails.workflow_status }}
						</span>
					</div>
					
					<div class="space-y-3">
						<div class="flex justify-between py-2 border-b border-gray-100 dark:border-warm-border/50">
							<span class="text-gray-500 text-sm">Order ID</span>
							<span class="font-medium text-gray-900 dark:text-white">{{ orderDetails.order_id }}</span>
						</div>
						<div class="flex justify-between py-2 border-b border-gray-100 dark:border-warm-border/50">
							<span class="text-gray-500 text-sm">Customer</span>
							<span class="font-medium text-gray-900 dark:text-white">{{ orderDetails.customer_name }}</span>
						</div>
						<div class="flex justify-between py-2 border-b border-gray-100 dark:border-warm-border/50">
							<span class="text-gray-500 text-sm">Metal</span>
							<span class="font-medium text-gray-900 dark:text-white">{{ orderDetails.metal_type || 'Custom' }}</span>
						</div>
						<div class="flex justify-between py-2 border-b border-gray-100 dark:border-warm-border/50">
							<span class="text-gray-500 text-sm">Created</span>
							<span class="font-medium text-gray-900 dark:text-white">{{ formatDate(orderDetails.creation) }}</span>
						</div>
					</div>

					<button
						@click="resetSearch"
						class="w-full py-2.5 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 text-sm font-medium transition-colors"
					>
						Track Another Order
					</button>
				</div>
			</div>
		</main>
	</div>
</template>

<script setup>
import { ref } from 'vue'
import { call } from 'frappe-ui'

const orderId = ref('')
const loading = ref(false)
const error = ref('')
const orderDetails = ref(null)

async function trackOrder() {
	if (!orderId.value.trim()) return
	
	loading.value = true
	error.value = ''
	
	try {
		const result = await call('zevar_core.api.special_order.track_special_order', {
			order_id: orderId.value.trim().toUpperCase()
		})
		
		if (result.error) {
			error.value = result.error
		} else {
			orderDetails.value = result
		}
	} catch (e) {
		error.value = e.message || 'Failed to track order. Please try again.'
	} finally {
		loading.value = false
	}
}

function resetSearch() {
	orderDetails.value = null
	orderId.value = ''
	error.value = ''
}

function formatDate(dateString) {
	if (!dateString) return 'N/A'
	const d = new Date(dateString)
	return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}
</script>
