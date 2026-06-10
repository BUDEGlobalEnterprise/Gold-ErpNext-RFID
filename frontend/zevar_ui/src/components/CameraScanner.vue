<template>
	<!-- Outer wrapper for modal backdrop or normal flow -->
	<div
		:class="[
			!inline && !isFullscreen
				? 'fixed inset-0 z-[99999] flex items-center justify-center bg-black/75 p-4 backdrop-blur-sm'
				: '',
		]"
	>
		<div
			ref="containerRef"
			:class="[
				isFullscreen
					? 'fixed inset-0 z-[99999] flex flex-col bg-black'
					: inline
					? 'relative w-full h-[320px] rounded-xl overflow-hidden shadow-inner bg-black'
					: 'w-full max-w-md h-[420px] max-h-[85vh] bg-[#0F1115] border border-[#D4AF37]/40 rounded-2xl overflow-hidden shadow-2xl flex flex-col relative',
			]"
		>
			<div
				v-if="!inline || isFullscreen"
				class="flex items-center justify-between p-4 bg-black/80 text-white shrink-0"
			>
				<h3 class="font-bold text-lg">
					{{ isReviewMode ? 'Review Scanned Details' : headerTitle }}
				</h3>
				<div class="flex items-center gap-2">
					<!-- Fullscreen toggle -->
					<button
						@click="toggleFullscreen"
						class="p-2 bg-gray-800 hover:bg-gray-700 rounded-full transition-colors"
						:title="isFullscreen ? 'Exit fullscreen' : 'Fullscreen'"
					>
						<svg
							v-if="isFullscreen"
							class="w-6 h-6"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M9 9V4.5M9 9H4.5M9 9L3.75 3.75M9 15v4.5M9 15H4.5M9 15l-5.25 5.25M15 9h4.5M15 9V4.5M15 9l5.25-5.25M15 15h4.5M15 15v4.5m0-4.5l5.25 5.25"
							/>
						</svg>
						<svg
							v-else
							class="w-6 h-6"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M3.75 3.75v4.5m0-4.5h4.5m-4.5 0L9 9M3.75 20.25v-4.5m0 4.5h4.5m-4.5 0L9 15M20.25 3.75h-4.5m4.5 0v4.5m0-4.5L15 9m5.25 11.25h-4.5m4.5 0v-4.5m0 4.5L15 15"
							/>
						</svg>
					</button>
					<!-- Close button -->
					<button
						@click="close"
						class="p-2 bg-gray-800 hover:bg-gray-700 rounded-full transition-colors"
					>
						<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M6 18L18 6M6 6l12 12"
							/>
						</svg>
					</button>
				</div>
			</div>

			<!-- Inline close button (same position as original: top-2 right-2) -->
			<div v-if="inline && !isFullscreen" class="absolute top-2 right-2 z-10">
				<button
					@click="close"
					class="p-1.5 bg-black/50 hover:bg-black/80 text-white rounded-full transition-colors backdrop-blur-sm"
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
			<!-- Camera viewport / OCR views -->
			<div class="flex-1 relative overflow-hidden flex items-center justify-center bg-black">
				<!-- Review Mode Layout -->
				<div
					v-if="isReviewMode"
					class="absolute inset-0 overflow-y-auto p-4 bg-[#0F1115] text-white flex flex-col space-y-3 z-30"
				>
					<div
						class="flex items-center gap-3 bg-gray-900/60 p-2 rounded-xl border border-gray-800"
					>
						<img
							:src="capturedImage"
							class="w-16 h-12 object-cover rounded-lg border border-gray-700"
						/>
						<div>
							<h4 class="text-xs font-bold text-[#D4AF37]">
								Review Scanned Details
							</h4>
							<p class="text-[10px] text-gray-500">
								Edit fields below to correct any errors
							</p>
						</div>
					</div>

					<div class="space-y-3 flex-1">
						<div>
							<label
								class="block text-[10px] uppercase font-bold text-gray-500 mb-0.5"
								>Name</label
							>
							<input
								v-model="ocrFields.name"
								type="text"
								class="w-full px-2.5 py-1.5 bg-[#1a1c23] border border-gray-700 rounded-lg text-sm text-white focus:outline-none focus:ring-1 focus:ring-[#D4AF37]"
							/>
						</div>
						<div>
							<label
								class="block text-[10px] uppercase font-bold text-gray-500 mb-0.5"
								>ID Number</label
							>
							<input
								v-model="ocrFields.idNumber"
								type="text"
								class="w-full px-2.5 py-1.5 bg-[#1a1c23] border border-gray-700 rounded-lg text-sm text-white focus:outline-none focus:ring-1 focus:ring-[#D4AF37]"
							/>
						</div>
						<div>
							<label
								class="block text-[10px] uppercase font-bold text-gray-500 mb-0.5"
								>Date of Birth</label
							>
							<input
								v-model="ocrFields.dob"
								type="date"
								class="w-full px-2.5 py-1.5 bg-[#1a1c23] border border-gray-700 rounded-lg text-sm text-white focus:outline-none focus:ring-1 focus:ring-[#D4AF37]"
							/>
						</div>
						<div>
							<label
								class="block text-[10px] uppercase font-bold text-gray-500 mb-0.5"
								>Address</label
							>
							<textarea
								v-model="ocrFields.address"
								rows="2"
								class="w-full px-2.5 py-1.5 bg-[#1a1c23] border border-gray-700 rounded-lg text-sm text-white focus:outline-none focus:ring-1 focus:ring-[#D4AF37] resize-none"
							></textarea>
						</div>
					</div>

					<div class="flex gap-2 pt-2 border-t border-gray-800">
						<button
							@click="retryCamera"
							class="flex-1 py-2.5 text-xs font-semibold bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
						>
							Retake
						</button>
						<button
							@click="captureBackSide"
							class="flex-1 py-2.5 text-xs font-semibold bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
						>
							Scan Back Side
						</button>
						<button
							@click="onOcrConfirm"
							class="flex-1 py-2.5 text-xs font-semibold bg-[#D4AF37] text-black hover:bg-[#c4a030] rounded-lg transition-colors"
						>
							Confirm & Apply
						</button>
					</div>
				</div>

				<!-- OCR Loading Overlay -->
				<div
					v-else-if="isOcrLoading"
					class="absolute inset-0 flex flex-col items-center justify-center bg-black/90 text-white p-6 text-center z-30"
				>
					<div
						class="animate-spin rounded-full h-12 w-12 border-2 border-gray-400 border-t-[#D4AF37] mb-4"
					></div>
					<h4 class="text-lg font-bold mb-2">Analyzing ID Text</h4>
					<p class="text-sm text-gray-400 mb-6">
						{{
							isCapturingBack
								? 'Extracting back side details...'
								: 'Extracting details from card image...'
						}}
					</p>
					<button
						@click="cancelOcrLoading"
						class="px-4 py-2 bg-gray-800 hover:bg-gray-700 active:scale-95 text-white rounded-lg font-semibold text-xs transition-all duration-150 shadow-md border border-gray-750"
					>
						Cancel & Type Manually
					</button>
				</div>

				<!-- Standard Video / Target viewport -->
				<template v-else>
					<video
						ref="videoElement"
						class="w-full h-full object-cover"
						autoplay
						playsinline
						muted
						disablePictureInPicture
					></video>

					<!-- Scanner Target Overlay (same sizing as original: w-[85%] max-w-md h-64) -->
					<div
						class="absolute inset-0 pointer-events-none flex flex-col items-center justify-center"
					>
						<div
							:class="[
								isFullscreen
									? 'w-[70%] max-w-lg h-72'
									: inline
									? 'w-[80%] h-44'
									: 'w-[80%] h-48',
								'border-2 border-[#D4AF37] rounded-xl relative shadow-[0_0_0_9999px_rgba(0,0,0,0.6)]',
							]"
						>
							<!-- Scanning laser line (same as original) -->
							<div
								class="absolute top-1/2 left-0 right-0 h-0.5 bg-red-500/50 animate-pulse -translate-y-1/2"
							></div>
						</div>
						<p
							class="mt-4 text-white text-sm font-medium tracking-wide drop-shadow-md"
						>
							{{
								mode === 'id'
									? 'Flip ID over — scan the BARCODE on the BACK'
									: 'Position barcode within frame'
							}}
						</p>
						<p v-if="mode === 'id'" class="mt-1 text-gray-400 text-xs drop-shadow-md">
							The thick barcode on the back contains all ID data
						</p>
					</div>

					<!-- Bottom Buttons Overlay -->
					<div
						v-if="!inline"
						class="absolute bottom-4 left-0 right-0 flex flex-col items-center gap-3 z-20 pointer-events-auto px-4"
					>
						<!-- Main Manual Capture Button -->
						<button
							@click="manualCaptureAndParse"
							class="px-6 py-3 bg-[#D4AF37] hover:bg-[#c4a030] active:scale-95 text-black rounded-full font-extrabold text-sm shadow-xl flex items-center gap-2 transition-all duration-200 hover:shadow-[#D4AF37]/20 border border-[#D4AF37]"
						>
							<svg
								class="w-5 h-5"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2.2"
									d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"
								/>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2.2"
									d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"
								/>
							</svg>
							{{ mode === 'id' ? 'Capture & Parse ID' : 'Capture & Scan Barcode' }}
						</button>

						<div class="flex items-center gap-4">
							<button
								v-if="availableCameras.length > 1"
								@click="switchCamera"
								class="px-3.5 py-2 bg-gray-950/80 hover:bg-gray-900 border border-gray-800 text-white rounded-full font-bold text-xs shadow-lg flex items-center gap-1.5 transition-all hover:scale-105"
							>
								<svg
									class="w-3.5 h-3.5 text-gray-400"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2.5"
										d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
									/>
								</svg>
								Switch Lens
							</button>

							<!-- Small fallback link for manual entry -->
							<button
								v-if="mode === 'id'"
								@click="openManualEntry"
								class="px-3.5 py-2 bg-gray-950/80 hover:bg-gray-900 border border-gray-800 text-[#D4AF37] hover:text-[#c4a030] rounded-full font-bold text-xs shadow-lg flex items-center gap-1.5 transition-all hover:scale-105"
							>
								Type Manually
							</button>
						</div>
					</div>
				</template>

				<!-- Error message -->
				<div
					v-if="errorMsg && !showPermissionHelp"
					class="absolute bottom-10 left-4 right-4 bg-red-500/90 text-white p-3 rounded-lg text-center text-sm font-medium z-40"
				>
					{{ errorMsg }}
				</div>

				<!-- Permission help (shown when camera fails) -->
				<div
					v-if="showPermissionHelp"
					class="absolute inset-0 flex flex-col items-center justify-center bg-black/90 text-white p-6 text-center z-40"
				>
					<svg
						class="w-16 h-16 mb-4 text-red-400"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="1.5"
							d="M15.75 10.5l4.72-4.72a.75.75 0 011.28.53v11.38a.75.75 0 01-1.28.53l-4.72-4.72M4.5 18.75h9a2.25 2.25 0 002.25-2.25v-9a2.25 2.25 0 00-2.25-2.25h-9A2.25 2.25 0 002.25 7.5v9a2.25 2.25 0 002.25 2.25z"
						/>
					</svg>
					<h4 class="text-lg font-bold mb-2">Camera Access Required</h4>
					<p class="text-sm text-gray-300 mb-4">{{ permissionHelpText }}</p>
					<button
						@click="retryCamera"
						class="px-4 py-2 bg-[#D4AF37] text-black rounded-lg font-medium hover:bg-[#c4a030] transition-colors"
					>
						Try Again
					</button>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import {
	BrowserMultiFormatReader,
	NotFoundException,
	BarcodeFormat,
	DecodeHintType,
} from '@zxing/library'
import { playBeep } from '@/utils/beep.js'
import { isAAMVA, parseAAMVA } from '@/utils/idParser.js'

