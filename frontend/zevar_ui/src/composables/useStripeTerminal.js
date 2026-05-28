/**
 * useStripeTerminal — Vue 3 Composable for Stripe Terminal (Card-Present)
 *
 * Manages the full lifecycle:
 *   1. Dynamically loads the Stripe Terminal JS SDK
 *   2. Fetches connection tokens from the Frappe backend
 *   3. Discovers & connects to a card reader
 *   4. Collects payment via the reader
 *   5. Polls for PaymentIntent status until terminal
 *   6. Exposes reactive state for UI (status, error, receipt)
 *
 * PCI Note: Never logs or stores raw card numbers. The Stripe Terminal SDK
 * handles card data entirely within its PCI-certified scope.
 */
import { ref, readonly, computed, onUnmounted } from 'vue'
import { call } from 'frappe-ui'

// SDK load states
const SDK_STATES = { IDLE: 'idle', LOADING: 'loading', LOADED: 'loaded', ERROR: 'error' }
let sdkState = SDK_STATES.IDLE
let sdkPromise = null

/**
 * Dynamically load the Stripe Terminal JS SDK once.
 * Returns a promise that resolves when the global `StripeTerminal` is available.
 */
function loadStripeTerminalSDK() {
	if (sdkState === SDK_STATES.LOADED && window.StripeTerminal) {
		return Promise.resolve()
	}
	if (sdkState === SDK_STATES.LOADING && sdkPromise) {
		return sdkPromise
	}

	sdkState = SDK_STATES.LOADING
	sdkPromise = new Promise((resolve, reject) => {
		// Prevent duplicate script tags
		if (document.querySelector('script[src*="js.stripe.com/terminal"]')) {
			if (window.StripeTerminal) {
				sdkState = SDK_STATES.LOADED
				resolve()
			} else {
				// Script exists but hasn't loaded yet — wait
				const check = setInterval(() => {
					if (window.StripeTerminal) {
						clearInterval(check)
						sdkState = SDK_STATES.LOADED
						resolve()
					}
				}, 100)
				setTimeout(() => {
					clearInterval(check)
					sdkState = SDK_STATES.ERROR
					reject(new Error('Stripe Terminal SDK timed out'))
				}, 15000)
			}
			return
		}

		const script = document.createElement('script')
		script.src = 'https://js.stripe.com/terminal/v1/'
		script.async = true
		script.onload = () => {
			sdkState = SDK_STATES.LOADED
			resolve()
		}
		script.onerror = () => {
			sdkState = SDK_STATES.ERROR
			reject(new Error('Failed to load Stripe Terminal SDK'))
		}
		document.head.appendChild(script)
	})

	return sdkPromise
}

// Payment flow statuses — ordered progression
export const TERMINAL_STATUS = {
	IDLE: 'idle',
	LOADING_SDK: 'loading_sdk',
	DISCOVERING: 'discovering',
	CONNECTING: 'connecting',
	CREATING_INTENT: 'creating_intent',
	WAITING_FOR_CARD: 'waiting_for_card',
	PROCESSING: 'processing',
	CONFIRMING: 'confirming',
	SUCCEEDED: 'succeeded',
	FAILED: 'failed',
	CANCELED: 'canceled',
}

