import { call } from 'frappe-ui'

class HardwareService {
	constructor() {
		this.ws = null
		this.bridgeUrl = 'ws://localhost:8080'
		this.connected = false
		this.reconnectTimer = null
	}

	connect() {
		if (this.ws) return

		this.ws = new WebSocket(this.bridgeUrl)

		this.ws.onopen = () => {
			console.log('Hardware bridge connected')
			this.connected = true
			clearTimeout(this.reconnectTimer)
		}

		this.ws.onclose = () => {
			console.log('Hardware bridge disconnected')
			this.connected = false
			this.ws = null
			// Attempt to reconnect every 10 seconds
			this.reconnectTimer = setTimeout(() => this.connect(), 10000)
		}

		this.ws.onerror = (err) => {
			console.error('Hardware bridge error:', err)
		}

		this.ws.onmessage = (msg) => {
			try {
				const data = JSON.parse(msg.data)
				if (data.status === 'error') {
					console.error('Bridge reported error:', data.message)
				}
			} catch (e) {
				console.error('Failed to parse bridge message', e)
			}
		}
	}

	async printReceipt(invoiceName) {
		try {
			// 1. Generate ESC/POS content from backend
			const r = await call('zevar_core.integrations.hardware.api.generate_receipt_content', {
				invoice_name: invoiceName,
			})

			if (r && this.connected) {
				// 2. Send to local bridge
				this.ws.send(
					JSON.stringify({
						action: 'print',
						payload: r,
					})
				)
				return true
			} else {
				// Fallback to browser printing if bridge not connected
				window.open(`/printview?doctype=Sales Invoice&name=${invoiceName}`, '_blank')
				return false
			}
		} catch (e) {
			console.error('Failed to print receipt', e)
			window.open(`/printview?doctype=Sales Invoice&name=${invoiceName}`, '_blank')
			return false
		}
	}

	async printTag(itemCode) {
		try {
			const r = await call('zevar_core.integrations.hardware.api.generate_tag_content', {
				item_code: itemCode,
			})

			if (r && this.connected) {
				this.ws.send(
					JSON.stringify({
						action: 'print',
						payload: r.print_payload,
					})
				)
				return true
			}
			return false
		} catch (e) {
			console.error('Failed to print tag', e)
			return false
		}
	}
}

export const hardwareService = new HardwareService()
