<template>
	<div :class="persistent ? 'flex flex-col flex-1 h-full min-h-0 overflow-hidden' : ''">
		<!-- Backdrop -->
		<Teleport to="body" :disabled="persistent">
			<Transition
				enter-active-class="transition-opacity duration-300"
				enter-from-class="opacity-0"
				enter-to-class="opacity-100"
				leave-active-class="transition-opacity duration-200"
				leave-from-class="opacity-100"
				leave-to-class="opacity-0"
			>
				<div
					v-if="isOpen && !persistent"
					@click="close"
					class="fixed inset-0 bg-gray-900/50 backdrop-blur-sm z-40"
				></div>
			</Transition>

			<!-- Bottom Sheet (non-persistent mobile/tablet) -->
			<Transition
				enter-active-class="transition-transform duration-300 ease-out"
				enter-from-class="translate-y-full"
				enter-to-class="translate-y-0"
				leave-active-class="transition-transform duration-200 ease-in"
				leave-from-class="translate-y-0"
				leave-to-class="translate-y-full"
			>
				<div
					v-if="isOpen || persistent"
					:class="[
						persistent
							? 'flex flex-col flex-1 h-full min-h-0 overflow-hidden bg-transparent'
							: 'fixed bottom-0 left-0 right-0 z-50 max-h-[85vh] bg-white dark:bg-warm-card rounded-t-2xl shadow-2xl flex flex-col border-t border-gray-200 dark:border-warm-border min-h-0',
					]"
				>
					<!-- Cart Header -->
					<div
						class="p-4 border-b border-gray-100 dark:border-warm-border/50 flex items-center justify-between shrink-0"
					>
						<h2
							class="text-lg font-bold text-gray-800 dark:text-white flex items-center gap-2"
						>
							<span>💎</span> Selection Tray
							<span class="text-xs font-normal text-gray-500 dark:text-gray-400"
								>({{ cart.totalItems }}
								{{ cart.totalItems === 1 ? 'piece' : 'pieces' }})</span
							>
						</h2>

						<div class="flex items-center gap-2">
							<button
								v-if="cart.items.length > 0"
								@click="cart.clearCart()"
								class="text-xs font-bold text-red-500 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20 px-2 py-1 rounded transition-colors"
							>
								Clear
							</button>

							<button
								v-if="!persistent"
								@click="close"
								class="p-2 hover:bg-gray-200 dark:hover:bg-white/10 rounded-full transition-colors text-gray-500 dark:text-gray-400"
							>
								<svg
									class="w-5 h-5"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M6 18L18 6M6 6l12 12"
									></path>
								</svg>
							</button>
						</div>
					</div>

					<div
						v-if="cart.items.length === 0"
						class="flex-1 flex flex-col items-center justify-center text-gray-400 dark:text-gray-600"
					>
						<svg
							class="w-16 h-16 mb-4 text-gray-200 dark:text-gray-700"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"
							></path>
						</svg>
						<p>Your selection tray is empty.</p>
						<p class="text-xs text-gray-400 dark:text-gray-600 mt-1">
							Add pieces from the collection to begin curating.
						</p>
						<button
							@click="close"
							class="mt-4 text-sm text-[#D4AF37] font-medium hover:underline"
						>
							Browse Collection
						</button>
					</div>

					<div v-else class="flex-1 flex flex-col min-h-0 overflow-hidden">
						<!-- Customer Selector -->
						<div
							class="p-4 border-b border-gray-100 dark:border-warm-border/50 bg-white dark:bg-warm-card flex-shrink-0 z-10"
						>
							<div class="mb-3">
								<label
									class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider block mb-2"
									>Customer <span class="text-red-500">*</span></label
								>
								<div class="flex bg-gray-100 dark:bg-warm-dark-700 p-1 rounded-lg">
									<button
										class="flex-1 text-xs font-medium py-1.5 rounded-md transition-colors"
										:class="
											cart.customerType === 'Individual'
												? 'bg-white dark:bg-warm-card shadow-sm text-gray-900 dark:text-white'
												: 'text-gray-500'
										"
										@click="setCustomerType('Individual')"
									>
										Individual
									</button>
									<button
										class="flex-1 text-xs font-medium py-1.5 rounded-md transition-colors"
										:class="
											cart.customerType === 'Company'
												? 'bg-white dark:bg-warm-card shadow-sm text-gray-900 dark:text-white'
												: 'text-gray-500'
										"
										@click="setCustomerType('Company')"
									>
										Company
									</button>
									<button
										class="flex-1 text-xs font-medium py-1.5 rounded-md transition-colors"
										:class="
											cart.customerType === 'Walkin'
												? 'bg-white dark:bg-warm-card shadow-sm text-gray-900 dark:text-white'
												: 'text-gray-500'
										"
										@click="setCustomerType('Walkin')"
									>
										Walk-In
									</button>
								</div>
							</div>
							<CustomerSelector v-if="cart.customerType !== 'Walkin'" />
						</div>

						<div class="flex-1 min-h-0 overflow-y-auto p-4 space-y-4 custom-scrollbar">
							<div
								v-for="(item, index) in cart.items"
								:key="index"
								class="flex gap-4 border-b border-gray-100 dark:border-warm-border/50 pb-4 last:border-0"
							>
								<div
									class="w-16 h-16 bg-gray-100 dark:bg-warm-dark-700 rounded-lg flex-shrink-0 overflow-hidden border border-gray-200 dark:border-warm-border/50 relative"
								>
									<img
										v-if="item.image"
										:src="item.image"
										loading="lazy"
										class="w-full h-full object-cover"
									/>
									<div
										v-else
										class="w-full h-full flex items-center justify-center text-xs text-gray-400 dark:text-gray-600"
									>
										No Img
									</div>

									<div
										v-if="item.qty > 1"
										class="absolute bottom-0 right-0 bg-black dark:bg-[#D4AF37] text-white dark:text-black text-[10px] font-bold px-1.5 py-0.5 rounded-tl-md"
									>
										x{{ item.qty }}
									</div>
								</div>

								<div class="flex-1 min-w-0">
									<h3
										class="text-sm font-bold text-gray-900 dark:text-white truncate"
									>
										{{ item.item_name }}
									</h3>
									<p class="text-xs text-gray-500 dark:text-gray-400 truncate">
										{{ item.item_code }}
									</p>

									<div class="flex items-center gap-2 mt-1">
										<span
											class="text-[10px] uppercase font-bold bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-500 px-1.5 py-0.5 rounded"
											>{{ item.metal }}</span
										>
										<span
											class="text-[10px] uppercase font-bold bg-gray-100 dark:bg-warm-dark-900 text-gray-800 dark:text-gray-300 px-1.5 py-0.5 rounded"
											>{{ item.purity }}</span
										>
									</div>

									<div class="mt-2 flex items-center justify-between">
										<div class="flex flex-col">
											<span class="text-xs text-gray-400 dark:text-gray-500"
												>{{ formatCurrency(item.amount) }} ea</span
											>
											<span
												class="font-mono text-sm font-bold text-gray-900 dark:text-white"
											>
												{{ formatCurrency(item.amount * item.qty) }}
											</span>
										</div>

										<button
											@click="cart.removeItem(index)"
											class="text-red-400 hover:text-red-600 p-1 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-colors"
											title="Remove Item"
										>
											<svg
												class="w-4 h-4"
												fill="none"
												stroke="currentColor"
												viewBox="0 0 24 24"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
												></path>
											</svg>
										</button>
									</div>
								</div>
							</div>
						</div>
					</div>

					<!-- Trade-Ins Section -->
					<div v-if="cart.items.length > 0" class="px-4 pb-2 shrink-0">
						<div class="border-t border-gray-100 dark:border-warm-border/50 pt-3">
							<button
								@click="showTradeInForm = !showTradeInForm"
								class="w-full flex items-center justify-between text-sm font-medium text-[#D4AF37] hover:text-[#b5952f] transition"
							>
								<span class="flex items-center gap-2">
									<svg
										class="w-4 h-4"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"
										></path>
									</svg>
									Trade-In ({{ cart.tradeIns.length }})
								</span>
								<svg
									class="w-4 h-4 transition-transform"
									:class="showTradeInForm ? 'rotate-180' : ''"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M19 9l-7 7-7-7"
									></path>
								</svg>
							</button>

							<div v-if="showTradeInForm" class="mt-3 space-y-3">
								<!-- Existing trade-ins -->
								<div
									v-for="(ti, idx) in cart.tradeIns"
									:key="idx"
									class="flex items-center justify-between bg-orange-50 dark:bg-orange-900/10 p-2 rounded-lg border border-orange-100 dark:border-orange-800/20"
								>
									<div class="min-w-0">
										<div
											class="text-xs font-bold text-gray-900 dark:text-white truncate"
										>
											{{ ti.description || 'Trade-In Item' }}
										</div>
										<div class="text-[10px] text-gray-500">
											Value: {{ formatCurrency(ti.trade_in_value) }} · Min
											new:
											{{ formatCurrency(ti.trade_in_value * 2) }}
										</div>
									</div>
									<button
										@click="cart.removeTradeIn(idx)"
										class="p-1 text-red-400 hover:text-red-600 ml-2 flex-shrink-0"
									>
										<svg
											class="w-3.5 h-3.5"
											fill="none"
											stroke="currentColor"
											viewBox="0 0 24 24"
										>
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M6 18L18 6M6 6l12 12"
											></path>
										</svg>
									</button>
								</div>

								<!-- Add form -->
								<div class="space-y-2">
									<input
										v-model="tradeInDescription"
										type="text"
										placeholder="Item description (e.g. Gold Ring)"
										class="w-full px-3 py-2 bg-white dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm"
									/>
									<div class="flex gap-2">
										<div class="flex items-center gap-1 flex-1">
											<span class="text-gray-400 text-sm">$</span>
											<input
												v-model.number="tradeInValue"
												type="number"
												min="0"
												placeholder="Trade-in value"
												class="w-full px-2 py-2 bg-white dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm font-mono"
											/>
										</div>
										<button
											@click="addTradeInItem"
											:disabled="!tradeInValue || tradeInValue <= 0"
											class="px-3 py-2 text-sm font-medium bg-[#D4AF37] text-black rounded-lg hover:bg-[#b5952f] disabled:opacity-50 transition flex-shrink-0"
										>
											Add
										</button>
									</div>
								</div>

								<!-- Trade-in credit total -->
								<div
									v-if="cart.tradeIns.length > 0"
									class="flex justify-between text-sm font-bold text-orange-600 dark:text-orange-400 pt-2 border-t border-orange-100 dark:border-orange-800/20"
								>
									<span>Trade-In Credit</span>
									<span>-{{ formatCurrency(tradeInTotal) }}</span>
								</div>
							</div>
						</div>
					</div>

					<div
						v-if="cart.items.length > 0"
						class="p-6 bg-gray-50 dark:bg-warm-dark-700 border-t border-gray-200 dark:border-warm-border shrink-0"
					>
						<div class="space-y-2 mb-4 text-sm">
							<div class="flex justify-between text-gray-600 dark:text-gray-400">
								<span>Subtotal</span>
								<span>{{ formatCurrency(cart.subtotal) }}</span>
							</div>
							<div class="flex justify-between text-gray-600 dark:text-gray-400">
								<span>Tax ({{ cart.taxRate }}%)</span>
								<span>{{ formatCurrency(cart.tax) }}</span>
							</div>
							<div
								v-if="cart.tradeIns.length > 0"
								class="flex justify-between text-orange-600 dark:text-orange-400"
							>
								<span>Trade-In Credit</span>
								<span>-{{ formatCurrency(tradeInTotal) }}</span>
							</div>
							<div
								class="flex justify-between text-lg font-bold text-gray-900 dark:text-white pt-2 border-t border-gray-200 dark:border-warm-border"
							>
								<span>Total</span>
								<span>{{ formatCurrency(cart.grandTotal) }}</span>
							</div>
						</div>

						<div class="flex flex-col gap-2 mt-4">
							<button
								v-if="posSession.hasActiveSession"
								@click="startLayaway"
								class="w-full py-3 rounded-lg font-bold shadow-lg transition-all flex items-center justify-center gap-2 bg-[#D4AF37]/10 text-[#D4AF37] border border-[#D4AF37]/30 hover:bg-[#D4AF37]/20 active:scale-95"
							>
								Create Layaway
							</button>
							<router-link
								v-if="!posSession.hasActiveSession"
								to="/opening"
								class="w-full py-3 rounded-lg font-bold shadow-lg transition-all flex items-center justify-center gap-2 bg-red-500/10 text-red-500 border border-red-500/30 hover:bg-red-500/20 active:scale-95 text-sm"
							>
								Open Register Session
							</router-link>
							<button
								v-else
								@click="showCheckout = true"
								:disabled="!isCheckoutReady"
								class="w-full py-3 rounded-lg font-bold shadow-lg transition-all flex items-center justify-center gap-2"
								:class="
									isCheckoutReady
										? 'bg-gray-900 dark:bg-[#D4AF37] text-white dark:text-black hover:bg-gray-800 dark:hover:bg-[#b5952f] active:scale-95'
										: 'bg-gray-200 dark:bg-warm-dark-700 text-gray-400 dark:text-gray-600 cursor-not-allowed'
								"
							>
								{{ checkoutButtonText }}
							</button>
						</div>
					</div>
				</div>
			</Transition>
		</Teleport>

		<CheckoutModal :show="showCheckout" @close="showCheckout = false" />
	</div>
