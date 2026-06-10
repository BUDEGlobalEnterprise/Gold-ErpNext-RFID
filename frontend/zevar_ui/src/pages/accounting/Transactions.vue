<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<div class="flex items-center gap-3">
					<h2 class="premium-title !text-xl sm:!text-2xl">Transactions</h2>
					<span
						class="status-label !mb-0 !bg-gray-100 dark:!bg-warm-dark-700 !text-gray-600 dark:!text-white/60 !px-4 !py-1 !rounded-full !border !border-gray-200 dark:!border-warm-border"
					>
						{{ store.transactionsTotal }} Records
					</span>
				</div>
				<div class="flex items-center gap-2">
					<button
						@click="loadData"
						class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-warm-dark-700"
						title="Refresh"
					>
						<svg
							class="w-4 h-4 text-gray-500"
							:class="{ 'animate-spin': store.transactionsResource.loading }"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357 2m15.357 2H15"
							/>
						</svg>
					</button>
					<button
						@click="showPaymentModal = true"
						class="flex items-center gap-1.5 px-3 py-2 bg-[#D4AF37] text-white rounded-lg text-xs font-bold hover:bg-[#C4A030] transition"
					>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 6v6m0 0v6m0-6h6m-6 0H6"
							/>
						</svg>
						Payment
					</button>
					<button
						@click="showJournalModal = true"
						class="flex items-center gap-1.5 px-3 py-2 bg-gray-800 dark:bg-warm-dark-600 text-white rounded-lg text-xs font-bold hover:bg-gray-700 transition"
					>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 6v6m0 0v6m0-6h6m-6 0H6"
							/>
						</svg>
						Journal
					</button>
				</div>
			</div>

			<div class="flex flex-wrap gap-2 mb-4 flex-shrink-0">
				<button
					v-for="f in typeFilters"
					:key="f.value"
					@click="activeType = f.value"
					class="px-3 py-1.5 rounded-full text-xs font-bold transition"
					:class="
						activeType === f.value
							? 'bg-[#D4AF37] text-white'
							: 'bg-gray-100 dark:bg-warm-dark-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-warm-dark-600'
					"
				>
					{{ f.label }}
				</button>
			</div>

			<div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4 flex-shrink-0">
				<div class="premium-card !p-4">
					<div
						class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1"
					>
						Total Records
					</div>
					<div class="text-2xl font-bold text-gray-900 dark:text-white">
						{{ store.transactionsTotal }}
					</div>
				</div>
				<div class="premium-card !p-4">
					<div
						class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1"
					>
						Payments
					</div>
					<div class="text-2xl font-bold text-emerald-500">{{ paymentCount }}</div>
				</div>
				<div class="premium-card !p-4">
					<div
						class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1"
					>
						Journals
					</div>
					<div class="text-2xl font-bold text-blue-500">{{ journalCount }}</div>
				</div>
				<div class="premium-card !p-4">
					<div
						class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1"
					>
						Total Value
					</div>
					<div class="text-2xl font-bold text-[#D4AF37]">
						{{ formatCurrency(totalValue) }}
					</div>
				</div>
			</div>

			<div class="flex-1 overflow-y-auto min-h-0">
				<div
					v-if="store.transactionsResource.loading && !store.transactions.length"
					class="flex items-center justify-center py-20"
				>
					<div
						class="animate-spin w-8 h-8 border-2 border-[#D4AF37] border-t-transparent rounded-full"
					></div>
				</div>
				<div
					v-else-if="!store.transactions.length"
					class="flex flex-col items-center justify-center py-20 text-gray-400 dark:text-gray-500"
				>
					<svg
						class="w-12 h-12 mb-3"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="1.5"
							d="M9 14l6-6m-5.5.5h.01m4.99 5h.01M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16l3.5-2 3.5 2 3.5-2 3.5 2z"
						/>
					</svg>
					<p class="text-sm font-medium">No transactions found</p>
				</div>
				<div v-else class="space-y-2">
					<div
						v-for="txn in store.transactions"
						:key="txn.name"
						class="premium-card !p-4 flex items-center justify-between cursor-pointer hover:ring-1 hover:ring-[#D4AF37]/30 transition"
						@click="viewDetail(txn)"
					>
						<div class="flex items-center gap-3 min-w-0">
							<div
								class="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0"
								:class="
									txn.doctype === 'Payment Entry'
										? 'bg-emerald-100 dark:bg-emerald-900/30'
										: 'bg-blue-100 dark:bg-blue-900/30'
								"
							>
								<svg
									class="w-4 h-4"
									:class="
										txn.doctype === 'Payment Entry'
											? 'text-emerald-600'
											: 'text-blue-600'
									"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										v-if="txn.doctype === 'Payment Entry'"
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
									/>
									<path
										v-else
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
									/>
								</svg>
							</div>
							<div class="min-w-0">
								<div
									class="text-sm font-bold text-gray-900 dark:text-white truncate"
								>
									{{ txn.name }}
								</div>
								<div class="text-[11px] text-gray-500 dark:text-gray-400 truncate">
									{{
										txn.doctype === 'Payment Entry'
											? txn.payment_type
											: txn.mode_of_payment
									}}
									<span v-if="txn.party_name">
										&middot; {{ txn.party_name }}</span
									>
								</div>
							</div>
						</div>
						<div class="text-right flex-shrink-0 ml-3">
							<div
								class="text-sm font-bold"
								:class="txn.paid_amount >= 0 ? 'text-emerald-600' : 'text-red-500'"
							>
								{{ formatCurrency(txn.paid_amount) }}
							</div>
							<div class="text-[10px] text-gray-400">{{ txn.posting_date }}</div>
							<span
								class="inline-block mt-1 px-2 py-0.5 rounded-full text-[9px] font-bold"
								:class="statusClass(txn)"
							>
								{{ statusLabel(txn) }}
							</span>
						</div>
					</div>
				</div>
			</div>
		</div>

		<div
			v-if="showPaymentModal"
			class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
			@click.self="showPaymentModal = false"
		>
			<div class="premium-card !p-6 w-full max-w-md mx-4 max-h-[90vh] overflow-y-auto">
				<h3 class="premium-title !text-lg mb-4">Create Payment Entry</h3>
				<div class="space-y-3">
					<div>
						<label
							class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase mb-1 block"
							>Payment Type</label
						>
						<select v-model="paymentForm.payment_type" class="form-input">
							<option value="Receive">Receive</option>
							<option value="Pay">Pay</option>
							<option value="Internal Transfer">Internal Transfer</option>
						</select>
					</div>
					<div>
						<label
							class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase mb-1 block"
							>Party</label
						>
						<input
							v-model="paymentForm.party"
							class="form-input"
							placeholder="Customer or Supplier"
						/>
					</div>
					<div>
						<label
							class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase mb-1 block"
							>Amount</label
						>
						<input
							v-model.number="paymentForm.paid_amount"
							type="number"
							class="form-input"
							placeholder="0.00"
						/>
					</div>
					<div>
						<label
							class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase mb-1 block"
							>Mode of Payment</label
						>
						<select v-model="paymentForm.mode_of_payment" class="form-input">
							<option
								v-for="m in store.modesOfPayment"
								:key="m.name"
								:value="m.name"
							>
								{{ m.name }}
							</option>
						</select>
					</div>
					<div>
						<label
							class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase mb-1 block"
							>Reference No</label
						>
						<input
							v-model="paymentForm.reference_no"
							class="form-input"
							placeholder="Optional"
						/>
					</div>
				</div>
				<div class="flex gap-2 mt-5">
					<button
						@click="showPaymentModal = false"
						class="flex-1 px-4 py-2 rounded-lg text-xs font-bold bg-gray-100 dark:bg-warm-dark-700 text-gray-600 dark:text-gray-300"
					>
						Cancel
					</button>
					<button
						@click="submitPayment"
						class="flex-1 px-4 py-2 rounded-lg text-xs font-bold bg-[#D4AF37] text-white hover:bg-[#C4A030]"
						:disabled="store.createPaymentEntryResource.loading"
					>
						{{ store.createPaymentEntryResource.loading ? 'Creating...' : 'Create' }}
					</button>
				</div>
			</div>
		</div>

		<div
			v-if="showJournalModal"
			class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
			@click.self="showJournalModal = false"
		>
			<div class="premium-card !p-6 w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
				<h3 class="premium-title !text-lg mb-4">Create Journal Entry</h3>
				<div class="space-y-3">
					<div>
						<label
							class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase mb-1 block"
							>Voucher Type</label
						>
						<select v-model="journalForm.voucher_type" class="form-input">
							<option value="Journal Entry">Journal Entry</option>
							<option value="Bank Entry">Bank Entry</option>
							<option value="Cash Entry">Cash Entry</option>
							<option value="Credit Note">Credit Note</option>
							<option value="Debit Note">Debit Note</option>
						</select>
					</div>
					<div>
						<label
							class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase mb-1 block"
							>Remark</label
						>
						<input
							v-model="journalForm.user_remark"
							class="form-input"
							placeholder="Optional"
						/>
					</div>
					<div>
						<label
							class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase mb-1 block"
							>Account Entries</label
						>
						<div
							v-for="(row, i) in journalForm.accounts"
							:key="i"
							class="flex gap-2 mb-2"
						>
							<select v-model="row.account" class="form-input flex-1">
								<option value="">Select Account</option>
								<option v-for="a in store.accounts" :key="a.name" :value="a.name">
									{{ a.account_name }}
								</option>
							</select>
							<input
								v-model.number="row.debit"
								type="number"
								class="form-input w-20"
								placeholder="Dr"
							/>
							<input
								v-model.number="row.credit"
								type="number"
								class="form-input w-20"
								placeholder="Cr"
							/>
							<button
								@click="journalForm.accounts.splice(i, 1)"
								class="text-red-400 hover:text-red-600 px-1"
							>
								&times;
							</button>
						</div>
						<button
							@click="
								journalForm.accounts.push({ account: '', debit: 0, credit: 0 })
							"
							class="text-xs text-[#D4AF37] font-bold hover:underline"
						>
							+ Add Row
						</button>
					</div>
				</div>
				<div class="flex gap-2 mt-5">
					<button
						@click="showJournalModal = false"
						class="flex-1 px-4 py-2 rounded-lg text-xs font-bold bg-gray-100 dark:bg-warm-dark-700 text-gray-600 dark:text-gray-300"
					>
						Cancel
					</button>
					<button
						@click="submitJournal"
						class="flex-1 px-4 py-2 rounded-lg text-xs font-bold bg-[#D4AF37] text-white hover:bg-[#C4A030]"
						:disabled="store.createJournalEntryResource.loading"
					>
						{{ store.createJournalEntryResource.loading ? 'Creating...' : 'Create' }}
					</button>
				</div>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '../../components/AppLayout.vue'
