import re

with open("src/components/CheckoutModal.vue", "r") as f:
    content = f.read()

socket_logic = """
	function handlePaymentReceived(data) {
		if (step.value === 'qr_payment' && successInvoiceId.value === data.invoice) {
			step.value = 'success'
			successBreakdown.value = selectedPayments.value
			// Play a success chime if needed
			try {
				const audio = new Audio('/assets/zevar_core/sounds/success.mp3')
				audio.play()
			} catch (e) {}
		}
	}

	onMounted(() => {
		if (window.frappe?.socketio) {
			window.frappe.socketio.socket?.on('payment_received', handlePaymentReceived)
		}
	})

	onUnmounted(() => {
		if (window.frappe?.socketio) {
			window.frappe.socketio.socket?.off('payment_received', handlePaymentReceived)
		}
	})
</script>
"""

content = content.replace("</script>", socket_logic)

with open("src/components/CheckoutModal.vue", "w") as f:
    f.write(content)

