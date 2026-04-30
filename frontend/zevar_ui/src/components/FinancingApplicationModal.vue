<template>
	<BaseModal :show="show" max-width="max-w-2xl" :show-close="true" @close="close">
		<div class="p-6" style="min-height: 400px;">
			<!-- Step 1: Customer Info -->
			<template v-if="step === 'info'">
				<h2 class="text-xl font-bold text-gray-900 dark:text-white mb-1">Apply for Financing</h2>
				<p class="text-sm text-gray-500 dark:text-gray-400 mb-6">We'll try each provider in order until you're approved.</p>

				<div class="grid grid-cols-2 gap-4 mb-4">
					<div>
						<label class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1 block">First Name *</label>
						<input v-model="form.firstName" type="text" class="w-full px-3 py-2 bg-white dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm" />
					</div>
					<div>
						<label class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1 block">Last Name *</label>
						<input v-model="form.lastName" type="text" class="w-full px-3 py-2 bg-white dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm" />
					</div>
				</div>
				<div class="grid grid-cols-2 gap-4 mb-4">
					<div>
						<label class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1 block">Email</label>
						<input v-model="form.email" type="email" class="w-full px-3 py-2 bg-white dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm" />
					</div>
					<div>
						<label class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1 block">Phone</label>
						<input v-model="form.phone" type="tel" class="w-full px-3 py-2 bg-white dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm" />
					</div>
				</div>
				<div class="grid grid-cols-2 gap-4 mb-4">
					<div>
						<label class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1 block">Monthly Income</label>
						<input v-model.number="form.monthlyIncome" type="number" class="w-full px-3 py-2 bg-white dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm" />
					</div>
					<div>
						<label class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1 block">SSN Last 4</label>
						<input v-model="form.ssnLast4" type="text" maxlength="4" class="w-full px-3 py-2 bg-white dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm font-mono" />
					</div>
				</div>
				<div class="mb-4">
					<label class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1 block">Address</label>
					<input v-model="form.addressLine1" type="text" placeholder="Street Address" class="w-full px-3 py-2 bg-white dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm mb-2" />
					<div class="grid grid-cols-3 gap-2">
						<input v-model="form.city" type="text" placeholder="City" class="px-3 py-2 bg-white dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm" />
						<input v-model="form.state" type="text" placeholder="State" maxlength="2" class="px-3 py-2 bg-white dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm" />
						<input v-model="form.zipCode" type="text" placeholder="ZIP" class="px-3 py-2 bg-white dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm" />
					</div>
				</div>

				<div v-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/30 rounded-xl p-3 mb-4">
					<p class="text-sm text-red-600 dark:text-red-400">{{ error }}</p>
				</div>

				<button @click="submitWaterfall" :disabled="!canSubmitInfo || submitting"
					class="w-full py-3 rounded-xl font-bold text-lg transition-all flex items-center justify-center gap-2"
					:class="!canSubmitInfo || submitting ? 'bg-gray-100 text-gray-400 dark:bg-warm-dark-700 dark:text-gray-600' : 'bg-gray-900 text-white dark:bg-[#D4AF37] dark:text-black'">
					<span v-if="submitting" class="animate-spin rounded-full h-5 w-5 border-2 border-gray-400 border-t-white"></span>
					<span v-else>Apply for Financing</span>
				</button>
			</template>

			<!-- Step 2: Processing / Results -->
			<template v-if="step === 'results'">
				<h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Financing Application Results</h2>
				<div class="space-y-3 mb-6">
					<div v-for="result in waterfallResults" :key="result.provider"
						class="flex items-center justify-between p-4 border rounded-xl"
						:class="{
							'border-green-300 bg-green-50 dark:bg-green-900/20 dark:border-green-800': result.status === 'approved',
							'border-red-200 bg-red-50 dark:bg-red-900/10 dark:border-red-800/30': result.status === 'denied',
							'border-gray-200 bg-gray-50 dark:bg-warm-dark-700 dark:border-warm-border': result.status === 'skipped' || result.status === 'error',
						}">
						<div class="flex items-center gap-3">
							<div class="w-8 h-8 rounded-full flex items-center justify-center"
								:class="result.status === 'approved' ? 'bg-green-200 text-green-600' : result.status === 'denied' ? 'bg-red-200 text-red-600' : 'bg-gray-200 text-gray-400'">
								<svg v-if="result.status === 'approved'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" /></svg>
								<svg v-else-if="result.status === 'denied'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12" /></svg>
								<svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
							</div>
							<div>
								<span class="font-medium text-gray-900 dark:text-white text-sm">{{ result.provider }}</span>
								<span v-if="result.status === 'approved' && result.approval_amount" class="block text-xs text-green-600 dark:text-green-400">
									Approved: {{ formatCurrency(result.approval_amount) }}
								</span>
								<span v-else-if="result.error" class="block text-xs text-red-500">{{ result.error }}</span>
							</div>
						</div>
						<span class="text-xs font-bold uppercase"
							:class="result.status === 'approved' ? 'text-green-600' : result.status === 'denied' ? 'text-red-500' : 'text-gray-400'">
							{{ result.status }}
						</span>
					</div>
				</div>

				<div v-if="approvedResult" class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800/30 rounded-xl p-5 mb-4 text-center">
					<h3 class="text-lg font-bold text-green-700 dark:text-green-400 mb-1">Approved by {{ approvedResult.provider }}!</h3>
					<p class="text-2xl font-bold text-green-700 dark:text-green-400">{{ formatCurrency(approvedResult.approval_amount) }}</p>
					<p class="text-sm text-green-600 dark:text-green-500 mt-1">Application ID: {{ approvedResult.application_id }}</p>
				</div>

				<div v-else-if="waterfallResults.length > 0" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/30 rounded-xl p-5 mb-4 text-center">
					<h3 class="text-lg font-bold text-red-700 dark:text-red-400 mb-1">Not Approved</h3>
					<p class="text-sm text-red-600 dark:text-red-500">All financing providers were unable to approve at this time.</p>
				</div>

				<button @click="close" class="w-full py-3 rounded-xl font-bold bg-gray-900 dark:bg-[#D4AF37] text-white dark:text-black hover:bg-gray-800 dark:hover:bg-[#b5952f] transition">
					Done
				</button>
			</template>
		</div>
	</BaseModal>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { createResource } from 'frappe-ui'
