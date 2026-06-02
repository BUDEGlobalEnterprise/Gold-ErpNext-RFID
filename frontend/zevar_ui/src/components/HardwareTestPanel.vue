<template>
	<div class="space-y-4">
		<!-- Bridge status banner -->
		<div
			class="premium-card !p-4 flex items-center justify-between gap-4"
			:class="bridgeConnected ? 'border-green-300 dark:border-green-700' : 'border-amber-300 dark:border-amber-700'"
		>
			<div class="flex items-center gap-3">
				<span
					class="w-3 h-3 rounded-full"
					:class="bridgeConnected ? 'bg-green-500 animate-pulse' : 'bg-amber-500'"
				></span>
				<div>
					<div class="font-bold text-sm text-gray-900 dark:text-white">
						Hardware Bridge
						<span v-if="bridgeMock" class="text-xs text-amber-600 font-normal">(mock)</span>
					</div>
					<div class="text-xs text-gray-500 dark:text-gray-400">
						{{ bridgeUrl }} · {{ bridgeConnected ? 'connected' : 'disconnected — tests will run in browser-fallback mode' }}
					</div>
				</div>
			</div>
			<button
				@click="probeBridge"
				class="px-3 py-1.5 text-xs font-bold rounded-lg bg-gray-100 dark:bg-warm-dark-700 hover:bg-gray-200 dark:hover:bg-warm-dark-600 transition"
			>
				Reconnect
			</button>
		</div>

		<!-- Device cards -->
		<div class="grid grid-cols-1 md:grid-cols-2 gap-3">
			<!-- Barcode Scanner -->
			<DeviceCard
				title="Barcode / RFID Scanner"
				:status="scannerStatus"
				hint="Scanners type characters then press Enter. Type or scan any barcode below."
			>
				<input
					ref="scannerInputRef"
					v-model="scannerInput"
					type="text"
					placeholder="Scan or type a barcode (e.g. ITEM-001)..."
					class="w-full px-3 py-2 text-sm border rounded-lg bg-white dark:bg-warm-dark-900 border-gray-300 dark:border-warm-dark-600 focus:ring-2 focus:ring-[#D4AF37] outline-none"
					@keydown.enter="testScanner"
				/>
				<div v-if="lastScan" class="text-xs mt-2 text-gray-500 dark:text-gray-400">
					Last scan: <span class="font-mono text-[#D4AF37]">{{ lastScan }}</span>
				</div>
			</DeviceCard>

			<!-- Receipt Printer -->
			<DeviceCard
				title="Receipt Printer (ESC/POS)"
				:status="receiptStatus"
				hint="Sends a sample ESC/POS receipt to the bridge, or opens a browser print preview."
			>
				<div class="flex gap-2">
					<button
						@click="testReceipt"
						:disabled="receiptStatus === 'running'"
						class="flex-1 px-3 py-2 text-xs font-bold rounded-lg bg-[#D4AF37] text-white hover:bg-[#B8962E] transition disabled:opacity-50"
					>
						Print Test Receipt
					</button>
					<button
						@click="previewReceipt"
						class="px-3 py-2 text-xs font-bold rounded-lg bg-gray-100 dark:bg-warm-dark-700 hover:bg-gray-200 dark:hover:bg-warm-dark-600 transition"
					>
						Preview
					</button>
				</div>
				<div v-if="receiptOutput" class="text-xs mt-2 font-mono text-gray-500 dark:text-gray-400 whitespace-pre-wrap max-h-32 overflow-y-auto">
					{{ receiptOutput }}
				</div>
			</DeviceCard>

			<!-- Tag Printer (Zebra ZPL) -->
			<DeviceCard
				title="Tag Printer (ZPL)"
				:status="tagStatus"
				hint="Sends a sample ZPL jewelry tag. Click Preview to render at labelary.com."
			>
				<div class="flex gap-2">
					<button
						@click="testTag"
						:disabled="tagStatus === 'running'"
						class="flex-1 px-3 py-2 text-xs font-bold rounded-lg bg-[#D4AF37] text-white hover:bg-[#B8962E] transition disabled:opacity-50"
					>
						Print Test Tag
					</button>
					<button
						@click="previewTag"
						class="px-3 py-2 text-xs font-bold rounded-lg bg-gray-100 dark:bg-warm-dark-700 hover:bg-gray-200 dark:hover:bg-warm-dark-600 transition"
					>
						Preview ZPL
					</button>
				</div>
				<div v-if="tagZpl" class="text-[10px] mt-2 font-mono text-gray-500 dark:text-gray-400 whitespace-pre-wrap max-h-32 overflow-y-auto">
					{{ tagZpl }}
				</div>
			</DeviceCard>

			<!-- Cash Drawer -->
			<DeviceCard
				title="Cash Drawer"
				:status="drawerStatus"
				hint="Sends the ESC/POS pulse (1B 70 00 19 FA) via the receipt printer."
			>
				<button
					@click="testDrawer"
					:disabled="drawerStatus === 'running'"
					class="w-full px-3 py-2 text-xs font-bold rounded-lg bg-[#D4AF37] text-white hover:bg-[#B8962E] transition disabled:opacity-50"
				>
					Open Cash Drawer
				</button>
			</DeviceCard>

			<!-- Stripe Terminal -->
			<DeviceCard
				title="Stripe Terminal"
				:status="stripeStatus"
				hint="Quick check reads SDK + reader state. Full test charges $0.50 in test mode, then auto-refunds."
			>
				<div class="flex gap-2">
					<button
						@click="testStripeQuick"
						:disabled="stripeStatus === 'running'"
						class="flex-1 px-3 py-2 text-xs font-bold rounded-lg bg-gray-100 dark:bg-warm-dark-700 hover:bg-gray-200 dark:hover:bg-warm-dark-600 transition disabled:opacity-50"
					>
						Quick Check
					</button>
					<button
						@click="testStripeFull"
						:disabled="stripeStatus === 'running'"
						class="flex-1 px-3 py-2 text-xs font-bold rounded-lg bg-[#D4AF37] text-white hover:bg-[#B8962E] transition disabled:opacity-50"
					>
						Full Test ($0.50)
					</button>
				</div>
				<div v-if="stripeMessage" class="text-xs mt-2 text-gray-500 dark:text-gray-400">
					{{ stripeMessage }}
				</div>
			</DeviceCard>

			<!-- Square Terminal -->
			<DeviceCard
				title="Square Terminal"
				:status="squareStatus"
				hint="Quick check reads Square SDK state. Full test runs a $0.50 sandbox charge."
			>
				<div class="flex gap-2">
					<button
						@click="testSquareQuick"
						:disabled="squareStatus === 'running'"
						class="flex-1 px-3 py-2 text-xs font-bold rounded-lg bg-gray-100 dark:bg-warm-dark-700 hover:bg-gray-200 dark:hover:bg-warm-dark-600 transition disabled:opacity-50"
					>
						Quick Check
					</button>
					<button
						@click="testSquareFull"
						:disabled="squareStatus === 'running'"
						class="flex-1 px-3 py-2 text-xs font-bold rounded-lg bg-[#D4AF37] text-white hover:bg-[#B8962E] transition disabled:opacity-50"
					>
						Full Test ($0.50)
					</button>
				</div>
				<div v-if="squareMessage" class="text-xs mt-2 text-gray-500 dark:text-gray-400">
					{{ squareMessage }}
				</div>
			</DeviceCard>
		</div>

		<!-- Activity log -->
		<div class="premium-card !p-4">
			<div class="flex items-center justify-between mb-2">
				<h4 class="text-xs font-bold uppercase tracking-wider text-gray-700 dark:text-gray-300">
					Activity Log
				</h4>
				<button
					v-if="activityLog.length"
					@click="activityLog = []"
					class="text-xs text-gray-400 hover:text-gray-600"
				>
					Clear
				</button>
			</div>
			<div v-if="!activityLog.length" class="text-xs text-gray-400 py-4 text-center">
				No test activity yet.
			</div>
			<div v-else class="space-y-1 max-h-48 overflow-y-auto text-xs font-mono">
				<div
					v-for="(entry, i) in activityLog"
					:key="i"
					class="flex items-start gap-2 py-1"
				>
					<span class="text-gray-400 shrink-0">{{ entry.time }}</span>
					<span
						class="shrink-0 w-2 h-2 rounded-full mt-1"
						:class="{
							'bg-green-500': entry.level === 'success',
							'bg-red-500': entry.level === 'error',
							'bg-amber-500': entry.level === 'warn',
							'bg-gray-400': entry.level === 'info',
						}"
					></span>
					<span class="text-gray-700 dark:text-gray-300 break-all">{{ entry.message }}</span>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { call } from 'frappe-ui'
