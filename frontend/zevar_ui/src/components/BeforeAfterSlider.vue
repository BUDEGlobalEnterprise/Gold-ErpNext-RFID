<template>
	<div
		class="before-after-slider relative select-none overflow-hidden rounded-xl border border-gray-200 dark:border-warm-border"
		:style="{ height: height + 'px' }"
	>
		<!-- After image (background) -->
		<img
			v-if="afterSrc"
			:src="afterSrc"
			class="absolute inset-0 w-full h-full object-cover"
			alt="After repair"
			draggable="false"
		/>

		<!-- Before image (clipped) -->
		<div class="absolute inset-0 overflow-hidden" :style="{ width: sliderPosition + '%' }">
			<img
				v-if="beforeSrc"
				:src="beforeSrc"
				class="absolute inset-0 w-full h-full object-cover"
				:style="{ width: containerWidth + 'px' }"
				alt="Before repair"
				draggable="false"
			/>
		</div>

		<!-- Slider handle -->
		<div
			class="absolute top-0 bottom-0 z-10 cursor-ew-resize"
			:style="{ left: `calc(${sliderPosition}% - 16px)` }"
			@mousedown.prevent="startDrag"
			@touchstart.prevent="startDrag"
		>
			<div class="w-8 h-full flex items-center justify-center">
				<div class="w-[3px] h-full bg-white shadow-lg"></div>
				<div
					class="absolute top-1/2 -translate-y-1/2 w-8 h-8 bg-white rounded-full shadow-lg flex items-center justify-center"
				>
					<svg
						class="w-4 h-4 text-gray-600"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M8 7l-4 5 4 5M16 7l4 5-4 5"
						/>
					</svg>
				</div>
			</div>
		</div>

		<!-- Labels -->
		<div class="absolute top-3 left-3 z-20">
			<span
				class="px-2 py-1 bg-blue-500/80 text-white text-[10px] font-bold rounded-full backdrop-blur-sm"
				>BEFORE</span
			>
		</div>
		<div class="absolute top-3 right-3 z-20">
			<span
				class="px-2 py-1 bg-green-500/80 text-white text-[10px] font-bold rounded-full backdrop-blur-sm"
				>AFTER</span
			>
		</div>

		<!-- Empty state -->
		<div
			v-if="!beforeSrc && !afterSrc"
			class="absolute inset-0 flex items-center justify-center bg-gray-100 dark:bg-warm-dark-900"
		>
			<div class="text-center text-gray-400">
				<svg
					class="w-8 h-8 mx-auto mb-2"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="1.5"
						d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
					/>
				</svg>
				<p class="text-xs">No photos to compare</p>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

defineProps({
	/** URL to the "before" image */
	beforeSrc: { type: String, default: '' },
	/** URL to the "after" image */
	afterSrc: { type: String, default: '' },
	/** Container height in px */
	height: { type: Number, default: 280 },
})

const sliderPosition = ref(50)
const isDragging = ref(false)
const containerWidth = ref(0)
const containerRef = ref(null)

function startDrag() {
	isDragging.value = true
	document.addEventListener('mousemove', onDrag)
	document.addEventListener('mouseup', stopDrag)
	document.addEventListener('touchmove', onDrag, { passive: false })
	document.addEventListener('touchend', stopDrag)
}

function onDrag(e) {
	if (!isDragging.value) return
	e.preventDefault()

	const container =
		e.target.closest('.before-after-slider') || document.querySelector('.before-after-slider')
	if (!container) return

	const rect = container.getBoundingClientRect()
	const clientX = e.touches ? e.touches[0].clientX : e.clientX
	const x = clientX - rect.left
	const percent = Math.max(0, Math.min(100, (x / rect.width) * 100))
	sliderPosition.value = percent
}

function stopDrag() {
	isDragging.value = false
	document.removeEventListener('mousemove', onDrag)
	document.removeEventListener('mouseup', stopDrag)
	document.removeEventListener('touchmove', onDrag)
	document.removeEventListener('touchend', stopDrag)
}

onMounted(() => {
	const el = document.querySelector('.before-after-slider')
	if (el) containerWidth.value = el.offsetWidth
})

onUnmounted(() => {
	stopDrag()
})
</script>