export function useStripeTerminal() {
	// ── Reactive state ──
	const status = ref(TERMINAL_STATUS.IDLE)
	const error = ref(null)
	const readers = ref([])
	const connectedReader = ref(null)
	const paymentResult = ref(null)
	const receiptUrl = ref(null)
	const statusMessage = ref('')

	// Internal
	let terminalInstance = null
	let pollTimer = null
	let currentPaymentIntentId = null

	const isProcessing = computed(() =>
		![TERMINAL_STATUS.IDLE, TERMINAL_STATUS.SUCCEEDED, TERMINAL_STATUS.FAILED, TERMINAL_STATUS.CANCELED].includes(status.value)
	)

	const isConnected = computed(() => !!connectedReader.value)

	// ── Fetch connection token (called by Stripe SDK) ──
	async function fetchConnectionToken() {
		const res = await call('zevar_core.integrations.stripe_terminal.api.get_connection_token')
		if (!res?.secret) {
			throw new Error('Failed to get connection token')
		}
		return res.secret
	}

	// ── Initialize the SDK & terminal instance ──
	async function initialize() {
		if (terminalInstance) return terminalInstance

		status.value = TERMINAL_STATUS.LOADING_SDK
		statusMessage.value = 'Loading payment terminal...'
		error.value = null

		try {
			await loadStripeTerminalSDK()

			terminalInstance = window.StripeTerminal.create({
				onFetchConnectionToken: fetchConnectionToken,
				onUnexpectedReaderDisconnect: () => {
					connectedReader.value = null
					error.value = 'Card reader disconnected unexpectedly. Please reconnect.'
					status.value = TERMINAL_STATUS.IDLE
					statusMessage.value = ''
				},
			})

			status.value = TERMINAL_STATUS.IDLE
			statusMessage.value = ''
			return terminalInstance
		} catch (e) {
			error.value = `Terminal initialization failed: ${e.message}`
			status.value = TERMINAL_STATUS.FAILED
			statusMessage.value = ''
			throw e
		}
	}

	// ── Discover available readers ──
	async function discoverReaders() {
		try {
			await initialize()
			status.value = TERMINAL_STATUS.DISCOVERING
			statusMessage.value = 'Searching for card readers...'
			error.value = null

			const result = await terminalInstance.discoverReaders()

			if (result.error) {
				throw new Error(result.error.message)
			}

			readers.value = (result.discoveredReaders || []).map(r => ({
				id: r.id,
				label: r.label || r.id,
				device_type: r.device_type,
				status: r.status,
				serial_number: r.serial_number,
				ip_address: r.ip_address,
				is_online: r.status === 'online',
				_raw: r,
			}))

			status.value = TERMINAL_STATUS.IDLE
			statusMessage.value = ''
			return readers.value
		} catch (e) {
			error.value = `Reader discovery failed: ${e.message}`
			status.value = TERMINAL_STATUS.FAILED
			statusMessage.value = ''
			throw e
		}
	}

	// ── Connect to a specific reader ──
	async function connectReader(reader) {
		try {
			await initialize()
			status.value = TERMINAL_STATUS.CONNECTING
			statusMessage.value = `Connecting to ${reader.label || 'reader'}...`
			error.value = null

			// Use the raw Stripe reader object if available
			const rawReader = reader._raw || reader
			const result = await terminalInstance.connectReader(rawReader)

			if (result.error) {
				throw new Error(result.error.message)
			}

			connectedReader.value = {
				id: result.reader.id,
				label: result.reader.label,
				device_type: result.reader.device_type,
				status: 'connected',
			}

			status.value = TERMINAL_STATUS.IDLE
			statusMessage.value = ''
			return connectedReader.value
		} catch (e) {
			error.value = `Reader connection failed: ${e.message}`
			status.value = TERMINAL_STATUS.FAILED
			statusMessage.value = ''
			throw e
		}
	}

	// ── Disconnect the current reader ──
	async function disconnectReader() {
		if (terminalInstance && connectedReader.value) {
			try {
				await terminalInstance.disconnectReader()
			} catch {
				// Ignore errors during disconnect
			}
		}
		connectedReader.value = null
		status.value = TERMINAL_STATUS.IDLE
		statusMessage.value = ''
	}

	// ── Collect payment via the connected reader ──
	async function collectPayment({ amount, invoiceName, description, currency = 'usd' }) {
		if (!connectedReader.value) {
			throw new Error('No card reader connected. Please connect a reader first.')
		}

		error.value = null
		paymentResult.value = null
		receiptUrl.value = null

		try {
			// Step 1: Create PaymentIntent via our backend
			status.value = TERMINAL_STATUS.CREATING_INTENT
			statusMessage.value = 'Creating payment...'

			const intent = await call('zevar_core.integrations.stripe_terminal.api.create_terminal_payment', {
				amount,
				currency,
				invoice_name: invoiceName || null,
				description: description || null,
			})

			if (!intent?.client_secret) {
				throw new Error('Failed to create payment intent')
			}

			currentPaymentIntentId = intent.payment_intent_id

			// Step 2: Present the payment on the reader
			status.value = TERMINAL_STATUS.WAITING_FOR_CARD
			statusMessage.value = 'Present card on the reader...'

			const collectResult = await terminalInstance.collectPaymentMethod(intent.client_secret)

			if (collectResult.error) {
				if (collectResult.error.code === 'canceled') {
					status.value = TERMINAL_STATUS.CANCELED
					statusMessage.value = 'Payment canceled'
					return { success: false, canceled: true }
				}
				throw new Error(collectResult.error.message)
			}

			// Step 3: Process/confirm the payment
			status.value = TERMINAL_STATUS.PROCESSING
			statusMessage.value = 'Processing payment...'

			const processResult = await terminalInstance.processPayment(collectResult.paymentIntent)

			if (processResult.error) {
				throw new Error(processResult.error.message)
			}

			// Step 4: Confirm via backend (the webhook will also reconcile)
			status.value = TERMINAL_STATUS.CONFIRMING
			statusMessage.value = 'Confirming payment...'

			// Poll for the final status from our backend
			const finalStatus = await pollPaymentStatus(currentPaymentIntentId)

			if (finalStatus?.status === 'succeeded') {
				paymentResult.value = finalStatus
				receiptUrl.value = finalStatus.charges?.[0]?.receipt_url || null
				status.value = TERMINAL_STATUS.SUCCEEDED
				statusMessage.value = 'Payment approved!'
				return {
					success: true,
					paymentIntentId: currentPaymentIntentId,
					amount: finalStatus.amount,
					receiptUrl: receiptUrl.value,
					cardBrand: finalStatus.charges?.[0]?.payment_method_details?.card_present?.brand,
					last4: finalStatus.charges?.[0]?.payment_method_details?.card_present?.last4,
				}
			} else {
				throw new Error(`Payment ended with status: ${finalStatus?.status || 'unknown'}`)
			}
		} catch (e) {
			error.value = e.message
			if (status.value !== TERMINAL_STATUS.CANCELED) {
				status.value = TERMINAL_STATUS.FAILED
			}
			statusMessage.value = ''
			// Attempt to cancel the lingering intent
			if (currentPaymentIntentId && status.value === TERMINAL_STATUS.FAILED) {
				try {
					await call('zevar_core.integrations.stripe_terminal.api.cancel_terminal_payment', {
						payment_intent_id: currentPaymentIntentId,
					})
				} catch {
					// Best-effort cleanup
				}
			}
			return { success: false, error: e.message }
		} finally {
			currentPaymentIntentId = null
		}
	}

	// ── Cancel an in-progress payment collection ──
	async function cancelCollection() {
		if (terminalInstance) {
			try {
				await terminalInstance.cancelCollectPaymentMethod()
			} catch {
				// May fail if no collection is in progress
			}
		}
		if (currentPaymentIntentId) {
			try {
				await call('zevar_core.integrations.stripe_terminal.api.cancel_terminal_payment', {
					payment_intent_id: currentPaymentIntentId,
				})
			} catch {
				// Best-effort
			}
		}
		status.value = TERMINAL_STATUS.CANCELED
		statusMessage.value = 'Payment canceled'
	}

	// ── Poll backend for payment status ──
	async function pollPaymentStatus(paymentIntentId, maxAttempts = 30, intervalMs = 1000) {
		return new Promise((resolve, reject) => {
			let attempts = 0

			pollTimer = setInterval(async () => {
				attempts++
				try {
					const result = await call('zevar_core.integrations.stripe_terminal.api.get_payment_status', {
						payment_intent_id: paymentIntentId,
					})

					if (result?.status === 'succeeded') {
						clearInterval(pollTimer)
						pollTimer = null
						resolve(result)
					} else if (['canceled', 'requires_payment_method'].includes(result?.status)) {
						clearInterval(pollTimer)
						pollTimer = null
						reject(new Error(`Payment ${result.status}`))
					} else if (attempts >= maxAttempts) {
						clearInterval(pollTimer)
						pollTimer = null
						// One final check — it may have succeeded between polls
						if (result?.status === 'succeeded') {
							resolve(result)
						} else {
							reject(new Error('Payment confirmation timed out'))
						}
					}
				} catch (e) {
					if (attempts >= maxAttempts) {
						clearInterval(pollTimer)
						pollTimer = null
						reject(e)
					}
				}
			}, intervalMs)
		})
	}

	// ── List readers via backend (doesn't need SDK) ──
	async function listBackendReaders() {
		try {
			const result = await call('zevar_core.integrations.stripe_terminal.api.list_terminal_devices')
			return result?.devices || []
		} catch {
			return []
		}
	}

	// ── Reset state ──
	function reset() {
		status.value = TERMINAL_STATUS.IDLE
		error.value = null
		paymentResult.value = null
		receiptUrl.value = null
		statusMessage.value = ''
		currentPaymentIntentId = null
		if (pollTimer) {
			clearInterval(pollTimer)
			pollTimer = null
		}
	}

	// Cleanup on unmount
	onUnmounted(() => {
		if (pollTimer) {
			clearInterval(pollTimer)
			pollTimer = null
		}
	})

	return {
		// State (readonly)
		status: readonly(status),
		error: readonly(error),
		readers: readonly(readers),
		connectedReader: readonly(connectedReader),
		paymentResult: readonly(paymentResult),
		receiptUrl: readonly(receiptUrl),
		statusMessage: readonly(statusMessage),

		// Computed
		isProcessing,
		isConnected,

		// Methods
		initialize,
		discoverReaders,
		connectReader,
		disconnectReader,
		collectPayment,
		cancelCollection,
		listBackendReaders,
		reset,
	}
}
