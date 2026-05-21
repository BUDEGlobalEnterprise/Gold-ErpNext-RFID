<template>
	<Teleport to="body">
		<Transition name="modal" @after-enter="onAfterEnter">
			<div
				v-if="show"
				class="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6"
				@keydown.escape="onEscape"
				tabindex="-1"
				ref="overlayRef"
			>
				<!-- Backdrop -->
				<div
					class="absolute inset-0 bg-black/50 backdrop-blur-sm"
					@click="onBackdropClick"
				></div>

				<!-- Content -->
				<div
					:class="[
						maxWidth,
						'relative bg-white dark:bg-warm-card rounded-2xl shadow-2xl w-full overflow-hidden border border-transparent dark:border-warm-border flex flex-col',
						noMaxHeight ? '' : 'max-h-[90vh]',
						fixedHeight ? '' : '',
					]"
					:style="fixedHeight ? { height: fixedHeight } : {}"
				>
					<!-- Header Slot -->
					<div
						v-if="$slots.header"
						class="flex items-center justify-between p-6 border-b border-gray-100 dark:border-warm-border/50 flex-shrink-0"
					>
						<slot name="header"></slot>
						<button
							@click="close"
							class="p-2 hover:bg-gray-100 dark:hover:bg-warm-dark-700 rounded-full transition"
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
						class="absolute top-4 right-4 p-2 hover:bg-gray-100 dark:hover:bg-warm-dark-700 rounded-full transition z-10"
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
					<div :class="[scrollable ? 'overflow-y-auto' : '', 'flex-1 min-h-0']">
						<slot></slot>
					</div>

					<!-- Footer Slot -->
					<div
						v-if="$slots.footer"
						class="flex items-center justify-between gap-3 p-4 border-t border-gray-100 dark:border-warm-border/50 bg-gray-50/50 dark:bg-warm-dark-900/50 flex-shrink-0"
					>
						<slot name="footer"></slot>
					</div>
				</div>
			</div>
		</Transition>
	</Teleport>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'

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

function close() {
	emit('close')
	emit('update:show', false)
}

function onBackdropClick() {
	if (!props.persistent) {
		close()
	}
}

function onEscape() {
	if (!props.persistent) {
		close()
	}
}

function onAfterEnter() {
	if (overlayRef.value) {
		overlayRef.value.focus()
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
</style>