const props = defineProps({
	mode: {
		type: String,
		default: 'all', // 'all', 'id', 'barcode'
	},
	inline: {
		type: Boolean,
		default: false,
	},
	beep: {
		type: Boolean,
		default: true,
	},
})

const emit = defineEmits(['close', 'scan'])

const containerRef = ref(null)
const videoElement = ref(null)
const errorMsg = ref('')
const isFullscreen = ref(false)
const showPermissionHelp = ref(false)
const availableCameras = ref([])
const currentCameraIndex = ref(-1)

const capturedImage = ref('')

let codeReader = null
let mediaStream = null
let nativeScannerInterval = null
let barcodeDetector = null

if ('BarcodeDetector' in window) {
	try {
		barcodeDetector = new window.BarcodeDetector({
			formats: ['pdf417', 'qr_code', 'ean_13', 'code_128', 'code_39', 'upc_a'],
		})
	} catch (e) {
		console.warn('BarcodeDetector format not supported', e)
	}
}

const isReviewMode = ref(false)
const isOcrLoading = ref(false)
const isCapturingBack = ref(false)
const ocrText = ref('')
const ocrFields = ref({ name: '', idNumber: '', dob: '', address: '', type: 'State ID' })

async function manualCaptureAndParse() {
	if (!videoElement.value) return
	isOcrLoading.value = true
	errorMsg.value = ''

	try {
		const vid = videoElement.value
		const srcW = vid.videoWidth
		const srcH = vid.videoHeight
		if (!srcW || !srcH) {
			errorMsg.value = 'Camera not ready. Please try again.'
			isOcrLoading.value = false
			return
		}

		// Step 1: Capture raw frame
		const rawCanvas = document.createElement('canvas')
		rawCanvas.width = srcW
		rawCanvas.height = srcH
		const rawCtx = rawCanvas.getContext('2d')
		rawCtx.drawImage(vid, 0, 0, srcW, srcH)
		const frameDataUrl = rawCanvas.toDataURL('image/jpeg', 0.92)
		capturedImage.value = frameDataUrl

		// Step 2a: Try native BarcodeDetector first (fastest, works on Chrome/Android)
		if (barcodeDetector) {
			try {
				const barcodes = await barcodeDetector.detect(rawCanvas)
				if (barcodes && barcodes.length > 0) {
					console.log(
						'[ID Scanner] Native BarcodeDetector found barcode:',
						barcodes[0].rawValue
					)
					isOcrLoading.value = false
					onScanSuccess(barcodes[0].rawValue)
					return
				}
			} catch (nativeErr) {
				console.log('[ID Scanner] Native BarcodeDetector failed:', nativeErr)
			}
		}

		// Step 2b: Try zxing barcode reader
		const img = new Image()
		img.src = frameDataUrl
		await new Promise((resolve, reject) => {
			img.onload = resolve
			img.onerror = () => reject(new Error('Captured image load failed'))
		})

		let barcodeResult = null
		try {
			const hints = new Map()
			hints.set(DecodeHintType.POSSIBLE_FORMATS, getFormats())
			hints.set(DecodeHintType.TRY_HARDER, true)
			const tempReader = new BrowserMultiFormatReader(hints)
			barcodeResult = await tempReader.decodeFromImageElement(img)
			tempReader.reset()
		} catch (barcodeErr) {
			console.log(
				'[ID Scanner] zxing barcode decode failed on manual capture:',
				barcodeErr.message
			)
		}

		if (barcodeResult) {
			const text = barcodeResult.getText()
			console.log('[ID Scanner] Barcode found in manual capture:', text)
			isOcrLoading.value = false
			onScanSuccess(text)
			return
		}

		// Step 3: No barcode found — go straight to manual entry form (no OCR)
		// The barcode on the BACK of the ID is the reliable data source.
		// If user is scanning the front, let them type manually.
		console.log('[ID Scanner] No barcode detected. Opening manual entry form.')
		isOcrLoading.value = false
		stopScanner()

		if (props.mode === 'id') {
			// Show the review form with empty fields for manual entry
			ocrFields.value = { name: '', idNumber: '', dob: '', address: '', type: 'State ID' }
			isReviewMode.value = true
			errorMsg.value =
				'No barcode found. Flip ID to scan the barcode on the back, or type details below.'
		} else {
			errorMsg.value =
				'No barcode detected. Please align the barcode within the frame and try again.'
		}
	} catch (e) {
		console.error('Manual capture/parse error:', e)
		errorMsg.value = 'Capture failed. Please try again.'
		isOcrLoading.value = false
	}
}

