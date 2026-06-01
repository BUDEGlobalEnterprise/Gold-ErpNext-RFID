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
							: 'fixed bottom-0 left-0 right-0 z-50 max-h-[85vh] bg-[#FAF5EE] dark:bg-warm-card rounded-t-2xl shadow-2xl flex flex-col border-t border-[#EFEAE2] dark:border-warm-border min-h-0 overflow-hidden',
					]"
				>
					<!-- Cart Header -->
					<div
						class="p-3.5 sm:p-4 border-b border-gray-100 dark:border-warm-border/50 flex items-center justify-between shrink-0"
					>
						<div class="flex items-center gap-2 min-w-0">
							<span class="text-sm">🛒</span>
							<h2 class="text-xs sm:text-sm font-black text-gray-900 dark:text-white tracking-tight uppercase">
								Sale
							</h2>
							<div
								class="w-6 h-6 rounded-full bg-gradient-to-br from-[#D4AF37] to-[#F2E6A0] flex items-center justify-center text-[#1E2022] font-black text-[11px] shadow-sm shrink-0"
								data-testid="cart-item-count"
							>
								{{ cart.totalItems }}
							</div>
						</div>

						<div class="flex items-center gap-1.5 shrink-0">
							<button
								v-if="cart.items.length > 0"
								@click="holdCurrentCart"
								:disabled="holdingCart"
								class="px-2.5 py-1 text-[9px] font-black tracking-wider uppercase rounded-full border border-amber-200 dark:border-amber-900/40 bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400 hover:scale-105 active:scale-95 transition-all shadow-xs flex items-center gap-1"
								title="Park this cart for later"
							>
								⏸ Hold
							</button>
							<button
								v-if="cart.items.length > 0"
								@click="cart.clearCart()"
								class="px-2.5 py-1 text-[9px] font-black tracking-wider uppercase rounded-full border border-red-200 dark:border-red-900/40 bg-red-50 dark:bg-red-900/20 text-red-500 dark:text-red-400 hover:scale-105 active:scale-95 transition-all shadow-xs flex items-center gap-1"
								title="Clear active cart"
							>
								🗑 Clear
							</button>

							<button
								v-if="!persistent"
								@click="close"
								class="w-7 h-7 rounded-full border border-gray-200 dark:border-warm-border/50 bg-gray-50 dark:bg-warm-dark-800 text-gray-500 dark:text-gray-400 flex items-center justify-center transition hover:scale-105 active:scale-95 shadow-xs"
								title="Close Panel"
							>
								✕
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
						<p>Your shopping cart is empty.</p>
						<p class="text-xs text-gray-400 dark:text-gray-600 mt-1">
							Search or scan items to add them here.
						</p>
						<button
							@click="close"
							class="mt-4 text-sm text-[#D4AF37] font-medium hover:underline"
						>
							Browse Catalog
						</button>
					</div>

					<div v-else class="flex-1 flex flex-col min-h-0 overflow-hidden">
						<div class="flex-1 min-h-0 overflow-y-auto p-3 sm:p-4 space-y-3.5 sm:space-y-4 custom-scrollbar">
							<!-- Customer Selector (Compact layout) -->
							<div
								class="p-3 border border-[#E3C583]/20 dark:border-warm-border/30 rounded-xl bg-white dark:bg-warm-dark-800/40 shadow-xs z-10 animate-in fade-in"
							>
								<div class="mb-2.5">
									<div class="flex items-center justify-between">
										<!-- Bigger, More Visible Segment Tabs -->
										<div class="flex bg-gray-100/80 dark:bg-warm-dark-700 p-1 rounded-xl border border-gray-200/40 dark:border-warm-border/10 w-full shadow-inner">
											<button
												class="flex-1 text-[11px] font-black py-2 rounded-lg transition-all uppercase tracking-wider duration-200"
												:class="
													cart.customerType === 'Individual'
														? 'bg-[#D4AF37] text-white shadow-md transform scale-[1.02]'
														: 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
												"
												@click="setCustomerType('Individual')"
											>
												Individual
											</button>
											<button
												class="flex-1 text-[11px] font-black py-2 rounded-lg transition-all uppercase tracking-wider duration-200"
												:class="
													cart.customerType === 'Company'
														? 'bg-[#D4AF37] text-white shadow-md transform scale-[1.02]'
														: 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
												"
												@click="setCustomerType('Company')"
											>
												Company
											</button>
											<button
												class="flex-1 text-[11px] font-black py-2 rounded-lg transition-all uppercase tracking-wider duration-200"
												:class="
													cart.customerType === 'Walkin'
														? 'bg-[#D4AF37] text-white shadow-md transform scale-[1.02]'
														: 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
												"
												@click="setCustomerType('Walkin')"
											>
												Walk-In
											</button>
										</div>
									</div>
								</div>
								<CustomerSelector v-if="cart.customerType !== 'Walkin'" @open-clienteling="showClienteling = true" />
								<button
									v-if="cart.customer?.name && cart.customerType !== 'Walkin'"
									@click.prevent="showClienteling = true"
									class="mt-2 w-full flex items-center justify-center gap-1.5 py-1.5 text-[10px] font-bold uppercase tracking-wider text-[#D4AF37] hover:bg-[#D4AF37]/10 rounded-lg transition-colors border border-[#D4AF37]/20"
									title="Client Intelligence"
								>
									<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
									</svg>
									Client Profile
								</button>
							</div>

							<!-- Sleek Unified Register Cart List -->
							<div class="bg-white dark:bg-warm-dark-800 rounded-xl p-3 border border-[#EFEAE2] dark:border-warm-border/30 shadow-xs divide-y divide-gray-100 dark:divide-warm-border/20 z-10 animate-in fade-in">
								<div
									v-for="(item, index) in cart.items"
									:key="index"
									class="py-2.5 first:pt-0 last:pb-0 flex gap-3 relative animate-in slide-in-from-bottom-2"
								>
									<!-- Image Container (Slightly more compact) -->
									<div
										class="w-11 h-11 rounded-lg flex-shrink-0 overflow-hidden border border-[#EFEAE2] dark:border-warm-border/30 relative bg-[#F3F1ED] dark:bg-warm-dark-900"
									>
										<img
											:src="`${baseUrl}placeholders/${getJewelryCategory(item)}.png`"
											:alt="item.item_name"
											class="w-full h-full object-cover"
											@error="(e) => e.target.src = `${baseUrl}placeholders/jewel.png`"
										/>
									</div>

									<!-- Item Details -->
									<div class="flex-1 min-w-0 flex flex-col justify-between">
										<div class="pr-6">
											<h3
												class="text-[11px] font-bold text-gray-900 dark:text-white truncate leading-snug"
											>
												{{ item.item_name }}
											</h3>
											<div class="flex items-center gap-2 mt-0.5">
												<span class="text-[9px] text-gray-400 dark:text-gray-500 font-mono">
													{{ item.item_code }}
												</span>
												<span
													v-if="item.metal || item.purity"
													class="text-[9px] font-semibold text-[#CBA358]"
												>
													• {{ item.metal && item.purity ? `${item.metal} · ${item.purity}` : (item.metal || item.purity) }}
												</span>
											</div>
										</div>

										<!-- Pricing & Quantity Controls -->
										<div class="flex items-center justify-between mt-2">
											<!-- Sleek Quantity Adjuster -->
											<div class="flex items-center border border-gray-200 dark:border-warm-border/40 rounded-md overflow-hidden h-6 w-16">
												<button 
													@click="updateQty(index, item.qty - 1)" 
													class="w-5 h-full flex items-center justify-center bg-gray-50 dark:bg-warm-dark-900 hover:bg-gray-100 dark:hover:bg-warm-dark-800 text-[10px] font-extrabold text-gray-500 transition-colors"
												>-</button>
												<span class="flex-1 text-center text-[10px] font-bold text-gray-900 dark:text-white">{{ item.qty }}</span>
												<button 
													@click="updateQty(index, item.qty + 1)" 
													class="w-5 h-full flex items-center justify-center bg-gray-50 dark:bg-warm-dark-900 hover:bg-gray-100 dark:hover:bg-warm-dark-800 text-[10px] font-extrabold text-gray-500 transition-colors"
												>+</button>
											</div>

											<!-- Prices (Unit & Total) -->
											<div class="text-right flex flex-col items-end">
												<span class="text-[8px] text-gray-400 dark:text-gray-500"
													>{{ formatCurrency(item.amount) }} ea</span
												>
												<span class="font-mono text-xs font-black text-[#D4AF37]">
													{{ formatCurrency(item.amount * item.qty) }}
												</span>
											</div>
										</div>
									</div>

									<!-- Clean Right Side Delete Button -->
									<button
										@click="cart.removeItem(index)"
										class="absolute top-2 right-0 w-4 h-4 flex items-center justify-center text-gray-300 dark:text-gray-600 hover:text-red-500 rounded-full transition-colors"
										title="Remove Item"
									>
										✕
									</button>
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
								<span data-testid="grand-total">{{
									formatCurrency(cart.grandTotal)
								}}</span>
							</div>
						</div>

						<div class="flex flex-col gap-2.5 mt-4">
							<button
								v-if="posSession.hasActiveSession"
								@click="startLayaway"
								class="w-full py-3.5 bg-[#D6BA8B] hover:bg-[#C9A976] text-[#1E2022] rounded-xl font-bold shadow-sm transition duration-200 active:scale-95 text-sm flex flex-col items-center justify-center leading-tight border border-[#D6BA8B]/20"
							>
								<span>Create Layaway</span>
								<span class="text-[9px] font-normal text-gray-700/80 mt-0.5">
									{{ formatCurrency(cart.grandTotal * 0.5) }} Deposit Required
								</span>
							</button>
							<router-link
								v-if="!posSession.hasActiveSession"
								to="/opening"
								class="w-full py-3.5 bg-red-500/10 text-red-500 hover:bg-red-500/20 border border-red-500/30 rounded-xl font-bold transition duration-200 active:scale-95 text-sm flex items-center justify-center gap-2"
							>
								Open Register Session
							</router-link>
							<button
								v-else
								@click="
									showCheckout = true;
									ui.closeLayawayPayment();
								"
								:disabled="!isCheckoutReady"
								class="w-full py-3.5 rounded-xl font-bold shadow-md transition duration-200 active:scale-95 text-sm flex items-center justify-center gap-2"
								:class="
									isCheckoutReady
										? 'bg-[#1E2022] hover:bg-black text-white dark:bg-[#D4AF37] dark:text-black dark:hover:bg-[#b5952f]'
										: 'bg-gray-200 dark:bg-warm-dark-700 text-gray-400 dark:text-gray-600 cursor-not-allowed'
								"
								data-testid="checkout-btn"
							>
								{{ checkoutButtonText }}
							</button>
						</div>
					</div>
				</div>
			</Transition>
		</Teleport>

		<CheckoutModal :show="showCheckout" @close="showCheckout = false" />
		<CustomerClientelingDrawer
			:show="showClienteling"
			:customer-name="cart.customer?.name || ''"
			@close="showClienteling = false"
		/>
	</div>
