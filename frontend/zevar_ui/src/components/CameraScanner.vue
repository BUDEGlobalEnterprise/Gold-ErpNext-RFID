<template>
	<div class="fixed inset-0 z-[100] flex flex-col bg-black">
		<div class="flex items-center justify-between p-4 bg-black/80 text-white shrink-0">
			<h3 class="font-bold text-lg">Scan Barcode</h3>
			<button
				@click="$emit('close')"
				class="p-2 bg-gray-800 hover:bg-gray-700 rounded-full transition-colors"
			>
				<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M6 18L18 6M6 6l12 12"
					></path>
				</svg>
			</button>
		</div>

		<div class="flex-1 relative overflow-hidden flex items-center justify-center">
			<video
				ref="videoElement"
				class="w-full h-full object-cover"
				autoplay
				playsinline
				muted
			></video>

			<!-- Scanner Target Overlay -->
			<div
				class="absolute inset-0 pointer-events-none flex flex-col items-center justify-center"
			>
				<div
					class="w-64 h-32 border-2 border-[#D4AF37] rounded-xl relative shadow-[0_0_0_9999px_rgba(0,0,0,0.5)]"
				>
					<div
						class="absolute top-1/2 left-0 right-0 h-0.5 bg-red-500/50 animate-pulse -translate-y-1/2"
					></div>
				</div>
				<p class="mt-4 text-white text-sm font-medium tracking-wide drop-shadow-md">
					Position barcode within frame
				</p>
			</div>

			<div
				v-if="errorMsg"
				class="absolute bottom-10 left-4 right-4 bg-red-500/90 text-white p-3 rounded-lg text-center text-sm font-medium"
			>
				{{ errorMsg }}
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { BrowserMultiFormatReader, NotFoundException } from '@zxing/library'

const emit = defineEmits(['close', 'scan'])

const videoElement = ref(null)
const errorMsg = ref('')

let codeReader = null

onMounted(async () => {
	try {
		codeReader = new BrowserMultiFormatReader()

		const videoInputDevices = await codeReader.listVideoInputDevices()

		if (!videoInputDevices || videoInputDevices.length === 0) {
			errorMsg.value = 'No camera found on this device.'
			return
		}

		// Prefer back camera
		const backCamera = videoInputDevices.find(
			(device) =>
				device.label.toLowerCase().includes('back') ||
				device.label.toLowerCase().includes('environment')
		)
		const selectedDeviceId = backCamera ? backCamera.deviceId : videoInputDevices[0].deviceId

		await codeReader.decodeFromVideoDevice(
			selectedDeviceId,
			videoElement.value,
			(result, err) => {
				if (result) {
					emit('scan', result.getText())
					emit('close')
				}
				if (err && !(err instanceof NotFoundException)) {
					console.error(err)
				}
			}
		)
	} catch (e) {
		console.error('Camera error:', e)
		errorMsg.value = 'Failed to access camera. Please check permissions.'
	}
})

onUnmounted(() => {
	if (codeReader) {
		codeReader.reset()
	}
})
</script>