function captureBackSide() {
	isReviewMode.value = false
	isCapturingBack.value = true
	retryCamera()
}

function onOcrConfirm() {
	if (props.beep) {
		playBeep()
	}
	if (props.mode === 'barcode') {
		emit('scan', ocrFields.value.idNumber)
	} else if (isReviewMode.value) {
		// Emit the exact signature ScannerInput expects: @scan="handleCameraScan(value, ocrParsedData)"
		emit('scan', ocrFields.value.idNumber, {
			name: ocrFields.value.name,
			idNumber: ocrFields.value.idNumber,
			dob: ocrFields.value.dob,
			address: ocrFields.value.address,
			type: ocrFields.value.type,
		})
	}
	close()
}

const headerTitle = computed(() => {
	if (props.mode === 'id') return "Scan ID / Driver's License"
	if (props.mode === 'barcode') return 'Scan Barcode'
	return 'Scan Barcode or ID'
})

const permissionHelpText = computed(() => {
	if (location.protocol !== 'https:' && location.hostname !== 'localhost') {
		return 'Camera access requires HTTPS. Please load this page over a secure connection (https://).'
	}
	return 'Please allow camera access in your browser settings and try again.'
})

function getFormats() {
	// For maximum compatibility (especially internationally), allow all standard
	// barcode formats even when in 'id' mode, so QR codes and generic barcodes work.
	return [
		BarcodeFormat.PDF_417,
		BarcodeFormat.QR_CODE,
		BarcodeFormat.EAN_13,
		BarcodeFormat.EAN_8,
		BarcodeFormat.CODE_128,
		BarcodeFormat.CODE_39,
		BarcodeFormat.CODE_93,
		BarcodeFormat.UPC_A,
		BarcodeFormat.UPC_E,
	]
}