import { useCartStore } from '@/stores/cart.js'
import BaseModal from './BaseModal.vue'

const props = defineProps({
	show: { type: Boolean, default: false },
	customer: { type: String, default: '' },
	amount: { type: Number, default: 0 },
})
const emit = defineEmits(['close', 'approved'])

const cart = useCartStore()
const step = ref('info')
const submitting = ref(false)
const error = ref('')
const waterfallResults = ref([])

const form = ref({
	firstName: '',
	lastName: '',
	email: '',
	phone: '',
	monthlyIncome: null,
	ssnLast4: '',
	addressLine1: '',
	city: '',
	state: '',
	zipCode: '',
})

const canSubmitInfo = computed(() => form.value.firstName && form.value.lastName)

const approvedResult = computed(() => waterfallResults.value.find(r => r.status === 'approved'))

async function submitWaterfall() {
	if (!canSubmitInfo.value) return
	submitting.value = true
	error.value = ''
	try {
		const resource = createResource({
			url: 'zevar_core.integrations.waterfall.start_financing_waterfall',
			auto: false,
		})
		const result = await resource.submit({
			customer: props.customer || cart.customerId || 'Walk-In Customer',
			first_name: form.value.firstName,
			last_name: form.value.lastName,
			email: form.value.email || undefined,
			phone: form.value.phone || undefined,
			monthly_income: form.value.monthlyIncome || undefined,
			requested_amount: props.amount || cart.grandTotal,
			ssn_last4: form.value.ssnLast4 || undefined,
			address_line1: form.value.addressLine1 || undefined,
			city: form.value.city || undefined,
			state: form.value.state || undefined,
			zip_code: form.value.zipCode || undefined,
		})
		const data = result?.message ?? result
		waterfallResults.value = data?.waterfall_results || []
		step.value = 'results'
		if (approvedResult.value) {
			emit('approved', approvedResult.value)
		}
	} catch (e) {
		error.value = e?.message || 'Failed to submit application'
	} finally {
		submitting.value = false
	}
}

watch(() => props.show, (isOpen) => {
	if (isOpen) {
		step.value = 'info'
		submitting.value = false
		error.value = ''
		waterfallResults.value = []
	}
})

function close() {
	emit('close')
}

function formatCurrency(val) {
	if (!val) return '$0.00'
	return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val)
}
</script>