</template>

<script setup>
import { useCartStore } from '@/stores/cart.js'
import { usePosSessionStore } from '@/stores/posSession.js'
import CheckoutModal from '@/components/CheckoutModal.vue'
import CustomerSelector from '@/components/CustomerSelector.vue'
import CustomerClientelingDrawer from './CustomerClientelingDrawer.vue'
import { ref, computed } from 'vue'

const baseUrl = import.meta.env.BASE_URL
import { useRouter } from 'vue-router'
import { useUIStore } from '@/stores/ui.js'

const props = defineProps({
	isOpen: Boolean,
	persistent: Boolean,
})
const emit = defineEmits(['close'])

function getJewelryCategory(item) {
	const name = (item.item_name || '').toLowerCase();
	const group = (item.item_group || '').toLowerCase();
	const type = (item.jewelry_type || '').toLowerCase();
	const cat = (item.category || '').toLowerCase();
	
	if (name.includes('ring') || group.includes('ring') || type.includes('ring') || cat.includes('ring')) {
		return 'ring';
	}
	if (name.includes('earring') || group.includes('earring') || type.includes('earring') || cat.includes('earring')) {
		return 'earring';
	}
	if (name.includes('pendant') || name.includes('gemstone') || group.includes('pendant') || type.includes('pendant') || cat.includes('pendant')) {
		return 'pendant';
	}
	if (name.includes('watch') || name.includes('timepiece') || group.includes('watch') || type.includes('watch') || cat.includes('watch')) {
		return 'watch';
	}
	if (name.includes('bracelet') || name.includes('bangle') || group.includes('bangle') || group.includes('bracelet') || type.includes('bracelet') || cat.includes('bracelet') || name.includes('cuff')) {
		return 'bracelet';
	}
	if (name.includes('necklace') || name.includes('choker') || group.includes('necklace') || type.includes('necklace') || cat.includes('necklace')) {
		return 'necklace';
	}
	// Smart resolution for Chain, Link, Rope, Cuban
	if (name.includes('chain') || name.includes('link') || name.includes('rope') || name.includes('cuban') || group.includes('chain') || type.includes('chain')) {
		if (/7|8|9/.test(name)) {
			return 'bracelet';
		}
		return 'necklace';
	}
	return 'jewel';
}
const cart = useCartStore()
const posSession = usePosSessionStore()
const ui = useUIStore()
const router = useRouter()
const showCheckout = ref(false)
const showClienteling = ref(false)
const holdingCart = ref(false)