function getOrientationConstraints() {
	const isPortrait = window.innerHeight > window.innerWidth
	return {
		width: { ideal: isPortrait ? 1080 : 1920 },
		height: { ideal: isPortrait ? 1920 : 1080 },
	}
}

function buildConstraints(deviceId) {
	const { width, height } = getOrientationConstraints()
	const video = {
		width,
		height,
		facingMode: 'environment',
	}
	if (deviceId) {
		video.deviceId = { exact: deviceId }
	}
	return { video }
}

async function applyAdvancedConstraints(track) {
	try {
		const capabilities = track.getCapabilities ? track.getCapabilities() : {}
		const advanced = []
		if (capabilities.focusMode) {
			if (capabilities.focusMode.includes('continuous')) {
				advanced.push({ focusMode: 'continuous' })
			} else if (capabilities.focusMode.includes('macro')) {
				advanced.push({ focusMode: 'macro' })
			} else if (capabilities.focusMode.includes('auto')) {
				advanced.push({ focusMode: 'auto' })
			}
		}
		if (advanced.length > 0) {
			await track.applyConstraints({ advanced })
		}
	} catch {
		// Device doesn't support focus constraints — continue without auto-focus
	}
}

async function acquireStream(deviceId) {
	// Attempt 1: Full HD + specific device
	try {
		return await navigator.mediaDevices.getUserMedia(buildConstraints(deviceId))
	} catch (e) {
		if (e.name !== 'OverconstrainedError' && e.name !== 'NotFoundError') throw e
	}

	// Attempt 2: HD without specific device, just facingMode
	try {
		const { width, height } = getOrientationConstraints()
		return await navigator.mediaDevices.getUserMedia({
			video: { width, height, facingMode: 'environment' },
		})
	} catch (e) {
		if (e.name !== 'OverconstrainedError') throw e
	}

	// Attempt 3: Any camera
	return navigator.mediaDevices.getUserMedia({ video: true })
}

