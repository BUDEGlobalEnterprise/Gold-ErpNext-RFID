/**
 * usePaymentGateway — Unified composable bridging Stripe & Square terminals.
 *
 * Determines which gateway is active from Payment Gateway Settings,
 * delegates to the correct composable, and provides a single API surface
 * for CheckoutModal.vue to consume.
 */
import { ref, readonly, computed } from 'vue'
import { call } from 'frappe-ui'
import { useStripeTerminal, TERMINAL_STATUS } from './useStripeTerminal.js'
import { useSquareTerminal, SQUARE_STATUS } from './useSquareTerminal.js'

export const GATEWAY = { STRIPE: 'stripe', SQUARE: 'square', MOCK: 'mock', NONE: 'none' }

export function usePaymentGateway() {
	const activeGateway = ref(GATEWAY.NONE)
	const gatewayLoading = ref(false)
	const gatewayError = ref(null)

	const stripe = useStripeTerminal()
	const square = useSquareTerminal()

	const mockStatus = ref('idle')
	const mockStatusMessage = ref('')
	const mockError = ref(null)
	const mockSelectedDevice = ref(null)
	const mockDevices = ref([{ id: 'mock-1', label: 'Simulated Terminal (Dev)', status: 'online' }])

	// Unified status
	const status = computed(() => {
		if (activeGateway.value === GATEWAY.STRIPE) return stripe.status.value
		if (activeGateway.value === GATEWAY.SQUARE) return square.status.value
		if (activeGateway.value === GATEWAY.MOCK) return mockStatus.value
		return 'idle'
	})

	const statusMessage = computed(() => {
		if (activeGateway.value === GATEWAY.STRIPE) return stripe.statusMessage.value
		if (activeGateway.value === GATEWAY.SQUARE) return square.statusMessage.value
		if (activeGateway.value === GATEWAY.MOCK) return mockStatusMessage.value
		return ''
	})

	const error = computed(() => {
		if (gatewayError.value) return gatewayError.value
		if (activeGateway.value === GATEWAY.STRIPE) return stripe.error.value
		if (activeGateway.value === GATEWAY.SQUARE) return square.error.value
		if (activeGateway.value === GATEWAY.MOCK) return mockError.value
		return null
	})

	const isProcessing = computed(() => {
		if (activeGateway.value === GATEWAY.STRIPE) return stripe.isProcessing.value
		if (activeGateway.value === GATEWAY.SQUARE) return square.isProcessing.value
		if (activeGateway.value === GATEWAY.MOCK) return mockStatus.value === 'processing'
		return false
	})

	const isTerminalReady = computed(() => {
		if (activeGateway.value === GATEWAY.STRIPE) return stripe.isConnected.value
		if (activeGateway.value === GATEWAY.SQUARE) return !!square.selectedDevice.value
		if (activeGateway.value === GATEWAY.MOCK) return !!mockSelectedDevice.value
		return false
	})

	const devices = computed(() => {
		if (activeGateway.value === GATEWAY.STRIPE) return stripe.readers.value
		if (activeGateway.value === GATEWAY.SQUARE) return square.devices.value
		if (activeGateway.value === GATEWAY.MOCK) return mockDevices.value
		return []
	})

	// Detect active gateway from settings
	async function detectGateway() {
		gatewayLoading.value = true
		gatewayError.value = null
		try {
			const settings = await call('frappe.client.get', {
				doctype: 'Payment Gateway Settings',
				name: 'Payment Gateway Settings',
				fields: ['stripe_enabled', 'square_enabled'],
			})
			if (settings?.stripe_enabled) {
				activeGateway.value = GATEWAY.STRIPE
			} else if (settings?.square_enabled) {
				activeGateway.value = GATEWAY.SQUARE
			} else {
				activeGateway.value = GATEWAY.MOCK
				console.log('No payment gateway enabled. Falling back to MOCK Terminal for development.')
			}
		} catch (e) {
			// In dev environments where Payment Gateway Settings might not even exist yet
			activeGateway.value = GATEWAY.MOCK
			console.log('Failed to load gateway settings. Falling back to MOCK Terminal for development.')
		} finally {
			gatewayLoading.value = false
		}
		return activeGateway.value
	}

	// Discover/fetch devices for the active gateway
	async function loadDevices() {
		if (activeGateway.value === GATEWAY.STRIPE) {
			return await stripe.discoverReaders()
		} else if (activeGateway.value === GATEWAY.SQUARE) {
			return await square.fetchDevices()
		} else if (activeGateway.value === GATEWAY.MOCK) {
			return mockDevices.value
		}
		return []
	}

	// Connect/select a device
	async function selectDevice(device) {
		if (activeGateway.value === GATEWAY.STRIPE) {
			return await stripe.connectReader(device)
		} else if (activeGateway.value === GATEWAY.SQUARE) {
			square.selectDevice(device)
			return device
		} else if (activeGateway.value === GATEWAY.MOCK) {
			mockSelectedDevice.value = device
			return device
		}
	}

	// Unified payment collection
	async function collectPayment({ amount, invoiceName, description, currency }) {
		if (activeGateway.value === GATEWAY.STRIPE) {
			return await stripe.collectPayment({
				amount,
				invoiceName,
				description,
				currency: currency?.toLowerCase() || 'usd',
			})
		} else if (activeGateway.value === GATEWAY.SQUARE) {
			return await square.collectPayment({
				amount,
				invoiceName,
				description,
				currency: currency?.toUpperCase() || 'USD',
				deviceId: square.selectedDevice.value?.id,
			})
		} else if (activeGateway.value === GATEWAY.MOCK) {
			mockStatus.value = 'processing'
			mockStatusMessage.value = 'Please ask customer to tap card on Simulated Terminal...'
			return new Promise((resolve) => {
				setTimeout(() => {
					mockStatus.value = 'idle'
					mockStatusMessage.value = ''
					resolve({
						success: true,
						transactionId: 'txn_mock_' + Math.random().toString(36).substring(2, 9),
						amount: amount
					})
				}, 3000)
			})
		}
		return { success: false, error: 'No gateway active' }
	}

	// Cancel
	async function cancelPayment() {
		if (activeGateway.value === GATEWAY.STRIPE) await stripe.cancelCollection()
		else if (activeGateway.value === GATEWAY.SQUARE) square.cancelCollection()
		else if (activeGateway.value === GATEWAY.MOCK) { mockStatus.value = 'idle'; mockStatusMessage.value = '' }
	}

	// Reset
	function reset() {
		stripe.reset()
		square.reset()
		mockStatus.value = 'idle'
		mockSelectedDevice.value = null
		gatewayError.value = null
	}

	return {
		activeGateway: readonly(activeGateway),
		gatewayLoading: readonly(gatewayLoading),
		status,
		statusMessage,
		error,
		isProcessing,
		isTerminalReady,
		devices,
		detectGateway,
		loadDevices,
		selectDevice,
		collectPayment,
		cancelPayment,
		reset,
		// Expose sub-composables for advanced usage
		stripe,
		square,
	}
}