import { useAccountingStore } from '../../stores/accounting'

const store = useAccountingStore()

const activeType = ref('all')
const showPaymentModal = ref(false)
const showJournalModal = ref(false)

const paymentForm = ref({
	payment_type: 'Receive',
	party: '',
	paid_amount: 0,
	mode_of_payment: 'Cash',
	reference_no: '',
})

const journalForm = ref({
	voucher_type: 'Journal Entry',
	user_remark: '',
	accounts: [{ account: '', debit: 0, credit: 0 }],
})

const typeFilters = [
	{ label: 'All', value: 'all' },
	{ label: 'Payments', value: 'Payment Entry' },
	{ label: 'Journals', value: 'Journal Entry' },
]

const paymentCount = computed(
	() => store.transactions.filter((t) => t.doctype === 'Payment Entry').length
)
const journalCount = computed(
	() => store.transactions.filter((t) => t.doctype === 'Journal Entry').length
)
const totalValue = computed(() =>
	store.transactions.reduce((sum, t) => sum + (t.paid_amount || 0), 0)
)

function formatCurrency(val) {
	return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val || 0)
}

function statusClass(txn) {
	if (txn.docstatus === 0)
		return 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
	if (txn.docstatus === 1)
		return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
	return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
}

function statusLabel(txn) {
	if (txn.docstatus === 0) return 'Draft'
	if (txn.docstatus === 1) return 'Submitted'
	return 'Cancelled'
}

function loadData() {
	store.loadTransactions({ doctype: activeType.value === 'all' ? undefined : activeType.value })
}

function viewDetail(txn) {
	window.open(`/app/${txn.doctype.toLowerCase().replace(/ /g, '-')}/${txn.name}`, '_blank')
}

async function submitPayment() {
	const f = paymentForm.value
	await store.createPaymentEntry(f.payment_type, f.party, f.paid_amount, f.mode_of_payment, {
		reference_no: f.reference_no,
	})
	showPaymentModal.value = false
	paymentForm.value = {
		payment_type: 'Receive',
		party: '',
		paid_amount: 0,
		mode_of_payment: 'Cash',
		reference_no: '',
	}
	loadData()
}

async function submitJournal() {
	const f = journalForm.value
	await store.createJournalEntry(JSON.stringify(f.accounts), f.voucher_type, f.user_remark)
	showJournalModal.value = false
	journalForm.value = {
		voucher_type: 'Journal Entry',
		user_remark: '',
		accounts: [{ account: '', debit: 0, credit: 0 }],
	}
	loadData()
}

onMounted(() => {
	loadData()
	store.loadModesOfPayment()
	store.loadAccounts()
})
</script>