async function initScanner() {
	errorMsg.value = ''
	showPermissionHelp.value = false

	const isSecure =
		location.protocol === 'https:' ||
		location.hostname === 'localhost' ||
		location.hostname === '127.0.0.1'
	if (!isSecure) {
		errorMsg.value = 'Camera requires HTTPS. Please use a secure connection.'
		showPermissionHelp.value = true
		return
	}

	if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
		errorMsg.value = 'Camera API not available in this browser.'
		return
	}

	try {
		const devices = await navigator.mediaDevices.enumerateDevices()
		availableCameras.value = devices.filter((d) => d.kind === 'videoinput')

		if (availableCameras.value.length === 0) {
			errorMsg.value = 'No camera found on this device.'
			return
		}

		if (currentCameraIndex.value === -1) {
			let bestIdx = 0
			for (let i = 0; i < availableCameras.value.length; i++) {
				const label = availableCameras.value[i].label.toLowerCase()
				if (label.includes('back') || label.includes('environment')) {
					bestIdx = i
					if (label.includes('0') || label.includes('main')) break
				}
			}
			currentCameraIndex.value = bestIdx
		}

		const deviceId = availableCameras.value[currentCameraIndex.value]?.deviceId || null

		const stream = await acquireStream(deviceId)
		mediaStream = stream

		const videoTrack = stream.getVideoTracks()[0]
		if (videoTrack) {
			await applyAdvancedConstraints(videoTrack)
		}

		videoElement.value.srcObject = stream
		await videoElement.value.play()

		const hints = new Map()
		hints.set(DecodeHintType.POSSIBLE_FORMATS, getFormats())
		hints.set(DecodeHintType.TRY_HARDER, true)

		codeReader = new BrowserMultiFormatReader(hints)
		codeReader.decodeFromVideoElementContinuously(videoElement.value, (result, err) => {
			if (result) {
				onScanSuccess(result.getText())
			}
			if (err && !(err instanceof NotFoundException)) {
				// Expected scan noise
			}
		})

		// Start Native BarcodeDetector if available (much faster for PDF417)
		if (barcodeDetector) {
			nativeScannerInterval = setInterval(async () => {
				if (
					!videoElement.value ||
					isOcrLoading.value ||
					isReviewMode.value ||
					videoElement.value.readyState !== 4
				)
					return
				try {
					const barcodes = await barcodeDetector.detect(videoElement.value)
					if (barcodes && barcodes.length > 0) {
						onScanSuccess(barcodes[0].rawValue)
					}
				} catch (err) {
					// Silent ignore
				}
			}, 300)
		}
	} catch (e) {
		console.error('Camera error:', e)
		handleCameraError(e)
	}
}

