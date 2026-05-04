<template>
	<div
		class="py-3 border-b"
		:class="isDark ? 'border-white/5 bg-[#18181b]' : 'border-gray-200 bg-white'"
	>
		<div class="max-w-6xl mx-auto px-4 sm:px-6">
			<div class="flex items-center justify-between">
				<!-- Live Badge -->
				<div class="flex items-center gap-2 flex-shrink-0">
					<div
						class="flex items-center gap-1.5 px-2 py-1 rounded-md"
						:class="isOffline
							? (isDark ? 'bg-red-500/10' : 'bg-red-50')
							: (isDark ? 'bg-emerald-500/10' : 'bg-emerald-50')"
					>
						<span
							class="w-1.5 h-1.5 rounded-full"
							:class="isOffline ? 'bg-red-500' : 'bg-emerald-500 animate-pulse'"
						></span>
						<span
							class="text-[10px] font-semibold uppercase tracking-wide"
							:class="isOffline
								? 'text-red-600'
								: 'text-emerald-600'"
						>
							{{ isOffline ? 'Offline' : 'Live' }}
						</span>
					</div>
					<span
						class="text-[10px]"
						:class="isDark ? 'text-gray-500' : 'text-gray-400'"
						>{{ formattedTime }}</span
					>
				</div>

				<!-- Prices - Centered -->
				<div
					class="flex items-center justify-center gap-6 flex-1 overflow-x-auto scrollbar-hide"
				>
					<div
						v-for="metal in metals"
						:key="metal.symbol"
						class="flex items-center gap-2 flex-shrink-0"
					>
						<!-- Element Symbol Badge -->
						<div
							class="w-7 h-7 rounded-md flex items-center justify-center text-[10px] font-bold"
							:class="metal.badgeClass"
						>
							{{ metal.symbol }}
						</div>
						<!-- Price -->
						<div class="text-right">
							<div v-if="!isMetalSupported(metal)" class="flex items-center gap-1">
								<span class="text-xs font-semibold text-gray-400">N/A</span>
							</div>
							<div v-else-if="!hasValidPrice(metal)" class="flex items-center gap-1">
								<span class="text-xs font-semibold text-amber-500">--</span>
							</div>
							<div v-else class="flex items-center gap-1">
								<span
									class="text-xs font-semibold"
									:class="isDark ? 'text-gray-100' : 'text-gray-900'"
									>${{ formatPrice(metal.price) }}</span
								>
								<span
									class="text-[9px] font-medium"
									:style="{ color: metal.change >= 0 ? '#10b981' : '#ef4444' }"
								>
									{{ metal.change >= 0 ? '+' : ''
									}}{{ metal.change?.toFixed(2) }}%
								</span>
							</div>
							<span
								class="text-[9px]"
								:class="isDark ? 'text-gray-500' : 'text-gray-400'"
								>{{ metal.name }}</span
							>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { call } from 'frappe-ui'

const isDark = ref(true)
const isLoading = ref(true)
const isOffline = ref(false)
const lastSuccessfulFetch = ref(null)
let refreshInterval = null
let observer = null

onMounted(() => {
	isDark.value = document.documentElement.classList.contains('dark')
	observer = new MutationObserver(() => {
		isDark.value = document.documentElement.classList.contains('dark')
	})
	observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] })

	fetchPrices()
	refreshInterval = setInterval(fetchPrices, 60000)
})

onUnmounted(() => {
	if (observer) observer.disconnect()
	if (refreshInterval) clearInterval(refreshInterval)
})

const formattedTime = computed(() =>
	new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
)

function isMetalSupported(metal) {
	return metal.supported !== false
}

function hasValidPrice(metal) {
	return metal.price !== null && metal.price !== undefined
}

const metals = ref([
	{
		symbol: 'Au',
		name: 'Gold (XAU)',
		price: null,
		change: null,
		badgeClass: 'bg-gradient-to-br from-[#D4AF37] to-amber-600 text-black',
		supported: true, // This metal is provided by the live API
	},
	{
		symbol: 'Ag',
		name: 'Silver (XAG)',
		price: null,
		change: null,
		badgeClass: 'bg-gradient-to-br from-gray-300 to-gray-400 text-gray-700',
		supported: true,
		purity: '999 Fine', // Silver rate to use from the API
	},
	{
		symbol: 'Pt',
		name: 'Platinum',
		price: null,
		change: null,
		badgeClass: 'bg-gradient-to-br from-gray-100 to-gray-200 text-gray-700',
		supported: false, // Not available from Zevar live API
	},
	{
		symbol: 'Pd',
		name: 'Palladium',
		price: null,
		change: null,
		badgeClass: 'bg-gradient-to-br from-blue-200 to-blue-300 text-blue-800',
		supported: false,
	},
])

function formatPrice(price) {
	if (price === null || price === undefined) return '0.00'
	return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

async function fetchPrices() {
	try {
		const result = await call('zevar_core.api.pricing.get_live_metal_rates')
		const data = result?.rates || result?.message?.rates || result

		const TROY_OZ_GRAMS = 31.1035
		isOffline.value = false
		lastSuccessfulFetch.value = new Date()

		metals.value.forEach((metal) => {
			// Skip metals not provided by the Zevar API
			if (!metal.supported) return

			let metalKey = metal.name.includes('Gold') ? 'Yellow Gold' : metal.name.includes('Silver') ? 'Silver' : null
			if (!metalKey) return

			const metalRates = data[metalKey] || data.rates?.[metalKey]
			if (metalRates && metalRates.length > 0) {
				const rate24k = metal.purity === '999 Fine'
					? metalRates.find((r) => r.purity === '999 Fine')
					: metalRates.find((r) => r.purity === '24Kt')
				if (rate24k) {
					const spotPrice = rate24k.rate_per_gram * TROY_OZ_GRAMS
					metal.price = spotPrice
					// Use server-side trend data if available, else compute client-side
					metal.change = rate24k.change_pct !== undefined ? rate24k.change_pct : 0
				}
			}
		})
	} catch (err) {
		// API unreachable — show offline state, do NOT fake data
		isOffline.value = true
		// Keep previous prices intact (don't mutate)
	} finally {
		isLoading.value = false
	}
}
</script>

<style scoped>
.scrollbar-hide {
	-ms-overflow-style: none;
	scrollbar-width: none;
}
.scrollbar-hide::-webkit-scrollbar {
	display: none;
}
</style>
