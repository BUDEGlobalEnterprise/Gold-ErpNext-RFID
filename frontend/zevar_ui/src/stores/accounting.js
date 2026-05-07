import { defineStore } from 'pinia'
import { createResource } from 'frappe-ui'
import { ref, computed } from 'vue'

export const useAccountingStore = defineStore('accounting', () => {
	const transactions = ref([])
	const transactionsTotal = ref(0)
	const currentTransaction = ref(null)

	const terminals = ref([])
	const terminalsTotal = ref(0)
	const terminalStatus = ref(null)

	const invoices = ref([])
	const invoicesTotal = ref(0)
	const currentInvoice = ref(null)

	const creditNotes = ref([])
	const creditNotesTotal = ref(0)

	const accounts = ref([])
	const modesOfPayment = ref([])

	const transactionsResource = createResource({
		url: 'zevar_core.api.accounting.get_transactions',
		onSuccess(data) {
			transactions.value = data.transactions || []
			transactionsTotal.value = data.total || 0
		},
	})

	const transactionDetailResource = createResource({
		url: 'zevar_core.api.accounting.get_transaction_detail',
		onSuccess(data) {
			currentTransaction.value = data.transaction || null
		},
	})

	const createPaymentEntryResource = createResource({
		url: 'zevar_core.api.accounting.create_payment_entry',
	})

	const createJournalEntryResource = createResource({
		url: 'zevar_core.api.accounting.create_journal_entry',
	})

	const submitTransactionResource = createResource({
		url: 'zevar_core.api.accounting.submit_transaction',
	})

	const cancelTransactionResource = createResource({
		url: 'zevar_core.api.accounting.cancel_transaction',
	})

	const terminalsResource = createResource({
		url: 'zevar_core.api.accounting.get_terminals',
		onSuccess(data) {
			terminals.value = data.terminals || []
			terminalsTotal.value = data.total || 0
		},
	})

	const terminalStatusResource = createResource({
		url: 'zevar_core.api.accounting.get_terminal_status',
		onSuccess(data) {
			terminalStatus.value = data
		},
	})

	const invoicesResource = createResource({
		url: 'zevar_core.api.accounting.get_invoices',
		onSuccess(data) {
			invoices.value = data.invoices || []
			invoicesTotal.value = data.total || 0
		},
	})

	const invoiceDetailResource = createResource({
		url: 'zevar_core.api.accounting.get_invoice_detail',
		onSuccess(data) {
			currentInvoice.value = data.invoice || null
		},
	})

	const submitInvoiceResource = createResource({
		url: 'zevar_core.api.accounting.submit_invoice',
	})

	const cancelInvoiceResource = createResource({
		url: 'zevar_core.api.accounting.cancel_invoice',
	})

	const creditNotesResource = createResource({
		url: 'zevar_core.api.accounting.get_credit_notes',
		onSuccess(data) {
			creditNotes.value = data.credit_notes || []
			creditNotesTotal.value = data.total || 0
		},
	})

	const createCreditNoteResource = createResource({
		url: 'zevar_core.api.accounting.create_credit_note',
	})

	const exportableInvoicesResource = createResource({
		url: 'zevar_core.api.accounting.get_exportable_invoices',
	})

	const exportUBLResource = createResource({
		url: 'zevar_core.api.accounting.export_ubl',
	})

	const accountsResource = createResource({
		url: 'zevar_core.api.accounting.get_accounts',
		onSuccess(data) {
			accounts.value = data.accounts || []
		},
	})

	const modesOfPaymentResource = createResource({
		url: 'zevar_core.api.accounting.get_modes_of_payment',
		onSuccess(data) {
			modesOfPayment.value = data.modes || []
		},
	})

	function loadTransactions(params = {}) {
		return transactionsResource.submit(params)
	}

	function loadTransactionDetail(doctype, name) {
		return transactionDetailResource.submit({ doctype, name })
	}

	function createPaymentEntry(payment_type, party, paid_amount, mode_of_payment, opts = {}) {
		return createPaymentEntryResource.submit({
			payment_type,
			party,
			paid_amount,
			mode_of_payment,
			...opts,
		})
	}

	function createJournalEntry(accounts_json, voucher_type, user_remark) {
		return createJournalEntryResource.submit({ accounts_json, voucher_type, user_remark })
	}

	function submitTransaction(doctype, name) {
		return submitTransactionResource.submit({ doctype, name })
	}

	function cancelTransaction(doctype, name) {
		return cancelTransactionResource.submit({ doctype, name })
	}

	function loadTerminals(params = {}) {
		return terminalsResource.submit(params)
	}

	function loadTerminalStatus(name) {
		return terminalStatusResource.submit({ name })
	}

	function loadInvoices(params = {}) {
		return invoicesResource.submit(params)
	}

	function loadInvoiceDetail(invoice_type, name) {
		return invoiceDetailResource.submit({ invoice_type, name })
	}

	function submitInvoice(invoice_type, name) {
		return submitInvoiceResource.submit({ invoice_type, name })
	}

	function cancelInvoice(invoice_type, name) {
		return cancelInvoiceResource.submit({ invoice_type, name })
	}

	function loadCreditNotes(params = {}) {
		return creditNotesResource.submit(params)
	}

	function createCreditNote(invoice_type, return_against, reason) {
		return createCreditNoteResource.submit({ invoice_type, return_against, reason })
	}

	function loadExportableInvoices(params = {}) {
		return exportableInvoicesResource.submit(params)
	}

	function exportUBL(invoices_json) {
		return exportUBLResource.submit({ invoices_json })
	}

	function loadAccounts(company) {
		return accountsResource.submit({ company })
	}

	function loadModesOfPayment() {
		return modesOfPaymentResource.submit()
	}

	function clearInvoiceDetail() {
		currentInvoice.value = null
	}

	function clearTransactionDetail() {
		currentTransaction.value = null
	}

	return {
		transactions,
		transactionsTotal,
		currentTransaction,
		terminals,
		terminalsTotal,
		terminalStatus,
		invoices,
		invoicesTotal,
		currentInvoice,
		creditNotes,
		creditNotesTotal,
		accounts,
		modesOfPayment,

		transactionsResource,
		transactionDetailResource,
		createPaymentEntryResource,
		createJournalEntryResource,
		submitTransactionResource,
		cancelTransactionResource,
		terminalsResource,
		terminalStatusResource,
		invoicesResource,
		invoiceDetailResource,
		submitInvoiceResource,
		cancelInvoiceResource,
		creditNotesResource,
		createCreditNoteResource,
		exportableInvoicesResource,
		exportUBLResource,
		accountsResource,
		modesOfPaymentResource,

		loadTransactions,
		loadTransactionDetail,
		createPaymentEntry,
		createJournalEntry,
		submitTransaction,
		cancelTransaction,
		loadTerminals,
		loadTerminalStatus,
		loadInvoices,
		loadInvoiceDetail,
		submitInvoice,
		cancelInvoice,
		loadCreditNotes,
		createCreditNote,
		loadExportableInvoices,
		exportUBL,
		loadAccounts,
		loadModesOfPayment,
		clearInvoiceDetail,
		clearTransactionDetail,
	}
})