function handleCameraError(e) {
	if (e.name === 'NotAllowedError' || e.name === 'PermissionDeniedError') {
		showPermissionHelp.value = true
		errorMsg.value = 'Camera permission was denied.'
	} else if (e.name === 'NotFoundError' || e.name === 'DevicesNotFoundError') {
		errorMsg.value = 'No camera found on this device.'
	} else if (e.name === 'NotReadableError' || e.name === 'TrackStartError') {
		errorMsg.value = 'Camera is already in use by another application.'
	} else if (e.name === 'OverconstrainedError') {
		errorMsg.value = 'Camera does not support the requested settings.'
	} else {
		errorMsg.value = `Camera error: ${e.message || e.name || e}`
	}
}

function onScanSuccess(text) {
	if (props.beep) {
		playBeep()
	}

	if (props.mode === 'id') {
		if (isAAMVA(text)) {
			console.log('[ID Scanner] AAMVA barcode detected, parsing...')
			const parsed = parseAAMVA(text)
			console.log('[ID Scanner] Parsed AAMVA:', parsed)
			stopScanner()
			ocrFields.value = {
				name: parsed.name || '',
				idNumber: parsed.idNumber || '',
				dob: parsed.dob || '',
				address: [parsed.address, parsed.city, parsed.state, parsed.zip]
					.filter(Boolean)
					.join(', '),
				type: "Driver's License",
			}
			capturedImage.value = '' // No photo needed for barcode scans
			isReviewMode.value = true
			return
		} else {
			// Try parsing as JSON for generic testing (e.g. {"name": "Test", "id": "123"})
			try {
				const parsed = JSON.parse(text)
				stopScanner()
				ocrFields.value = {
					name: parsed.name || '',
					idNumber: parsed.idNumber || parsed.id || text.substring(0, 30),
					dob: parsed.dob || '',
					address: parsed.address || '',
					type: parsed.type || 'Generic ID',
				}
				capturedImage.value = ''
				isReviewMode.value = true
				return
			} catch (e) {
				// Not JSON, dump raw text into ID field
				stopScanner()
				ocrFields.value = {
					name: '',
					idNumber: text.substring(0, 50), // Truncate just in case it's huge
					dob: '',
					address: '',
					type: 'Generic ID',
				}
				capturedImage.value = ''
				isReviewMode.value = true
				return
			}
		}
	}

	emit('scan', text)
	close()
}

function cancelOcrLoading() {
	isOcrLoading.value = false
	openManualEntry()
}

function openManualEntry() {
	stopScanner()
	ocrFields.value = { name: '', idNumber: '', dob: '', address: '', type: 'State ID' }
	capturedImage.value = ''
	isReviewMode.value = true
}

function close() {
	emit('close')
}

function retryCamera() {
	isReviewMode.value = false
	stopScanner()
	nextTick(() => {
		initScanner()
	})
}

function switchCamera() {
	if (availableCameras.value.length <= 1) return
	currentCameraIndex.value = (currentCameraIndex.value + 1) % availableCameras.value.length
	retryCamera()
}

function stopScanner() {
	if (codeReader) {
		codeReader.reset()
		codeReader = null
	}
	if (nativeScannerInterval) {
		clearInterval(nativeScannerInterval)
		nativeScannerInterval = null
	}
	if (mediaStream) {
		mediaStream.getTracks().forEach((track) => track.stop())
		mediaStream = null
	}
	if (videoElement.value) {
		videoElement.value.srcObject = null
	}
}

function toggleFullscreen() {
	isFullscreen.value = !isFullscreen.value
}

onMounted(() => {
	initScanner()
})

onUnmounted(() => {
	stopScanner()
})
</script>
