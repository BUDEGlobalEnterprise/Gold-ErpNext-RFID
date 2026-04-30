<template>
	<Teleport to="body">
		<Transition :name="transitionName" @after-enter="onAfterEnter">
			<div
				v-if="show"
				class="fixed inset-0 z-[100] flex"
				:class="isMobile ? 'items-end' : 'items-center justify-center p-4 sm:p-6'"
				@keydown.escape="onEscape"
				tabindex="-1"
				ref="overlayRef"
			>
				<!-- Backdrop -->
				<div
					class="absolute inset-0 bg-black/50 backdrop-blur-sm"
					@click="onBackdropClick"
				></div>

				<!-- Content: Bottom sheet on mobile, centered modal on desktop -->
				<div
					ref="contentRef"
					:class="[
						isMobile
							? 'bottom-sheet relative w-full rounded-t-2xl max-h-[92dvh]'
							: [maxWidthClass, 'relative rounded-2xl'],
						'bg-white dark:bg-warm-card shadow-2xl w-full overflow-hidden border border-transparent dark:border-warm-border flex flex-col',
						noMaxHeight ? '' : isMobile ? '' : 'max-h-[90vh]',
					]"
					:style="[!isMobile && fixedHeight ? { height: fixedHeight } : {}]"
					@touchstart.passive="onTouchStart"
					@touchmove.passive="onTouchMove"
					@touchend="onTouchEnd"
				>
					<!-- Drag handle for mobile bottom sheet -->
					<div v-if="isMobile" class="flex justify-center pt-3 pb-1 flex-shrink-0">
						<div class="w-10 h-1 bg-gray-300 dark:bg-gray-600 rounded-full"></div>
					</div>

					<!-- Header Slot -->
					<div
						v-if="$slots.header"
						class="flex items-center justify-between px-4 sm:px-6 py-4 border-b border-gray-100 dark:border-warm-border/50 flex-shrink-0"
					>
						<slot name="header"></slot>
						<button
							@click="close"
							class="p-2 hover:bg-gray-100 dark:hover:bg-warm-dark-700 rounded-full transition touch-target"
							aria-label="Close"
						>
							<svg
								class="w-5 h-5 text-gray-400"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M6 18L18 6M6 6l12 12"
								/>
							</svg>
						</button>
					</div>

					<!-- Close button when no header slot -->
					<button
						v-if="!$slots.header && showClose"
						@click="close"
						class="absolute top-4 right-4 p-2 hover:bg-gray-100 dark:hover:bg-warm-dark-700 rounded-full transition z-10 touch-target"
						aria-label="Close"
					>
						<svg
							class="w-5 h-5 text-gray-400"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M6 18L18 6M6 6l12 12"
							/>
						</svg>
					</button>

					<!-- Default Slot (Body) -->
					<div
						:class="[
							scrollable ? 'overflow-y-auto' : '',
							'flex-1 min-h-0',
							isMobile ? 'px-4 pb-4' : '',
						]"
					>
						<slot></slot>
					</div>

					<!-- Footer Slot -->
					<div
						v-if="$slots.footer"
						class="flex items-center justify-between gap-3 px-4 sm:px-6 py-4 border-t border-gray-100 dark:border-warm-border/50 bg-gray-50/50 dark:bg-warm-dark-900/50 flex-shrink-0"
					>
						<slot name="footer"></slot>
					</div>
				</div>
			</div>
		</Transition>
	</Teleport>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, computed } from 'vue'
import { useBreakpoint } from '@/composables/useBreakpoint.js'

const props = defineProps({
	show: { type: Boolean, default: false },
	maxWidth: { type: String, default: 'max-w-3xl' },
	persistent: { type: Boolean, default: false },
	scrollable: { type: Boolean, default: true },
	showClose: { type: Boolean, default: true },
	noMaxHeight: { type: Boolean, default: false },
	fixedHeight: { type: String, default: '' },
})

const emit = defineEmits(['close', 'update:show'])
const overlayRef = ref(null)
const contentRef = ref(null)
const { isMobile, reducedMotion } = useBreakpoint()

const maxWidthClass = props.maxWidth

// Transition: bottom sheet on mobile, scale on desktop
const transitionName = computed(() => {
	if (reducedMotion.value) return ''
	return isMobile.value ? 'bottom-sheet' : 'modal'
})

function close() {
	emit('close')
	emit('update:show', false)
}

function onBackdropClick() {
	if (!props.persistent) close()
}

function onEscape() {
	if (!props.persistent) close()
}

function onAfterEnter() {
	if (overlayRef.value) overlayRef.value.focus()
}

// Swipe-to-dismiss for bottom sheet
let touchStartY = 0
let currentY = 0
let isDragging = false

function onTouchStart(e) {
	if (!isMobile.value) return
	touchStartY = e.touches[0].clientY
	currentY = touchStartY
	isDragging = true
}

function onTouchMove(e) {
	if (!isDragging || !isMobile.value) return
	currentY = e.touches[0].clientY
	const diff = currentY - touchStartY
	if (diff > 0 && contentRef.value) {
		contentRef.value.style.transform = `translateY(${diff}px)`
		contentRef.value.style.transition = 'none'
	}
}

function onTouchEnd() {
	if (!isDragging || !isMobile.value) return
	isDragging = false
	const diff = currentY - touchStartY
	if (contentRef.value) {
		contentRef.value.style.transition = ''
		contentRef.value.style.transform = ''
	}
	if (diff > 80) {
		close()
	}
}

// Lock body scroll when modal is open
watch(
	() => props.show,
	(isOpen) => {
		if (isOpen) {
			document.body.style.overflow = 'hidden'
		} else {
			document.body.style.overflow = ''
		}
	}
)

onUnmounted(() => {
	document.body.style.overflow = ''
})
</script>

<style scoped>
/* Desktop modal transition */
.modal-enter-active,
.modal-leave-active {
	transition: opacity 0.2s ease;
}
.modal-enter-from,
.modal-leave-to {
	opacity: 0;
}
.modal-enter-active > div:last-child,
.modal-leave-active > div:last-child {
	transition: transform 0.2s ease, opacity 0.2s ease;
}
.modal-enter-from > div:last-child {
	transform: scale(0.95);
	opacity: 0;
}
.modal-leave-to > div:last-child {
	transform: scale(0.95);
	opacity: 0;
}

/* Mobile bottom sheet transition */
.bottom-sheet-enter-active,
.bottom-sheet-leave-active {
	transition: opacity 0.2s ease;
}
.bottom-sheet-enter-from,
.bottom-sheet-leave-to {
	opacity: 0;
}
.bottom-sheet-enter-active > div:last-child,
.bottom-sheet-leave-active > div:last-child {
	transition: transform 0.3s cubic-bezier(0.32, 0.72, 0, 1);
}
.bottom-sheet-enter-from > div:last-child {
	transform: translateY(100%);
}
.bottom-sheet-leave-to > div:last-child {
	transform: translateY(100%);
}

/* Bottom sheet safe area */
.bottom-sheet {
	padding-bottom: env(safe-area-inset-bottom, 0px);
}
</style>
