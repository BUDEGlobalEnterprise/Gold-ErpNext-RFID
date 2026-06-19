<template>
	<!-- ── Flex container: pinned header + scrollable body + pinned footer ── -->
	<div class="flex flex-col h-[calc(100vh-12rem)]">
		<!-- Step Indicator (always visible) ──────────────────────────────── -->
		<div
			class="bg-white/70 dark:bg-warm-dark-950/80 backdrop-blur-md border-b border-gray-200 dark:border-warm-border/50 px-4 py-3 shrink-0"
		>
			<div class="flex items-center justify-between max-w-4xl mx-auto">
				<button
					v-for="step in steps"
					:key="step.id"
					@click="goToStep(step.id)"
					class="flex flex-col items-center gap-1 relative group"
				>
					<div
						class="w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all duration-300 cursor-pointer"
						:class="[
							step.id === currentStep
								? 'bg-[#D4AF37] border-[#D4AF37] text-[#1E2022] shadow-lg shadow-[#D4AF37]/30 animate-pulse'
								: step.id < currentStep
								? 'bg-[#D4AF37]/20 border-[#D4AF37] text-[#D4AF37]'
								: 'bg-white/50 dark:bg-warm-dark-800/50 border-gray-300 dark:border-warm-border text-gray-400 hover:border-[#D4AF37]/50',
						]"
					>
						<svg v-if="step.id < currentStep" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
						</svg>
						<svg v-else-if="step.id === currentStep" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="step.icon" />
						</svg>
						<svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" :d="step.icon" />
						</svg>
					</div>
					<span
						class="text-[10px] font-black uppercase tracking-widest transition-colors"
						:class="step.id === currentStep ? 'text-[#D4AF37]' : 'text-gray-400 dark:text-gray-500'"
					>
						{{ step.label }}
					</span>
					<div
						v-if="step.id < 4"
						class="absolute top-5 left-full w-10 h-0.5 -translate-y-1/2 pointer-events-none"
						:class="step.id < currentStep ? 'bg-[#D4AF37]' : 'bg-gray-300 dark:bg-warm-border/50'"
					></div>
				</button>
			</div>
		</div>

		<!-- Scrollable form area ─────────────────────────────────────────── -->
		<div class="flex-1 overflow-y-auto p-4 lg:p-6">
			<!-- STEP 1: Intake ─────────────────────────────────────────────── -->
			<div v-show="currentStep === 1" class="max-w-2xl mx-auto space-y-6">
				<h2 class="premium-title tracking-tighter text-2xl text-gray-900 dark:text-white">Order Intake</h2>

				<!-- Customer -->
				<div>
					<label class="text-[10px] font-black uppercase tracking-widest text-gray-500 dark:text-gray-400 block mb-1.5">
						Customer
					</label>
					<CustomerSelector 
						@selected="draftOrder.customer = $event" 
						@cleared="draftOrder.customer = null" 
						class="w-full" 
					/>
				</div>

				<!-- 1. Jewel360 CRM Sync Badge ───────────────────────────────── -->
				<div
					v-if="draftOrder.customer"
					class="bg-blue-500/5 border border-blue-500/20 rounded-xl p-3 flex items-start gap-3"
				>
					<div class="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center shrink-0">
						<svg class="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-9H7z" />
						</svg>
					</div>
					<div class="flex-1 min-w-0">
						<p class="text-[10px] font-black uppercase tracking-widest text-blue-500">Jewel360 CRM Sync</p>
						<p class="text-xs font-medium text-gray-600 dark:text-gray-300 mt-0.5">
							Auto-loaded from CRM: Ring Size 7, White Gold preference
						</p>
					</div>
				</div>

				<!-- Metal Type -->
				<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
					<div>
						<label class="text-[10px] font-black uppercase tracking-widest text-gray-500 dark:text-gray-400 block mb-1.5">
							Metal Type
						</label>
						<select
							v-model="draftOrder.metalType"
							class="w-full h-11 bg-gray-50/50 dark:bg-warm-dark-900/50 border border-gray-200 dark:border-warm-border rounded-lg text-sm font-medium text-gray-800 dark:text-gray-200 focus:ring-2 focus:ring-[#D4AF37] px-4 cursor-pointer outline-none transition-all"
						>
							<option :value="''" disabled>Select metal</option>
							<option value="Gold">Gold</option>
							<option value="Platinum">Platinum</option>
							<option value="Silver">Silver</option>
							<option value="Palladium">Palladium</option>
						</select>
					</div>
					<div>
						<label class="text-[10px] font-black uppercase tracking-widest text-gray-500 dark:text-gray-400 block mb-1.5">
							Purity
						</label>
						<select
							v-model="draftOrder.metalPurity"
							class="w-full h-11 bg-gray-50/50 dark:bg-warm-dark-900/50 border border-gray-200 dark:border-warm-border rounded-lg text-sm font-medium text-gray-800 dark:text-gray-200 focus:ring-2 focus:ring-[#D4AF37] px-4 cursor-pointer outline-none transition-all"
						>
							<option :value="''" disabled>Select purity</option>
							<option value="10K">10K</option>
							<option value="14K">14K</option>
							<option value="18K">18K</option>
							<option value="22K">22K</option>
							<option value="24K">24K</option>
							<option value="PT950">PT950</option>
							<option value="PT999">PT999</option>
						</select>
					</div>
				</div>

				<!-- Metal Weight -->
				<div>
					<label class="text-[10px] font-black uppercase tracking-widest text-gray-500 dark:text-gray-400 block mb-1.5">
						Metal Weight (grams)
					</label>
					<input
						v-model.number="draftOrder.metalWeight"
						type="number" step="0.01" min="0" placeholder="0.00"
						class="w-full h-11 bg-gray-50/50 dark:bg-warm-dark-900/50 border border-gray-200 dark:border-warm-border rounded-lg text-sm font-medium text-gray-800 dark:text-gray-200 placeholder-gray-400 focus:ring-2 focus:ring-[#D4AF37] px-4 outline-none transition-all"
					/>
				</div>

				<!-- Labor Cost -->
				<div>
					<label class="text-[10px] font-black uppercase tracking-widest text-gray-500 dark:text-gray-400 block mb-1.5">
						Labor Cost (USD)
					</label>
					<input
						v-model.number="draftOrder.laborCost"
						type="number" step="0.01" min="0" placeholder="0.00"
						class="w-full h-11 bg-gray-50/50 dark:bg-warm-dark-900/50 border border-gray-200 dark:border-warm-border rounded-lg text-sm font-medium text-gray-800 dark:text-gray-200 placeholder-gray-400 focus:ring-2 focus:ring-[#D4AF37] px-4 outline-none transition-all"
					/>
				</div>

				<!-- Notes -->
				<div>
					<label class="text-[10px] font-black uppercase tracking-widest text-gray-500 dark:text-gray-400 block mb-1.5">
						Notes
					</label>
					<textarea
						v-model="draftOrder.notes" rows="3"
						placeholder="Any special requests or design notes..."
						class="w-full bg-gray-50/50 dark:bg-warm-dark-900/50 border border-gray-200 dark:border-warm-border rounded-lg text-sm font-medium text-gray-800 dark:text-gray-200 placeholder-gray-400 focus:ring-2 focus:ring-[#D4AF37] px-4 py-3 outline-none transition-all resize-none"
					/>
				</div>
			</div>

			<!-- STEP 2: Design ─────────────────────────────────────────────── -->
			<div v-show="currentStep === 2" class="max-w-2xl mx-auto space-y-6">
				<h2 class="premium-title tracking-tighter text-2xl text-gray-900 dark:text-white">Design Details</h2>

				<!-- Category -->
				<div>
					<label class="text-[10px] font-black uppercase tracking-widest text-gray-500 dark:text-gray-400 block mb-1.5">
						Category
					</label>
					<div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
						<button
							v-for="cat in designCategories" :key="cat"
							@click="draftOrder.designCategory = cat"
							class="h-14 rounded-xl border-2 text-sm font-bold transition-all"
							:class="[
								draftOrder.designCategory === cat
									? 'border-[#D4AF37] bg-[#D4AF37]/10 text-[#D4AF37] shadow-md'
									: 'border-gray-200 dark:border-warm-border/50 bg-white/50 dark:bg-warm-dark-800/50 text-gray-600 dark:text-gray-300 hover:border-[#D4AF37]/50',
							]"
						>
							{{ cat }}
						</button>
					</div>
				</div>

				<!-- Style / Description -->
				<div>
					<label class="text-[10px] font-black uppercase tracking-widest text-gray-500 dark:text-gray-400 block mb-1.5">
						Style / Description
					</label>
					<textarea
						v-model="draftOrder.designDescription" rows="4"
						placeholder="Describe the design, style, or attach reference details..."
						class="w-full bg-gray-50/50 dark:bg-warm-dark-900/50 border border-gray-200 dark:border-warm-border rounded-lg text-sm font-medium text-gray-800 dark:text-gray-200 placeholder-gray-400 focus:ring-2 focus:ring-[#D4AF37] px-4 py-3 outline-none transition-all resize-none"
					/>
				</div>

				<!-- Image Upload -->
				<div
					class="border-2 border-dashed border-gray-300 dark:border-warm-border/50 rounded-xl p-8 text-center cursor-pointer hover:border-[#D4AF37]/50 transition-colors"
					@click="triggerImageUpload"
				>
					<svg class="w-10 h-10 mx-auto text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
					</svg>
					<p class="text-sm font-medium text-gray-500 dark:text-gray-400">Click to upload design reference image</p>
				</div>
				<input ref="fileInput" type="file" accept="image/*" class="hidden" @change="handleImageUpload" />
			</div>

			<!-- STEP 3: Stones ─────────────────────────────────────────────── -->
			<div v-show="currentStep === 3" class="max-w-4xl mx-auto space-y-4">
				<h2 class="premium-title tracking-tighter text-2xl text-gray-900 dark:text-white">Stone Sourcing</h2>
				<StoneSourcingTable />
			</div>

			<!-- STEP 4: Quote ──────────────────────────────────────────────── -->
			<div v-show="currentStep === 4" class="max-w-2xl mx-auto space-y-6">
				<h2 class="premium-title tracking-tighter text-2xl text-gray-900 dark:text-white">Quote Review</h2>

				<!-- 5. The Edge (POS Hold) Warning Banner ───────────────────── -->
				<div class="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-4 flex items-start gap-3">
					<svg class="w-5 h-5 text-yellow-600 dark:text-yellow-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
					</svg>
					<div>
						<p class="text-xs font-black uppercase tracking-widest text-yellow-700 dark:text-yellow-500">POS Hold Active</p>
						<p class="text-xs font-medium text-yellow-800 dark:text-yellow-400 mt-0.5">
							Items attached to this Job Bag will be locked from POS sales until final delivery.
						</p>
					</div>
				</div>

				<!-- 4. Luxe POS (Bespoke Serialization) Barcode ─────────────── -->
				<div class="bg-white/70 dark:bg-warm-dark-950/80 backdrop-blur-md rounded-xl border border-gray-200 dark:border-warm-border/50 p-5">
					<p class="text-[10px] font-black uppercase tracking-widest text-gray-500 dark:text-gray-400 mb-3">
						Bespoke Serialization
					</p>
					<div class="flex items-center justify-between">
						<div>
							<p class="font-mono font-black text-gray-900 dark:text-white text-lg tracking-wider">
								{{ jobBagBarcode }}
							</p>
							<p class="text-[10px] text-gray-400 dark:text-gray-500 mt-1">Unique Job Bag ID for this bespoke item</p>
						</div>
						<!-- Barcode visual -->
						<div class="flex items-center gap-0.5">
							<div v-for="i in 24" :key="i" class="w-0.5 bg-gray-900 dark:bg-white" :class="[
								i % 3 === 0 ? 'h-10' : 'h-8',
							]"></div>
						</div>
					</div>
				</div>

				<!-- Cost Breakdown (Zevar BOM) ────────────────────────── -->
				<div class="bg-white/70 dark:bg-warm-dark-950/80 backdrop-blur-md rounded-xl border border-gray-200 dark:border-warm-border/50 p-5 space-y-3">
					<p class="text-[10px] font-black uppercase tracking-widest text-gray-500 dark:text-gray-400 mb-2">
						Bill of Materials — Live Pricing
					</p>

					<div class="flex justify-between text-sm">
						<span class="text-gray-500 dark:text-gray-400">Stones ({{ stones.length }})</span>
						<span class="font-mono font-bold text-gray-800 dark:text-gray-200">
							{{ formatCurrency(totalStoneCost) }}
						</span>
					</div>
					<div class="flex justify-between text-sm">
						<span class="text-gray-500 dark:text-gray-400">Metal ({{ draftOrder.metalWeight }}g {{ draftOrder.metalType }} {{ draftOrder.metalPurity }})</span>
						<span class="font-mono font-bold text-gray-800 dark:text-gray-200">
							{{ formatCurrency(metalCost) }}
						</span>
					</div>
					<div class="flex justify-between text-sm">
						<span class="text-gray-500 dark:text-gray-400">Labor</span>
						<span class="font-mono font-bold text-gray-800 dark:text-gray-200">
							{{ formatCurrency(draftOrder.laborCost) }}
						</span>
					</div>
					<div class="flex justify-between text-sm">
						<span class="text-gray-500 dark:text-gray-400">Overhead</span>
						<span class="font-mono font-bold text-gray-800 dark:text-gray-200">
							{{ formatCurrency(draftOrder.overheadCost) }}
						</span>
					</div>
					<div class="border-t border-gray-200 dark:border-warm-border pt-3 flex justify-between text-sm">
						<span class="text-gray-500 dark:text-gray-400">Margin</span>
						<span class="font-mono font-bold text-gray-800 dark:text-gray-200">
							{{ draftOrder.marginPercent }}%
						</span>
					</div>
				</div>

				<!-- Grand Total -->
				<div class="bg-[#D4AF37]/10 dark:bg-[#D4AF37]/5 rounded-xl border border-[#D4AF37]/30 p-5 text-center">
					<p class="text-[10px] font-black uppercase tracking-widest text-[#D4AF37] mb-1">Estimated Total</p>
					<p v-if="isFetchingQuote" class="font-mono font-black text-[#D4AF37] text-2xl animate-pulse">CALCULATING...</p>
					<p v-else class="font-mono font-black text-[#D4AF37] text-2xl">
						{{ formatCurrency(grandTotal) }}
					</p>
				</div>

				<!-- Submit -->
				<div class="flex gap-3 justify-end">
					<Button
						type="button"
						@click="handleStartNewOrder"
						class="px-6 py-2.5 rounded-xl text-sm font-bold bg-white dark:bg-warm-dark-800 border border-gray-200 dark:border-warm-border text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-warm-dark-700 transition-all"
					>
						Start Over
					</Button>
					<Button
						type="button"
						@click="handleSubmit" :disabled="isSubmitting"
						class="px-8 py-2.5 rounded-xl text-sm font-bold bg-[#D4AF37] text-[#1E2022] hover:bg-[#CBA358] shadow-lg shadow-[#D4AF37]/20 disabled:opacity-50 transition-all"
					>
						<svg v-if="isSubmitting" class="w-4 h-4 animate-spin inline mr-2" fill="none" viewBox="0 0 24 24">
							<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
							<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
						</svg>
						{{ isSubmitting ? 'Submitting...' : 'Submit Order' }}
					</Button>
				</div>

				<!-- Error -->
				<div v-if="submitError" class="bg-red-500/10 border border-red-500/30 rounded-xl p-4 text-red-600 dark:text-red-400 text-sm font-medium">
					{{ submitError }}
				</div>
			</div>

			<!-- STEP 5: Success ────────────────────────────────────────────── -->
			<div v-show="submitSuccess" class="max-w-xl mx-auto flex flex-col items-center justify-center space-y-6 py-12">
				<div class="w-20 h-20 bg-green-500/10 border border-green-500/20 rounded-full flex items-center justify-center">
					<svg class="w-10 h-10 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
					</svg>
				</div>
				<div class="text-center">
					<h2 class="text-2xl font-bold text-gray-900 dark:text-white">Order Submitted!</h2>
					<p class="text-gray-500 dark:text-gray-400 text-center max-w-sm">
						Your special order has been recorded. It will now appear in the Job Bag dashboard for production tracking.
					</p>
				</div>
				<div v-if="submittedOrderId" class="w-full max-w-sm p-4 bg-[#D4AF37]/5 border border-[#D4AF37]/20 rounded-xl">
					<p class="text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">Client Tracking Link</p>
					<div class="flex items-center gap-2">
						<input 
							type="text" 
							readonly 
							:value="trackingUrl"
							class="w-full text-xs p-2 bg-white dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded focus:outline-none"
							@click="$event.target.select()"
						/>
						<button 
							type="button"
							class="p-2 text-[#D4AF37] hover:bg-[#D4AF37]/10 rounded transition-colors"
							@click="copyTrackingUrl"
							title="Copy to clipboard"
						>
							<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
						</button>
					</div>
				</div>
				<div class="flex gap-4 mt-8">
					<Button
						type="button"
						@click="handleStartNewOrder"
						class="px-6 py-2.5 rounded-xl text-sm font-bold bg-white dark:bg-warm-dark-800 border border-gray-200 dark:border-warm-border text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-warm-dark-700 transition-all"
					>
						Start New Order
					</Button>
					<Button
						type="button"
						@click="$router.push('/special-orders/job-bag')"
						class="px-6 py-2.5 rounded-xl text-sm font-bold bg-[#D4AF37] text-[#1E2022] hover:bg-[#CBA358] shadow-lg shadow-[#D4AF37]/20 transition-all"
					>
						Go to Job Bag
					</Button>
				</div>
			</div>
		</div>

		<!-- ── Footer Navigation (always pinned to bottom) ────────────────── -->
		<div
			v-if="!submitSuccess"
			class="bg-white/70 dark:bg-warm-dark-950/80 backdrop-blur-md border-t border-gray-200 dark:border-warm-border/50 px-4 py-3 flex items-center justify-between shrink-0"
		>
			<Button
				type="button"
				v-if="currentStep > 1"
				@click.prevent="prevStep"
				class="px-5 py-2 rounded-xl text-sm font-bold bg-white dark:bg-warm-dark-800 border border-gray-200 dark:border-warm-border text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-warm-dark-700 transition-all"
			>
				← Back
			</Button>
			<div v-else></div>

			<span class="text-xs font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider">
				Step {{ currentStep }} of 4
			</span>

			<Button
				type="button"
				v-if="currentStep < 4"
				@click.prevent="nextStep"
				class="px-5 py-2 rounded-xl text-sm font-bold bg-[#D4AF37] text-[#1E2022] hover:bg-[#CBA358] shadow-md shadow-[#D4AF37]/20 transition-all"
			>
				Continue →
			</Button>
			<div v-else></div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useSpecialOrderStore } from '@/stores/specialOrder'
