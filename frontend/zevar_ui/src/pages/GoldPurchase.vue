<template>
	<div class="h-full flex flex-col">
		<div class="flex items-center justify-between px-4 py-3 border-b dark:border-warm-dark-600">
			<div class="flex items-center gap-3">
				<div class="p-2 bg-amber-100 dark:bg-amber-900/30 rounded-lg">
					<svg class="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
						/>
					</svg>
				</div>
				<div>
					<h1 class="text-lg font-bold text-gray-900 dark:text-white">Gold Scrap Purchase</h1>
					<p class="text-xs text-gray-500">Buy scrap gold from customers at live market rates</p>
				</div>
			</div>
			<button
				@click="showPurchaseModal = true"
				class="px-4 py-2 bg-amber-600 text-white rounded-lg text-sm font-medium hover:bg-amber-700"
			>
				+ New Purchase
			</button>
		</div>

		<!-- Purchases List -->
		<div class="flex-1 overflow-y-auto p-4">
			<div v-if="loading" class="text-center py-8 text-gray-400">Loading...</div>
			<div v-else-if="purchases.length === 0" class="text-center py-8">
				<p class="text-gray-400">No gold purchases yet</p>
				<button
					@click="showPurchaseModal = true"
					class="mt-2 text-amber-600 text-sm font-medium hover:underline"
				>
					Create first purchase
				</button>
			</div>
			<div v-else class="space-y-2">
				<div
					v-for="p in purchases"
					:key="p.name"
					class="border rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-warm-dark-700 cursor-pointer"
					@click="viewPurchase(p.name)"
				>
					<div class="flex justify-between">
						<div>
							<span class="font-mono text-sm text-amber-600">{{ p.name }}</span>
							<span class="text-gray-400 text-xs ml-2">{{ formatDate(p.purchase_date) }}</span>
						</div>
						<div class="text-right">
							<div class="font-bold text-amber-600">{{ fmtCurrency(p.total_agreed_value) }}</div>
							<div class="text-xs text-gray-400">{{ p.customer_name }}</div>
						</div>
					</div>
					<div class="flex gap-2 mt-1">
						<span
							class="px-2 py-0.5 text-xs rounded-full"
							:class="p.status === 'Submitted' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'"
						>
							{{ p.status }}
						</span>
						<span
							class="px-2 py-0.5 text-xs rounded-full"
							:class="p.payment_status === 'Paid' ? 'bg-blue-100 text-blue-700' : 'bg-yellow-100 text-yellow-700'"
						>
							{{ p.payment_status }}
						</span>
						<span class="text-xs text-gray-400">{{ p.payment_method }}</span>
					</div>
				</div>
			</div>
		</div>

		<!-- Purchase Modal -->
		<GoldPurchaseModal
			v-if="showPurchaseModal"
			@close="showPurchaseModal = false"
			@completed="onPurchaseCompleted"
		/>
	</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { call, toast } from 'frappe-ui'
import GoldPurchaseModal from '../components/GoldPurchaseModal.vue'

const purchases = ref([])
const loading = ref(true)
const showPurchaseModal = ref(false)

async function loadPurchases() {
	loading.value = true
	try {
		purchases.value = await call('zevar_core.api.gold_purchase.get_gold_purchases_list', {
			limit: 50,
		})
	} catch (e) {
		toast({ title: 'Error loading purchases', message: String(e), intent: 'error' })
	} finally {
		loading.value = false
	}
}

function onPurchaseCompleted() {
	showPurchaseModal.value = false
	loadPurchases()
}

function viewPurchase(name) {
	// Future: open detail view
	toast({ title: name, message: 'Purchase detail view coming soon', intent: 'info' })
}

function formatDate(dt) {
	if (!dt) return ''
	return new Date(dt).toLocaleDateString('en-US', {
		month: 'short',
		day: 'numeric',
		year: 'numeric',
		hour: '2-digit',
		minute: '2-digit',
	})
}

function fmtCurrency(val) {
	return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val || 0)
}

onMounted(loadPurchases)
</script>