import { hardwareService } from '../services/HardwareService.js'
import DeviceCard from './DeviceCard.vue'

const bridgeUrl = ref('ws://localhost:8080')
const bridgeConnected = ref(false)
const bridgeMock = ref(false)

const scannerInputRef = ref(null)
const scannerInput = ref('')
const lastScan = ref('')

const receiptStatus = ref('idle')
const receiptOutput = ref('')
const tagStatus = ref('idle')
const tagZpl = ref('')
const drawerStatus = ref('idle')
const stripeStatus = ref('idle')
const stripeMessage = ref('')
const squareStatus = ref('idle')
const squareMessage = ref('')

const scannerStatus = ref('idle')

const activityLog = ref([])

function log(message, level = 'info') {
	activityLog.value.unshift({
		time: new Date().toLocaleTimeString(),
		level,
		message,
	})
	if (activityLog.value.length > 100) activityLog.value.pop()
}

async function probeBridge() {
	bridgeConnected.value = hardwareService.connected
	if (!hardwareService.connected) {
		hardwareService.connect()
		// give the WebSocket a moment to handshake
		await new Promise((r) => setTimeout(r, 800))
	}
	try {
		const status = await hardwareService.getStatus()
		bridgeConnected.value = !!status?.receipt_printer
		bridgeMock.value = !!status?.mock || status?.bridge_version?.startsWith('mock')
		log(
			bridgeConnected.value
				? `Bridge connected (v${status?.bridge_version || '?'})`
				: 'Bridge unreachable — browser-fallback active',
			bridgeConnected.value ? 'success' : 'warn'
		)
	} catch (e) {
		log(`Bridge probe failed: ${e.message || e}`, 'error')
	}
}

