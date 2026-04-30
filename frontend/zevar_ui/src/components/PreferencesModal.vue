<template>
	<BaseModal :show="show" max-width="max-w-lg" @close="close">
		<template #header>
			<h2 class="text-lg font-bold text-gray-900 dark:text-white">POS Preferences</h2>
		</template>

		<!-- Default Behavior -->
		<div class="space-y-6 p-6">
			<div>
				<h4
					class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3"
				>
					Default Behavior
				</h4>

				<div class="space-y-3">
					<div
						class="flex items-center justify-between py-3 border-b border-gray-100 dark:border-warm-border/50"
					>
						<div class="flex-1">
							<span class="block text-sm font-medium text-gray-900 dark:text-white"
								>Auto-print Receipt</span
							>
							<span class="block text-xs text-gray-500 dark:text-gray-400 mt-0.5"
								>Automatically print receipt after each sale</span
							>
						</div>
						<label class="relative inline-flex items-center cursor-pointer">
							<input
								type="checkbox"
								v-model="prefs.auto_print_receipt"
								@change="savePrefs"
								class="sr-only peer"
							/>
							<div
								class="w-11 h-6 bg-gray-200 dark:bg-warm-dark-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"
							></div>
						</label>
					</div>

					<div
						class="flex items-center justify-between py-3 border-b border-gray-100 dark:border-warm-border/50"
					>
						<div class="flex-1">
							<span class="block text-sm font-medium text-gray-900 dark:text-white"
								>Auto-email Receipt</span
							>
							<span class="block text-xs text-gray-500 dark:text-gray-400 mt-0.5"
								>Send receipt to customer email</span
							>
						</div>
						<label class="relative inline-flex items-center cursor-pointer">
							<input
								type="checkbox"
								v-model="prefs.auto_email_receipt"
								@change="savePrefs"
								class="sr-only peer"
							/>
							<div
								class="w-11 h-6 bg-gray-200 dark:bg-warm-dark-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"
							></div>
						</label>
					</div>

					<div
						class="flex items-center justify-between py-3 border-b border-gray-100 dark:border-warm-border/50"
					>
						<div class="flex-1">
							<span class="block text-sm font-medium text-gray-900 dark:text-white"
								>Ask for Customer</span
							>
							<span class="block text-xs text-gray-500 dark:text-gray-400 mt-0.5"
								>Prompt to select customer before checkout</span
							>
						</div>
						<label class="relative inline-flex items-center cursor-pointer">
							<input
								type="checkbox"
								v-model="prefs.ask_for_customer"
								@change="savePrefs"
								class="sr-only peer"
							/>
							<div
								class="w-11 h-6 bg-gray-200 dark:bg-warm-dark-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"
							></div>
						</label>
					</div>

					<div
						class="flex items-center justify-between py-3 border-b border-gray-100 dark:border-warm-border/50"
					>
						<div class="flex-1">
							<span class="block text-sm font-medium text-gray-900 dark:text-white"
								>Confirm Void</span
							>
							<span class="block text-xs text-gray-500 dark:text-gray-400 mt-0.5"
								>Require confirmation before voiding</span
							>
						</div>
						<label class="relative inline-flex items-center cursor-pointer">
							<input
								type="checkbox"
								v-model="prefs.confirm_void"
								@change="savePrefs"
								class="sr-only peer"
							/>
							<div
								class="w-11 h-6 bg-gray-200 dark:bg-warm-dark-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"
							></div>
						</label>
					</div>
				</div>
			</div>

			<!-- Receipt Settings -->
			<div>
				<h4
					class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3"
				>
					Receipt Settings
				</h4>

				<div class="space-y-3">
					<div
						class="flex items-center justify-between py-3 border-b border-gray-100 dark:border-warm-border/50"
					>
						<div class="flex-1">
							<span class="block text-sm font-medium text-gray-900 dark:text-white"
								>Receipt Format</span
							>
						</div>
						<select
							v-model="prefs.receipt_format"
							@change="savePrefs"
							class="px-3 py-1.5 bg-gray-100 dark:bg-white/10 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white min-w-[120px]"
						>
							<option value="thermal">Thermal (80mm)</option>
							<option value="standard">Standard (A4)</option>
							<option value="compact">Compact</option>
						</select>
					</div>

					<div
						class="flex items-center justify-between py-3 border-b border-gray-100 dark:border-warm-border/50"
					>
						<div class="flex-1">
							<span class="block text-sm font-medium text-gray-900 dark:text-white"
								>Show Tax Breakdown</span
							>
							<span class="block text-xs text-gray-500 dark:text-gray-400 mt-0.5"
								>Display tax details on receipt</span
							>
						</div>
						<label class="relative inline-flex items-center cursor-pointer">
							<input
								type="checkbox"
								v-model="prefs.show_tax_breakdown"
								@change="savePrefs"
								class="sr-only peer"
							/>
							<div
								class="w-11 h-6 bg-gray-200 dark:bg-warm-dark-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"
							></div>
						</label>
					</div>

					<div
						class="flex items-center justify-between py-3 border-b border-gray-100 dark:border-warm-border/50"
					>
						<div class="flex-1">
							<span class="block text-sm font-medium text-gray-900 dark:text-white"
								>Print Item Details</span
							>
							<span class="block text-xs text-gray-500 dark:text-gray-400 mt-0.5"
								>Include item descriptions on receipt</span
							>
						</div>
						<label class="relative inline-flex items-center cursor-pointer">
							<input
								type="checkbox"
								v-model="prefs.print_item_details"
								@change="savePrefs"
								class="sr-only peer"
							/>
							<div
								class="w-11 h-6 bg-gray-200 dark:bg-warm-dark-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"
							></div>
						</label>
					</div>

					<div
						class="flex items-center justify-between py-3 border-b border-gray-100 dark:border-warm-border/50"
					>
						<div class="flex-1">
							<span class="block text-sm font-medium text-gray-900 dark:text-white"
								>Receipt Footer</span
							>
							<span class="block text-xs text-gray-500 dark:text-gray-400 mt-0.5"
								>Custom message on receipts</span
							>
						</div>
						<input
							type="text"
							v-model="prefs.receipt_footer"
							placeholder="Thank you for shopping with us!"
							@change="savePrefs"
							class="px-3 py-1.5 bg-gray-100 dark:bg-white/10 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white flex-1 max-w-[200px] ml-4"
						/>
					</div>
				</div>
			</div>

			<!-- Payment Defaults -->
			<div>
				<h4
					class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3"
				>
					Payment Defaults
				</h4>

				<div class="space-y-3">
					<div
						class="flex items-center justify-between py-3 border-b border-gray-100 dark:border-warm-border/50"
					>
						<div class="flex-1">
							<span class="block text-sm font-medium text-gray-900 dark:text-white"
								>Default Payment Method</span
							>
						</div>
						<select
							v-model="prefs.default_payment_method"
							@change="savePrefs"
							class="px-3 py-1.5 bg-gray-100 dark:bg-white/10 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white min-w-[120px]"
						>
							<option value="Cash">Cash</option>
							<option value="Credit Card">Credit Card</option>
							<option value="Debit Card">Debit Card</option>
						</select>
					</div>

					<div
						class="flex items-center justify-between py-3 border-b border-gray-100 dark:border-warm-border/50"
					>
						<div class="flex-1">
							<span class="block text-sm font-medium text-gray-900 dark:text-white"
								>Round to Nearest</span
							>
						</div>
						<select
							v-model="prefs.rounding"
							@change="savePrefs"
							class="px-3 py-1.5 bg-gray-100 dark:bg-white/10 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white min-w-[120px]"
						>
							<option value="0.01">Cent</option>
							<option value="0.05">Nickel</option>
							<option value="0.10">Dime</option>
							<option value="0.25">Quarter</option>
							<option value="1.00">Dollar</option>
						</select>
					</div>
				</div>
			</div>

			<!-- Quick Keys -->
			<div>
				<h4
					class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3"
				>
					Quick Cash Amounts
				</h4>
				<div class="flex flex-wrap gap-2">
					<button
						v-for="amount in quickAmounts"
						:key="amount"
						class="px-4 py-2 text-sm font-medium rounded-full transition-all"
						:class="
							prefs.quick_amounts?.includes(amount)
								? 'bg-blue-600 text-white border-2 border-blue-600'
								: 'bg-gray-100 dark:bg-white/10 text-gray-700 dark:text-gray-300 border-2 border-transparent hover:border-blue-400'
						"
						@click="toggleQuickAmount(amount)"
					>
						${{ amount }}
					</button>
				</div>
				<p class="text-xs text-gray-500 dark:text-gray-400 mt-2">
					Click to toggle quick cash buttons
				</p>
			</div>
		</div>

		<template #footer>
			<button
				class="px-4 py-2 text-sm font-semibold text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-warm-border rounded-lg hover:bg-gray-50 dark:hover:bg-white/10 transition"
				@click="resetPrefs"
			>
				Reset to Defaults
			</button>
			<button
				class="px-4 py-2 text-sm font-semibold bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
				@click="close"
			>
				Done
			</button>
		</template>
	</BaseModal>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import BaseModal from './BaseModal.vue'

