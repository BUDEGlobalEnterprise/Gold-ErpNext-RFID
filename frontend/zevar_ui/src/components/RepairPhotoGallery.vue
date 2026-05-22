<template>
	<div class="repair-photo-gallery">
		<!-- Gallery Header -->
		<div class="flex items-center justify-between mb-3">
			<h4 class="text-xs font-bold text-gray-500 uppercase tracking-wider">
				Photo Documentation
				<span v-if="allPhotos.length" class="ml-1 text-[10px] font-normal text-gray-400">({{ allPhotos.length }})</span>
			</h4>
			<div class="flex items-center gap-2">
				<button
					v-if="beforePhotos.length && afterPhotos.length"
					@click="showComparison = !showComparison"
					class="text-[10px] px-2 py-1 bg-[#D4AF37]/10 text-[#D4AF37] rounded-full font-bold hover:bg-[#D4AF37]/20 transition"
				>
					{{ showComparison ? '✕ Close' : '⬌ Compare' }}
				</button>
				<button
					v-if="canAddPhotos"
					@click="$emit('add-photo')"
					class="text-[10px] px-2 py-1 bg-gray-100 dark:bg-warm-dark-900 rounded-full font-bold hover:bg-gray-200 transition"
				>
					+ Add Photo
				</button>
			</div>
		</div>

		<!-- Before/After Comparison Slider -->
		<div v-if="showComparison && beforePhotos.length && afterPhotos.length" class="mb-4">
			<BeforeAfterSlider
				:beforeSrc="beforePhotos[comparisonBeforeIdx]"
				:afterSrc="afterPhotos[comparisonAfterIdx]"
				:height="280"
			/>
			<!-- Navigation if multiple photos -->
			<div v-if="beforePhotos.length > 1 || afterPhotos.length > 1" class="flex justify-center gap-4 mt-2">
				<div v-if="beforePhotos.length > 1" class="flex gap-1">
					<button
						v-for="(_, idx) in beforePhotos" :key="'b'+idx"
						@click="comparisonBeforeIdx = idx"
						class="w-2 h-2 rounded-full transition"
						:class="idx === comparisonBeforeIdx ? 'bg-blue-500' : 'bg-gray-300'"
					></button>
				</div>
				<div v-if="afterPhotos.length > 1" class="flex gap-1">
					<button
						v-for="(_, idx) in afterPhotos" :key="'a'+idx"
						@click="comparisonAfterIdx = idx"
						class="w-2 h-2 rounded-full transition"
						:class="idx === comparisonAfterIdx ? 'bg-green-500' : 'bg-gray-300'"
					></button>
				</div>
			</div>
		</div>

		<!-- Photo Grid -->
		<div v-if="!showComparison">
			<!-- Before Photos -->
			<div v-if="beforePhotos.length" class="mb-3">
				<p class="text-[10px] font-bold text-blue-600 dark:text-blue-400 uppercase mb-1.5 flex items-center gap-1">
					<span class="w-2 h-2 rounded-full bg-blue-500"></span>
					Before Repair ({{ beforePhotos.length }})
				</p>
				<div class="grid grid-cols-3 gap-1.5">
					<div
						v-for="(photo, idx) in beforePhotos"
						:key="'before-' + idx"
						class="relative group cursor-pointer rounded-lg overflow-hidden aspect-square"
						@click="openLightbox('before', idx)"
					>
						<img
							:src="photo"
							class="w-full h-full object-cover transition-transform duration-200 group-hover:scale-105"
							:alt="'Before photo ' + (idx + 1)"
						/>
						<div class="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors flex items-center justify-center">
							<svg class="w-5 h-5 text-white opacity-0 group-hover:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
							</svg>
						</div>
					</div>
				</div>
			</div>

			<!-- After Photos -->
			<div v-if="afterPhotos.length">
				<p class="text-[10px] font-bold text-green-600 dark:text-green-400 uppercase mb-1.5 flex items-center gap-1">
					<span class="w-2 h-2 rounded-full bg-green-500"></span>
					After Repair ({{ afterPhotos.length }})
				</p>
				<div class="grid grid-cols-3 gap-1.5">
					<div
						v-for="(photo, idx) in afterPhotos"
						:key="'after-' + idx"
						class="relative group cursor-pointer rounded-lg overflow-hidden aspect-square"
						@click="openLightbox('after', idx)"
					>
						<img
							:src="photo"
							class="w-full h-full object-cover transition-transform duration-200 group-hover:scale-105"
							:alt="'After photo ' + (idx + 1)"
						/>
						<div class="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors flex items-center justify-center">
							<svg class="w-5 h-5 text-white opacity-0 group-hover:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
							</svg>
						</div>
					</div>
				</div>
			</div>

			<!-- Empty State -->
			<div v-if="!beforePhotos.length && !afterPhotos.length" class="text-center py-4">
				<svg class="w-10 h-10 text-gray-300 dark:text-gray-600 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
						d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
						d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
				</svg>
				<p class="text-xs text-gray-400">No photos attached yet</p>
			</div>
		</div>

		<!-- Lightbox Modal -->
		<div
			v-if="lightboxOpen"
			class="fixed inset-0 z-[100] bg-black/90 flex items-center justify-center p-4"
			@click.self="closeLightbox"
		>
			<button
				@click="closeLightbox"
				class="absolute top-4 right-4 z-10 w-10 h-10 bg-white/10 rounded-full flex items-center justify-center hover:bg-white/20 transition"
			>
				<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
				</svg>
			</button>

			<!-- Label -->
			<div class="absolute top-4 left-4 z-10">
				<span class="px-3 py-1 rounded-full text-xs font-bold text-white"
					:class="lightboxType === 'before' ? 'bg-blue-500/80' : 'bg-green-500/80'">
					{{ lightboxType === 'before' ? 'BEFORE' : 'AFTER' }} {{ lightboxIdx + 1 }}/{{ lightboxType === 'before' ? beforePhotos.length : afterPhotos.length }}
				</span>
			</div>

			<!-- Navigation -->
			<button
				v-if="canGoPrev"
				@click.stop="prevPhoto"
				class="absolute left-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-white/10 rounded-full flex items-center justify-center hover:bg-white/20 transition"
			>
				<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
				</svg>
			</button>
			<button
				v-if="canGoNext"
				@click.stop="nextPhoto"
				class="absolute right-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-white/10 rounded-full flex items-center justify-center hover:bg-white/20 transition"
			>
				<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
				</svg>
			</button>

			<img
				:src="lightboxSrc"
				class="max-w-full max-h-[85vh] object-contain rounded-lg shadow-2xl"
				:alt="lightboxType + ' photo'"
			/>
		</div>
	</div>