function testScanner() {
	const value = scannerInput.value.trim()
	if (!value) {
		log('Scanner test: empty value', 'warn')
		return
	}
	lastScan.value = value
	scannerStatus.value = 'success'
	log(`Scanner captured: ${value} (${value.length} chars, Enter key received)`, 'success')
	scannerInput.value = ''
	scannerInputRef.value?.focus()
}

async function testReceipt() {
	receiptStatus.value = 'running'
	receiptOutput.value = ''
	try {
		const payload = await call('zevar_core.integrations.hardware.api.build_test_receipt')
		if (!payload) throw new Error('empty payload')

		// Mirror HardwareService.printReceipt but with our test payload
		const sent = hardwareService._send({ action: 'print', payload })
		if (sent) {
			log('Test receipt dispatched to bridge', 'success')
			receiptOutput.value = payload.content || '(binary payload sent)'
		} else {
			log('Bridge offline — opening browser print fallback', 'warn')
			window.open(
				`/printview?doctype=Sales Invoice&name=test&format=pos_receipt_thermal`,
				'_blank'
			)
		}
		receiptStatus.value = 'success'
	} catch (e) {
		log(`Receipt test failed: ${e.message || e}`, 'error')
		receiptStatus.value = 'error'
	}
}

async function previewReceipt() {
	try {
		const payload = await call('zevar_core.integrations.hardware.api.build_test_receipt')
		receiptOutput.value = payload?.content || '(empty)'
		log('Receipt preview loaded', 'info')
	} catch (e) {
		log(`Preview failed: ${e.message || e}`, 'error')
	}
}

async function testTag() {
	tagStatus.value = 'running'
	tagZpl.value = ''
	try {
		const result = await call('zevar_core.integrations.hardware.api.build_test_tag')
		const sent = hardwareService._send({
			action: 'print_tag_zpl',
			tag_data: result.tag_data,
		})
		if (sent) {
			log('Test ZPL tag dispatched to bridge', 'success')
			tagZpl.value = result.zpl || ''
		} else {
			log('Bridge offline — ZPL preview only', 'warn')
			tagZpl.value = result.zpl || ''
		}
		tagStatus.value = 'success'
	} catch (e) {
		log(`Tag test failed: ${e.message || e}`, 'error')
		tagStatus.value = 'error'
	}
}

async function previewTag() {
	try {
		const r = await call('zevar_core.integrations.hardware.api.build_test_zpl')
		tagZpl.value = r.zpl || ''
		// Open labelary in a new tab so the user can render the ZPL
		const url = `https://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/${encodeURIComponent(r.zpl)}`
		window.open(url, '_blank')
		log('ZPL preview sent to labelary.com', 'info')
	} catch (e) {
		log(`ZPL preview failed: ${e.message || e}`, 'error')
	}
}