const props = defineProps({
	show: { type: Boolean, default: false },
})

const emit = defineEmits(['close'])

const defaultPrefs = {
	auto_print_receipt: true,
	auto_email_receipt: false,
	ask_for_customer: true,
	confirm_void: true,
	receipt_format: 'thermal',
	show_tax_breakdown: true,
	print_item_details: false,
	receipt_footer: 'Thank you for shopping with us!',
	default_payment_method: 'Cash',
	rounding: '0.01',
	quick_amounts: [5, 10, 20, 50, 100],
}

const prefs = ref({ ...defaultPrefs })
const quickAmounts = [1, 5, 10, 20, 50, 100, 200, 500]

function savePrefs() {
	localStorage.setItem('pos_preferences', JSON.stringify(prefs.value))
}

function loadPrefs() {
	const stored = localStorage.getItem('pos_preferences')
	if (stored) {
		try {
			prefs.value = { ...defaultPrefs, ...JSON.parse(stored) }
		} catch {
			prefs.value = { ...defaultPrefs }
		}
	}
}

function resetPrefs() {
	prefs.value = { ...defaultPrefs }
	savePrefs()
}

function toggleQuickAmount(amount) {
	if (!prefs.value.quick_amounts) {
		prefs.value.quick_amounts = []
	}
	const index = prefs.value.quick_amounts.indexOf(amount)
	if (index > -1) {
		prefs.value.quick_amounts.splice(index, 1)
	} else {
		prefs.value.quick_amounts.push(amount)
		prefs.value.quick_amounts.sort((a, b) => a - b)
	}
	savePrefs()
}

function close() {
	emit('close')
}

watch(
	() => props.show,
	(val) => {
		if (val) loadPrefs()
	}
)

onMounted(loadPrefs)
</script>
