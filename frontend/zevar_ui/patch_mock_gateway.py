import re

with open("src/composables/usePaymentGateway.js", "r") as f:
    content = f.read()

# Mock Refs
if "const mockStatus =" not in content:
    content = content.replace(
        "const square = useSquareTerminal()",
        "const square = useSquareTerminal()\n\n\tconst mockStatus = ref('idle')\n\tconst mockStatusMessage = ref('')\n\tconst mockError = ref(null)\n\tconst mockSelectedDevice = ref(null)\n\tconst mockDevices = ref([{ id: 'mock-1', label: 'Simulated Terminal (Dev)', status: 'online' }])"
    )

# Computed props
content = content.replace(
    "if (activeGateway.value === GATEWAY.SQUARE) return square.status.value",
    "if (activeGateway.value === GATEWAY.SQUARE) return square.status.value\n\t\tif (activeGateway.value === GATEWAY.MOCK) return mockStatus.value"
)
content = content.replace(
    "if (activeGateway.value === GATEWAY.SQUARE) return square.statusMessage.value",
    "if (activeGateway.value === GATEWAY.SQUARE) return square.statusMessage.value\n\t\tif (activeGateway.value === GATEWAY.MOCK) return mockStatusMessage.value"
)
content = content.replace(
    "if (activeGateway.value === GATEWAY.SQUARE) return square.error.value",
    "if (activeGateway.value === GATEWAY.SQUARE) return square.error.value\n\t\tif (activeGateway.value === GATEWAY.MOCK) return mockError.value"
)
content = content.replace(
    "if (activeGateway.value === GATEWAY.SQUARE) return square.isProcessing.value",
    "if (activeGateway.value === GATEWAY.SQUARE) return square.isProcessing.value\n\t\tif (activeGateway.value === GATEWAY.MOCK) return mockStatus.value === 'processing'"
)
content = content.replace(
    "if (activeGateway.value === GATEWAY.SQUARE) return !!square.selectedDevice.value",
    "if (activeGateway.value === GATEWAY.SQUARE) return !!square.selectedDevice.value\n\t\tif (activeGateway.value === GATEWAY.MOCK) return !!mockSelectedDevice.value"
)
content = content.replace(
    "if (activeGateway.value === GATEWAY.SQUARE) return square.devices.value",
    "if (activeGateway.value === GATEWAY.SQUARE) return square.devices.value\n\t\tif (activeGateway.value === GATEWAY.MOCK) return mockDevices.value"
)

# loadDevices
content = content.replace(
    "} else if (activeGateway.value === GATEWAY.SQUARE) {\n\t\t\treturn await square.fetchDevices()\n\t\t}",
    "} else if (activeGateway.value === GATEWAY.SQUARE) {\n\t\t\treturn await square.fetchDevices()\n\t\t} else if (activeGateway.value === GATEWAY.MOCK) {\n\t\t\treturn mockDevices.value\n\t\t}"
)

# selectDevice
content = content.replace(
    "} else if (activeGateway.value === GATEWAY.SQUARE) {\n\t\t\tsquare.selectDevice(device)\n\t\t\treturn device\n\t\t}",
    "} else if (activeGateway.value === GATEWAY.SQUARE) {\n\t\t\tsquare.selectDevice(device)\n\t\t\treturn device\n\t\t} else if (activeGateway.value === GATEWAY.MOCK) {\n\t\t\tmockSelectedDevice.value = device\n\t\t\treturn device\n\t\t}"
)

# collectPayment
mock_collect = """} else if (activeGateway.value === GATEWAY.MOCK) {
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
		}"""

content = content.replace(
    """} else if (activeGateway.value === GATEWAY.SQUARE) {
			return await square.collectPayment({
				amount,
				invoiceName,
				description,
				currency: currency?.toUpperCase() || 'USD',
				deviceId: square.selectedDevice.value?.id,
			})
		}""",
    """} else if (activeGateway.value === GATEWAY.SQUARE) {
			return await square.collectPayment({
				amount,
				invoiceName,
				description,
				currency: currency?.toUpperCase() || 'USD',
				deviceId: square.selectedDevice.value?.id,
			})
		""" + mock_collect
)

# cancelPayment
content = content.replace(
    "else if (activeGateway.value === GATEWAY.SQUARE) square.cancelCollection()",
    "else if (activeGateway.value === GATEWAY.SQUARE) square.cancelCollection()\n\t\telse if (activeGateway.value === GATEWAY.MOCK) { mockStatus.value = 'idle'; mockStatusMessage.value = '' }"
)

# reset
content = content.replace(
    "square.reset()",
    "square.reset()\n\t\tmockStatus.value = 'idle'\n\t\tmockSelectedDevice.value = null"
)


with open("src/composables/usePaymentGateway.js", "w") as f:
    f.write(content)