function testDrawer() {
	drawerStatus.value = 'running'
	try {
		const sent = hardwareService.openCashDrawer()
		if (sent) {
			log('Cash drawer kick sent (\\x1b\\x70\\x00\\x19\\xfa)', 'success')
			drawerStatus.value = 'success'
		} else {
			log('Bridge offline — drawer cannot fire without printer link', 'error')
			drawerStatus.value = 'error'
		}
	} catch (e) {
		log(`Drawer test failed: ${e.message || e}`, 'error')
		drawerStatus.value = 'error'
	}
}

async function testStripeQuick() {
	stripeStatus.value = 'running'
	stripeMessage.value = 'Loading Stripe Terminal SDK...'
	try {
		const { useStripeTerminal } = await import('../composables/useStripeTerminal.js')
		const stripe = useStripeTerminal()
		await stripe.initialize()
		await stripe.discoverReaders()
		const readers = stripe.readers.value || []
		const connected = stripe.connectedReader.value
		if (connected) {
			stripeMessage.value = `Connected to ${connected.label || connected.serial_number}`
			log(`Stripe quick-check OK: ${stripeMessage.value}`, 'success')
		} else if (readers.length) {
			stripeMessage.value = `${readers.length} reader(s) discovered, none connected`
			log(`Stripe quick-check: ${readers.length} reader(s) discovered`, 'info')
		} else {
			stripeMessage.value = 'SDK loaded, no readers discovered (simulated reader OK in test mode)'
			log('Stripe quick-check: SDK loaded, no readers found', 'warn')
		}
		stripeStatus.value = 'success'
	} catch (e) {
		stripeMessage.value = e.message || String(e)
		log(`Stripe quick-check failed: ${stripeMessage.value}`, 'error')
		stripeStatus.value = 'error'
	}
}

async function testStripeFull() {
	stripeStatus.value = 'running'
	stripeMessage.value = 'Running $0.50 test charge...'
	try {
		const r = await call('zevar_core.integrations.stripe_terminal.api.run_test_payment', {
			amount_cents: 50,
		})
		if (r?.success) {
			stripeMessage.value = `Charged $0.50, refunded. Intent: ${r.payment_intent_id}`
			log(`Stripe full test OK (intent ${r.payment_intent_id})`, 'success')
			stripeStatus.value = 'success'
		} else {
			throw new Error(r?.message || 'Stripe test payment returned no success')
		}
	} catch (e) {
		stripeMessage.value = e.message || String(e)
		log(`Stripe full test failed: ${stripeMessage.value}`, 'error')
		stripeStatus.value = 'error'
	}
}

async function testSquareQuick() {
	squareStatus.value = 'running'
	squareMessage.value = 'Loading Square Terminal SDK...'
	try {
		const { useSquareTerminal } = await import('../composables/useSquareTerminal.js')
		const square = useSquareTerminal()
		// Best-effort: call whatever state inspector exists
		const status = square.status?.value || square.state?.value || 'unknown'
		squareMessage.value = `Square SDK state: ${status}`
		log(`Square quick-check: ${squareMessage.value}`, status === 'connected' ? 'success' : 'info')
		squareStatus.value = 'success'
	} catch (e) {
		squareMessage.value = e.message || String(e)
		log(`Square quick-check failed: ${squareMessage.value}`, 'error')
		squareStatus.value = 'error'
	}
}

async function testSquareFull() {
	squareStatus.value = 'running'
	squareMessage.value = 'Running $0.50 sandbox charge...'
	try {
		const r = await call('zevar_core.integrations.square_terminal.api.run_test_payment', {
			amount_cents: 50,
		})
		if (r?.success) {
			squareMessage.value = `Charged $0.50 sandbox, refunded. Order: ${r.order_id || r.transaction_id}`
			log(`Square full test OK`, 'success')
			squareStatus.value = 'success'
		} else {
			throw new Error(r?.message || 'Square test payment returned no success')
		}
	} catch (e) {
		// Many Zevar installs won't have square_terminal wired — surface cleanly
		squareMessage.value = e.message || String(e)
		log(`Square full test failed: ${squareMessage.value}`, 'error')
		squareStatus.value = 'error'
	}
}

onMounted(() => {
	probeBridge()
	scannerInputRef.value?.focus()
})

onBeforeUnmount(() => {
	// Don't close the bridge — it's a shared singleton
})
</script>