</template>

<script setup>
import { useCartStore } from '@/stores/cart.js'
import { usePosSessionStore } from '@/stores/posSession.js'
import CheckoutModal from '@/components/CheckoutModal.vue'
import CustomerSelector from '@/components/CustomerSelector.vue'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
	isOpen: Boolean,
	persistent: Boolean,
})
const emit = defineEmits(['close'])
const cart = useCartStore()
const posSession = usePosSessionStore()
const router = useRouter()
const showCheckout = ref(false)

function startLayaway() {
	emit('close')
	const query = { action: 'new' }
	if (cart.customer) {
		query.customer = cart.customer.name || cart.customer.customer_name
	}
	router.push({ name: 'Layaway', query })
}

const isCheckoutReady = computed(() => {
	if (!posSession.hasActiveSession) return false
	if (cart.customerType === 'Walkin') return true
	return !!cart.customer
})

const checkoutButtonText = computed(() => {
	if (!posSession.hasActiveSession) return 'Open Register to Checkout'
	if (cart.customerType === 'Walkin') return 'Checkout'
	if (!cart.customer) return 'Select Customer to Checkout'
	return 'Checkout'
})

function setCustomerType(type) {
	cart.customerType = type
	cart.clearCustomer()
}

// Trade-in form state
const showTradeInForm = ref(false)
const tradeInDescription = ref('')
const tradeInValue = ref(null)