import { useCartStore } from '@/stores/cart'
import { createResource } from 'frappe-ui'
import CustomerSelector from '@/components/CustomerSelector.vue'
import StoneSourcingTable from './StoneSourcingTable.vue'

const store = useSpecialOrderStore()
const { currentStep, steps, draftOrder, grandTotal, totalStoneCost, isFetchingQuote, liveQuote } = storeToRefs(store)
const { goToStep, nextStep, prevStep, resetDraft, submitOrder } = store

const designCategories = ['Ring', 'Necklace', 'Bracelet', 'Earrings']

// Generate the Luxe POS bespoke Job Bag barcode
const jobBagBarcode = computed(() => {
	const year = new Date().getFullYear()
	const seq = String(Math.floor(Math.random() * 9999) + 1).padStart(4, '0')
	return `JB-${year}-${seq}`
})

// Metal cost helper
const metalCost = computed(() => {
	if (liveQuote.value?.metal_cost !== undefined) {
		return liveQuote.value.metal_cost
	}
	const weight = Number(draftOrder.value?.metalWeight) || 0
	const pricePerGram = draftOrder.value?.metalPricePerGram || 0
	return Number((weight * pricePerGram).toFixed(2))
})

const stones = computed(() => store.draftOrder.stones)
const submitError = ref('')
const submitSuccess = ref(false)
const isSubmitting = ref(false)
const submittedOrderId = ref('')

