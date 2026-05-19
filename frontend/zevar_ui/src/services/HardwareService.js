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

	_send(payload) {
		if (!this.connected || !this.ws) return false
		this.ws.send(JSON.stringify(payload))
		return true
	}

	async printReceipt(invoiceName) {
		try {
			// 1. Generate ESC/POS content from backend
			const r = await call('zevar_core.integrations.hardware.api.generate_receipt_content', {
				invoice_name: invoiceName,
			})

			if (r && this._send({ action: 'print', payload: r })) {
				return true
			}
			// Fallback to browser print if bridge not connected
			window.open(`/printview?doctype=Sales Invoice&name=${invoiceName}&format=pos_receipt_thermal`, '_blank')
			return false
		} catch (e) {
			console.error('Failed to print receipt', e)
			window.open(`/printview?doctype=Sales Invoice&name=${invoiceName}&format=pos_receipt_thermal`, '_blank')
			return false
		}
	}

	async printTag(itemCode) {
		try {
			const r = await call('zevar_core.integrations.hardware.api.generate_tag_content', {
				item_code: itemCode,
			})

			if (r && this._send({ action: 'print', payload: r.print_payload })) {
				return true
			}
			return false
		} catch (e) {
			console.error('Failed to print tag', e)
			return false
		}
	}

	async printZplTag(tagData) {
		/** Print a jewelry tag using ZPL (Zebra printers).
		 *  tagData: { item_code, item_name, rate, metal_type, weight_grams }
		 */
		if (this._send({ action: 'print_tag_zpl', tag_data: tagData })) {
			return true
		}
		// Fallback: generate ZPL and open in new window for manual send
		console.log('Bridge not connected. ZPL tag data:', tagData)
		return false
	}

	openCashDrawer() {
		/** Trigger cash drawer via receipt printer kick-out signal. */
		return this._send({ action: 'cash_drawer' })
	}

	async getStatus() {
		/** Query bridge for printer connection status. */
		return new Promise((resolve) => {
			if (!this.connected) {
				resolve({ receipt_printer: false, tag_printer: false })
				return
			}

			const handler = (msg) => {
				try {
					const data = JSON.parse(msg.data)
					if (data.status === 'ok') {
						this.ws.removeEventListener('message', handler)
						resolve(data)
					}
				} catch (e) { /* ignore */ }
			}

			this.ws.addEventListener('message', handler)
			this._send({ action: 'status' })

			// Timeout after 3s
			setTimeout(() => {
				this.ws.removeEventListener('message', handler)
				resolve({ receipt_printer: false, tag_printer: false })
			}, 3000)
		})
	}
}

export const hardwareService = new HardwareService()