const tradeInTotal = computed(() => {
	return cart.tradeIns.reduce((sum, ti) => sum + (ti.trade_in_value || 0), 0)
})

function addTradeInItem() {
	if (!tradeInValue.value || tradeInValue.value <= 0) return
	// Auto-set new_item_value to the cart subtotal (the backend validates 2x rule at invoice level)
	cart.addTradeIn({
		description: tradeInDescription.value,
		tradeInValue: tradeInValue.value,
		newItemValue: cart.subtotal,
	})
	tradeInDescription.value = ''
	tradeInValue.value = null
}

function close() {
	emit('close')
}

function formatCurrency(val) {
	if (!val) return '$0.00'
	return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val)
}
// --- Persistent panel duplicates the same content, so we use a shared template approach ---
// The persistent panel content is identical to the bottom-sheet content.
// Both render the same cart items, customer selector, trade-ins, and checkout button.
// Vue re-uses the CartSidebar component in both modes via the v-if/persistent prop.

import { onMounted, onUnmounted } from 'vue'

// Body scroll lock for overlay mode
function lockBodyScroll() {
	document.body.style.overflow = 'hidden'
}
function unlockBodyScroll() {
	document.body.style.overflow = ''
}

// Watch open state for scroll lock
import { watchEffect } from 'vue'
watchEffect(() => {
	if (props.isOpen && !props.persistent) {
		lockBodyScroll()
	} else if (!props.persistent) {
		unlockBodyScroll()
	}
})

// Close on Escape
function handleEscape(e) {
	if (e.key === 'Escape' && props.isOpen && !props.persistent) {
		close()
	}
}

onMounted(() => {
	document.addEventListener('keydown', handleEscape)
})

onUnmounted(() => {
	document.removeEventListener('keydown', handleEscape)
	unlockBodyScroll()
})
</script>