</template>

<script setup>
import { ref, computed } from 'vue'
import BeforeAfterSlider from './BeforeAfterSlider.vue'

const props = defineProps({
	/** Array of before photo URLs */
	beforePhotos: { type: Array, default: () => [] },
	/** Array of after photo URLs */
	afterPhotos: { type: Array, default: () => [] },
	/** Whether the user can add photos (repair not delivered) */
	canAddPhotos: { type: Boolean, default: false },
})

defineEmits(['add-photo'])

const showComparison = ref(false)
const comparisonBeforeIdx = ref(0)
const comparisonAfterIdx = ref(0)

// Lightbox state
const lightboxOpen = ref(false)
const lightboxType = ref('before')
const lightboxIdx = ref(0)

const allPhotos = computed(() => [...props.beforePhotos, ...props.afterPhotos])

const lightboxSrc = computed(() => {
	const photos = lightboxType.value === 'before' ? props.beforePhotos : props.afterPhotos
	return photos[lightboxIdx.value] || ''
})

const canGoPrev = computed(() => lightboxIdx.value > 0)
const canGoNext = computed(() => {
	const photos = lightboxType.value === 'before' ? props.beforePhotos : props.afterPhotos
	return lightboxIdx.value < photos.length - 1
})

function openLightbox(type, idx) {
	lightboxType.value = type
	lightboxIdx.value = idx
	lightboxOpen.value = true
}

function closeLightbox() {
	lightboxOpen.value = false
}

function prevPhoto() {
	if (canGoPrev.value) lightboxIdx.value--
}

function nextPhoto() {
	if (canGoNext.value) lightboxIdx.value++
}
</script>
