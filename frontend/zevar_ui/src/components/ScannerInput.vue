<template>
	<div class="scanner-input relative">
		<div class="flex items-center gap-2">
			<div class="relative flex-1">
				<svg
					class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z"
					/>
				</svg>
				<input
					ref="inputRef"
					v-model="inputValue"
					type="text"
					:placeholder="placeholder"
					autofocus
					class="w-full pl-10 pr-4 py-3 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm focus:ring-2 focus:ring-[#D4AF37] focus:border-[#D4AF37] outline-none"
					@keydown.enter.prevent="onScan"
					@input="onInput"
				/>
			</div>
			<button
				v-if="showCamera"
				type="button"
				@click="openCamera"
				class="p-3 bg-gray-100 dark:bg-warm-dark-700 rounded-lg hover:bg-gray-200 dark:hover:bg-warm-dark-600 transition"
				title="Scan with camera"
			>
				<svg
					class="w-5 h-5 text-gray-600 dark:text-gray-300"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"
					/>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"
					/>
				</svg>
			</button>
		</div>
		<div v-if="lastScan" class="mt-1 text-xs text-green-600 dark:text-green-400">
			Last scan: {{ lastScan }}
		</div>

		<CameraScanner 
			v-if="showCameraScanner" 
			@close="showCameraScanner = false" 
			@scan="handleCameraScan" 
		/>
	</div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import CameraScanner from './CameraScanner.vue'

const props = defineProps({
	placeholder: { type: String, default: 'Scan barcode or RFID tag...' },
	showCamera: { type: Boolean, default: true },
	autoFocus: { type: Boolean, default: true },
})

const emit = defineEmits(['scan', 'camera-open'])

const inputRef = ref(null)
const inputValue = ref('')
const lastScan = ref('')
const showCameraScanner = ref(false)

let hidDevice = null
let buffer = ''
let bufferTimer = null

function onInput(e) {
	clearTimeout(bufferTimer)
	buffer = inputValue.value
	
	// If the buffer contains multiple newlines, process them immediately
	if (buffer.includes('\n')) {
		const lines = buffer.split('\n')
		// Process all complete lines (everything except the last partial line)
		for (let i = 0; i < lines.length - 1; i++) {
			const scan = lines[i].trim()
			if (scan) processScan(scan)
		}
		// Keep the remaining partial line in the input
		inputValue.value = lines[lines.length - 1]
		buffer = inputValue.value
	}

	bufferTimer = setTimeout(() => {
		if (buffer.length > 3) {
			processScan(buffer.trim())
			inputValue.value = ''
			buffer = ''
		}
	}, 150) // Slightly longer timeout for RFID bursts
}

function onScan() {
	const val = inputValue.value.trim()
	if (val) {
		processScan(val)
		inputValue.value = ''
	}
}

function processScan(value) {
	if (!value) return
	lastScan.value = value
	emit('scan', value)
}

function handleCameraScan(value) {
	processScan(value)
	showCameraScanner.value = false
}

function openCamera() {
	showCameraScanner.value = true
	emit('camera-open')
}

async function connectHID() {
	if (!navigator.hid) return
	try {
		const devices = await navigator.hid.requestDevice({
			filters: props.hidVendorId ? [{ vendorId: props.hidVendorId }] : [],
		})
		if (devices.length > 0) {
			hidDevice = devices[0]
			await hidDevice.open()
			hidDevice.addEventListener('inputreport', (event) => {
				const data = new TextDecoder().decode(event.data.buffer)
				processScan(data.trim())
			})
		}
	} catch {
		// HID not available or denied
	}
}

function focus() {
	inputRef.value?.focus()
}

onMounted(() => {
	if (props.autoFocus) {
		nextTick(() => focus())
	}
})

onUnmounted(() => {
	if (hidDevice) {
		hidDevice.close().catch(() => {})
	}
})

defineExpose({ focus, processScan })
</script>
