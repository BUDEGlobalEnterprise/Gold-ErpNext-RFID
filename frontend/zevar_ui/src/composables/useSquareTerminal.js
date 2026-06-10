/**
 * useSquareTerminal — Vue 3 Composable for Square Terminal (Card-Present)
 *
 * Cloud-to-cloud flow: Frontend → Backend → Square API → Terminal device.
 * No client-side SDK needed. Card data never touches our code.
 */
import { ref, readonly, computed, onUnmounted } from 'vue'
import { call } from 'frappe-ui'

export const SQUARE_STATUS = {
	IDLE: 'idle',
	LOADING_DEVICES: 'loading_devices',
	CREATING_CHECKOUT: 'creating_checkout',
	WAITING_FOR_CARD: 'waiting_for_card',
	PROCESSING: 'processing',
	SUCCEEDED: 'succeeded',
	FAILED: 'failed',
	CANCELED: 'canceled',
	TIMED_OUT: 'timed_out',
}

export function useSquareTerminal() {
	const status = ref(SQUARE_STATUS.IDLE)
	const error = ref(null)
	const devices = ref([])
	const selectedDevice = ref(null)
	const paymentResult = ref(null)
	const receiptUrl = ref(null)
	const statusMessage = ref('')

	let pollTimer = null
	let currentCheckoutId = null

	const isProcessing = computed(
		() =>
			![
				SQUARE_STATUS.IDLE,
				SQUARE_STATUS.SUCCEEDED,
				SQUARE_STATUS.FAILED,
				SQUARE_STATUS.CANCELED,
				SQUARE_STATUS.TIMED_OUT,
			].includes(status.value)
	)

	async function fetchDevices() {
		status.value = SQUARE_STATUS.LOADING_DEVICES
		statusMessage.value = 'Loading devices...'
		error.value = null
		try {
			const result = await call('zevar_core.integrations.square_terminal.api.get_devices')
			devices.value = (result?.devices || []).map((d) => ({
				id: d.id,
				name: d.name || d.id,
				type: d.type,
				status: d.status,
				location_id: d.location_id,
				is_online: d.status === 'ACTIVE' || d.status === 'PAIRED',
			}))
			status.value = SQUARE_STATUS.IDLE
			statusMessage.value = ''
			return devices.value
		} catch (e) {
			error.value = `Failed to load devices: ${e.message}`
			status.value = SQUARE_STATUS.FAILED
			statusMessage.value = ''
			throw e
		}
	}

	function selectDevice(device) {
		selectedDevice.value = device
	}

	async function collectPayment({
		amount,
		invoiceName,
		description,
		currency = 'USD',
		deviceId,
	}) {
		const device = deviceId || selectedDevice.value?.id
		if (!device) throw new Error('No Square Terminal device selected.')

		error.value = null
		paymentResult.value = null
		receiptUrl.value = null

		try {
			status.value = SQUARE_STATUS.CREATING_CHECKOUT
			statusMessage.value = 'Sending payment to terminal...'

			const checkout = await call(
				'zevar_core.integrations.square_terminal.api.create_terminal_checkout',
				{
					device_id: device,
					amount,
					currency,
					invoice_name: invoiceName || null,
					note: description || null,
				}
			)
			if (!checkout?.checkout_id) throw new Error('Failed to create terminal checkout')
			currentCheckoutId = checkout.checkout_id

			status.value = SQUARE_STATUS.WAITING_FOR_CARD
			statusMessage.value = 'Present card on the Square Terminal...'

			const finalResult = await pollCheckoutStatus(currentCheckoutId)

			if (finalResult.status === 'COMPLETED') {
				paymentResult.value = finalResult
				receiptUrl.value = finalResult.receipt_url || null
				status.value = SQUARE_STATUS.SUCCEEDED
				statusMessage.value = 'Payment approved!'
				return {
					success: true,
					checkoutId: currentCheckoutId,
					paymentId: finalResult.payment_id,
					amount: finalResult.amount,
					receiptUrl: finalResult.receipt_url,
					cardBrand: finalResult.card_brand,
					last4: finalResult.last_4,
				}
			} else if (finalResult.status === 'CANCELED') {
				status.value = SQUARE_STATUS.CANCELED
				statusMessage.value = 'Payment canceled on device'
				return { success: false, canceled: true }
			} else {
				throw new Error(`Checkout ended with status: ${finalResult.status}`)
			}
		} catch (e) {
			error.value = e.message
			if (status.value !== SQUARE_STATUS.CANCELED) status.value = SQUARE_STATUS.FAILED
			statusMessage.value = ''
			return { success: false, error: e.message }
		} finally {
			currentCheckoutId = null
		}
	}

	function pollCheckoutStatus(checkoutId, maxAttempts = 120, intervalMs = 2000) {
		return new Promise((resolve, reject) => {
			let attempts = 0
			pollTimer = setInterval(async () => {
				attempts++
				try {
					const result = await call(
						'zevar_core.integrations.square_terminal.api.get_checkout_status',
						{
							checkout_id: checkoutId,
						}
					)
					const s = result?.status
					if (s === 'IN_PROGRESS') {
						status.value = SQUARE_STATUS.PROCESSING
						statusMessage.value = 'Processing payment...'
					}
					if (s === 'COMPLETED') {
						clearInterval(pollTimer)
						pollTimer = null
						resolve(result)
					} else if (['CANCELED', 'CANCEL_REQUESTED'].includes(s)) {
						clearInterval(pollTimer)
						pollTimer = null
						resolve({ ...result, status: 'CANCELED' })
					} else if (attempts >= maxAttempts) {
						clearInterval(pollTimer)
						pollTimer = null
						reject(new Error('Checkout timed out'))
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

	function cancelCollection() {
		if (pollTimer) {
			clearInterval(pollTimer)
			pollTimer = null
		}
		status.value = SQUARE_STATUS.CANCELED
		statusMessage.value = 'Payment canceled'
		currentCheckoutId = null
	}

	async function pairDevice(deviceName, locationId) {
		try {
			return await call('zevar_core.integrations.square_terminal.api.pair_device', {
				device_name: deviceName,
				location_id: locationId || null,
			})
		} catch (e) {
			error.value = `Device pairing failed: ${e.message}`
			throw e
		}
	}

	function reset() {
		status.value = SQUARE_STATUS.IDLE
		error.value = null
		paymentResult.value = null
		receiptUrl.value = null
		statusMessage.value = ''
		currentCheckoutId = null
		if (pollTimer) {
			clearInterval(pollTimer)
			pollTimer = null
		}
	}

	onUnmounted(() => {
		if (pollTimer) {
			clearInterval(pollTimer)
			pollTimer = null
		}
	})

	return {
		status: readonly(status),
		error: readonly(error),
		devices: readonly(devices),
		selectedDevice: readonly(selectedDevice),
		paymentResult: readonly(paymentResult),
		receiptUrl: readonly(receiptUrl),
		statusMessage: readonly(statusMessage),
		isProcessing,
		fetchDevices,
		selectDevice,
		collectPayment,
		cancelCollection,
		pairDevice,
		reset,
	}
}
