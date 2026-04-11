<template>
	<Teleport to="body">
		<div
			class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm"
			@click.self="$emit('close')"
		>
			<div
				class="bg-white dark:bg-gray-900 rounded-2xl shadow-xl max-w-2xl w-full mx-4 overflow-hidden"
			>
				<div
					class="p-4 border-b border-gray-100 dark:border-gray-800 flex justify-between items-center"
				>
					<h3 class="text-lg font-bold text-gray-900 dark:text-white">Capture Photo</h3>
					<button
						@click="$emit('close')"
						class="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-full"
					>
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M6 18L18 6M6 6l12 12"
							/>
						</svg>
					</button>
				</div>

				<div class="p-4">
					<!-- Photo Type Selection -->
					<div class="flex gap-2 mb-4">
						<button
							@click="photoType = 'before'"
							:class="
								photoType === 'before' ? 'bg-blue-500 text-white' : 'bg-gray-100'
							"
							class="px-4 py-2 rounded-lg text-sm font-medium"
						>
							Before Repair
						</button>
						<button
							@click="photoType = 'after'"
							:class="
								photoType === 'after' ? 'bg-green-500 text-white' : 'bg-gray-100'
							"
							class="px-4 py-2 rounded-lg text-sm font-medium"
						>
							After Repair
						</button>
					</div>

					<!-- Camera View -->
					<div class="relative bg-black rounded-lg overflow-hidden aspect-video mb-4">
						<video
							ref="videoElement"
							autoplay
							playsinline
							class="w-full h-full object-cover"
						></video>
						<canvas ref="canvasElement" class="hidden"></canvas>

						<!-- Fallback message -->
						<div
							v-if="!cameraActive"
							class="absolute inset-0 flex items-center justify-center text-white"
						>
							<p>Camera unavailable</p>
						</div>

						<!-- Camera Overlay -->
						<div v-if="cameraActive" class="absolute inset-0 pointer-events-none">
							<div
								class="absolute inset-4 border-2 border-white/30 rounded-lg"
							></div>
							<div
								class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-16 h-16 border-2 border-[#D4AF37] rounded-full"
							></div>
						</div>
					</div>

					<!-- Camera Controls -->
					<div class="flex items-center justify-center gap-4">
						<button
							@click="switchCamera"
							v-if="hasMultipleCameras"
							class="p-3 bg-gray-100 dark:bg-gray-800 rounded-full hover:bg-gray-200"
						>
							<svg
								class="w-6 h-6"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
								/>
							</svg>
						</button>

						<button
							@click="capturePhoto"
							:disabled="!cameraActive"
							class="p-4 bg-[#D4AF37] rounded-full hover:bg-[#c9a432] disabled:opacity-50 disabled:cursor-not-allowed"
						>
							<svg class="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
								<circle cx="12" cy="12" r="10" fill="white" />
							</svg>
						</button>

						<button
							@click="uploadFile"
							class="p-3 bg-gray-100 dark:bg-gray-800 rounded-full hover:bg-gray-200"
						>
							<svg
								class="w-6 h-6"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"
								/>
							</svg>
						</button>
						<input
							ref="fileInput"
							type="file"
							accept="image/*"
							class="hidden"
							@change="handleFileUpload"
						/>
					</div>

					<!-- Captured Preview -->
					<div v-if="capturedImage" class="mt-4">
						<p class="text-sm font-medium text-gray-700 mb-2">Captured Image:</p>
						<img :src="capturedImage" class="max-h-48 rounded-lg" />
						<div class="flex gap-2 mt-2">
							<button
								@click="retakePhoto"
								class="px-4 py-2 bg-gray-100 rounded-lg text-sm"
							>
								Retake
							</button>
							<button
								@click="confirmPhoto"
								class="px-4 py-2 bg-[#D4AF37] text-black rounded-lg text-sm font-medium"
							>
								Use Photo
							</button>
						</div>
					</div>
				</div>
			</div>
		</div>
	</Teleport>
</template>

<script setup>
import { ref, onMounted, onUnmounted, defineEmits } from 'vue'

const emit = defineEmits(['close', 'photo-captured'])

const videoElement = ref(null)
const canvasElement = ref(null)
const fileInput = ref(null)
const cameraActive = ref(false)
const hasMultipleCameras = ref(false)
const capturedImage = ref(null)
const photoType = ref('before')

let stream = null
let currentCameraIndex = 0

async function initCamera() {
	try {
		const devices = await navigator.mediaDevices.enumerateDevices()
		const videoDevices = devices.filter((device) => device.kind === 'videoinput')
		hasMultipleCameras.value = videoDevices.length > 1

		stream = await navigator.mediaDevices.getUserMedia({
			video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } },
		})

		if (videoElement.value) {
			videoElement.value.srcObject = stream
			cameraActive.value = true
		}
	} catch (e) {
		console.error('Camera init failed:', e)
		cameraActive.value = false
	}
}

async function switchCamera() {
	if (stream) {
		stream.getTracks().forEach((track) => track.stop())
	}

	currentCameraIndex = currentCameraIndex === 0 ? 1 : 0

	try {
		stream = await navigator.mediaDevices.getUserMedia({
			video: { facingMode: currentCameraIndex === 0 ? 'environment' : 'user' },
		})

		if (videoElement.value) {
			videoElement.value.srcObject = stream
		}
	} catch (e) {
		console.error('Camera switch failed:', e)
	}
}

function capturePhoto() {
	if (!videoElement.value || !canvasElement.value) return

	const video = videoElement.value
	const canvas = canvasElement.value

	canvas.width = video.videoWidth
	canvas.height = video.videoHeight

	const ctx = canvas.getContext('2d')
	ctx.drawImage(video, 0, 0)

	capturedImage.value = canvas.toDataURL('image/jpeg', 0.9)
}

function retakePhoto() {
	capturedImage.value = null
}

function confirmPhoto() {
	emit('photo-captured', {
		data: capturedImage.value,
		type: photoType.value,
	})
}

function uploadFile() {
	fileInput.value.click()
}

function handleFileUpload(event) {
	const file = event.target.files[0]
	if (!file) return

	const reader = new FileReader()
	reader.onload = (e) => {
		capturedImage.value = e.target.result
	}
	reader.readAsDataURL(file)
}

onMounted(() => {
	initCamera()
})

onUnmounted(() => {
	if (stream) {
		stream.getTracks().forEach((track) => track.stop())
	}
})
</script>