const trackingUrl = computed(() => {
	if (!submittedOrderId.value) return ''
	// Use window only if we are in the browser
	const origin = typeof window !== 'undefined' ? window.location.origin : ''
	return `${origin}/pos/track?id=${submittedOrderId.value}`
})

function copyTrackingUrl() {
	if (typeof navigator !== 'undefined' && navigator.clipboard) {
		navigator.clipboard.writeText(trackingUrl.value)
	}
}

// Load warehouse list (for potential future use, not displayed in form)
const warehouses = ref([])
const posProfileResource = createResource({
	url: 'zevar_core.api.pos.get_pos_profile',
	auto: true,
})
onMounted(() => {
	posProfileResource.submit().then((res) => {
		if (res?.company) {
			store.draftOrder.company = res.company
		}
	})

	const cartStore = useCartStore()
	if (cartStore.customer) {
		store.draftOrder.customer = cartStore.customer
	}
})

function handleStartNewOrder() {
	resetDraft()
	submitSuccess.value = false
	submitError.value = ''
	submittedOrderId.value = ''
}

async function handleSubmit() {
	if (!draftOrder.value.customer) {
		submitError.value = 'Customer is required. Please select a customer in Step 1.'
		goToStep(1)
		return
	}

	isSubmitting.value = true
	submitError.value = ''
	try {
		const result = await submitOrder()
		if (result && result.order_id) {
			submittedOrderId.value = result.order_id
		}
		submitSuccess.value = true
	} catch (e) {
		// Use frappe-ui parsed messages if available, fallback to the exception name
		submitError.value = e?.messages?.[0] || e?.message || 'Failed to submit order. Please try again.'
		console.error('[SpecialOrder] submit error:', e)
	} finally {
		isSubmitting.value = false
	}
}

function formatCurrency(value) {
	return '$' + Number(value || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const fileInput = ref(null)
function triggerImageUpload() { fileInput.value?.click() }
function handleImageUpload(event) {
	const file = event.target.files?.[0]
	if (file) console.log('[SpecialOrder] Design image selected:', file.name)
}
</script>