async function holdCurrentCart() {
	if (cart.items.length === 0 || holdingCart.value) return
	holdingCart.value = true
	try {
		const note = prompt('Label for held cart (optional):', cart.customer?.customer_name || '')
		if (note === null) {
			holdingCart.value = false
			return
		} // cancelled

		const res = await fetch('/api/method/zevar_core.api.pos.hold_cart', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-Frappe-CSRF-Token': window.csrf_token || '',
			},
			body: JSON.stringify({
				items: JSON.stringify(
					cart.items.map((i) => ({
						item_code: i.item_code,
						item_name: i.item_name,
						qty: i.qty || 1,
						amount: i.amount || 0,
						serial_no: i.serial_no || null,
						image: i.image || null,
					}))
				),
				customer: cart.customer?.name || null,
				customer_name: cart.customer?.customer_name || null,
				note: note || undefined,
			}),
		})
		const data = await res.json()
		if (data.message?.success) {
			cart.clearCart()
			cart.clearCustomer()
		}
	} catch (e) {
		console.error('Hold cart failed:', e)
	} finally {
		holdingCart.value = false
	}
}

function startLayaway() {
	emit('close')
	showCheckout.value = false
	ui.closeLayawayPayment()
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

function updateQty(index, newQty) {
	if (newQty <= 0) {
		cart.removeItem(index)
	} else {
		cart.updateItemQuantity(index, newQty)
	}
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
