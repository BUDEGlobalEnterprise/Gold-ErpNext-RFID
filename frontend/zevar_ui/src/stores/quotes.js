import { defineStore } from 'pinia'
import { createResource } from 'frappe-ui'
import { ref } from 'vue'

export const useQuotesStore = defineStore('quotes', () => {
	const quotes = ref([])
	const quotesTotal = ref(0)
	const currentQuote = ref(null)

	const quotesResource = createResource({
		url: 'zevar_core.api.quotes.get_quotations',
		onSuccess(data) {
			quotes.value = data.quotes || []
			quotesTotal.value = data.total || 0
		},
	})

	const quoteDetailResource = createResource({
		url: 'zevar_core.api.quotes.get_quotation_detail',
		onSuccess(data) {
			currentQuote.value = data.quote || null
		},
	})

	const createQuoteResource = createResource({
		url: 'zevar_core.api.quotes.create_quotation',
	})

	const submitQuoteResource = createResource({
		url: 'zevar_core.api.quotes.submit_quotation',
	})

	const updateStatusResource = createResource({
		url: 'zevar_core.api.quotes.update_quotation_status',
	})

	const convertToOrderResource = createResource({
		url: 'zevar_core.api.quotes.convert_to_order',
	})

	const convertToInvoiceResource = createResource({
		url: 'zevar_core.api.quotes.convert_to_invoice',
	})

	const cancelQuoteResource = createResource({
		url: 'zevar_core.api.quotes.cancel_quotation',
	})

	function loadQuotes(params = {}) {
		return quotesResource.submit(params)
	}

	function loadQuoteDetail(name) {
		return quoteDetailResource.submit({ name })
	}

	function createQuote(customer, items_json, valid_till, order_type) {
		return createQuoteResource.submit({ customer, items_json, valid_till, order_type })
	}

	function submitQuote(name) {
		return submitQuoteResource.submit({ name })
	}

	function updateStatus(name, status) {
		return updateStatusResource.submit({ name, status })
	}

	function convertToOrder(name) {
		return convertToOrderResource.submit({ name })
	}

	function convertToInvoice(name) {
		return convertToInvoiceResource.submit({ name })
	}

	function cancelQuote(name) {
		return cancelQuoteResource.submit({ name })
	}

	return {
		quotes,
		quotesTotal,
		currentQuote,
		quotesResource,
		quoteDetailResource,
		createQuoteResource,
		submitQuoteResource,
		updateStatusResource,
		convertToOrderResource,
		convertToInvoiceResource,
		cancelQuoteResource,
		loadQuotes,
		loadQuoteDetail,
		createQuote,
		submitQuote,
		updateStatus,
		convertToOrder,
		convertToInvoice,
		cancelQuote,
	}
})
