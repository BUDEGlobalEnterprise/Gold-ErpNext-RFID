<template>
	<Teleport to="body">
		<TransitionGroup
			tag="div"
			class="fixed top-4 right-4 z-[99999] flex flex-col gap-2 pointer-events-none"
			enter-active-class="transition-all duration-300 ease-out"
			enter-from-class="opacity-0 translate-x-8 scale-95"
			enter-to-class="opacity-100 translate-x-0 scale-100"
			leave-active-class="transition-all duration-200 ease-in"
			leave-from-class="opacity-100 translate-x-0 scale-100"
			leave-to-class="opacity-0 translate-x-8 scale-95"
		>
			<div
				v-for="toast in toasts"
				:key="toast.id"
				class="pointer-events-auto max-w-sm w-full rounded-xl shadow-2xl border backdrop-blur-xl p-4 flex items-start gap-3"
				:class="toastClass(toast.type)"
			>
				<!-- Icon -->
				<div class="flex-shrink-0 mt-0.5">
					<!-- Success -->
					<svg v-if="toast.type === 'success'" class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
					<!-- Error -->
					<svg v-else-if="toast.type === 'error'" class="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
					<!-- Warning -->
					<svg v-else-if="toast.type === 'warning'" class="w-5 h-5 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
					</svg>
					<!-- Info -->
					<svg v-else class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
				</div>
				<!-- Content -->
				<div class="flex-1 min-w-0">
					<div v-if="toast.title" class="font-bold text-sm">{{ toast.title }}</div>
					<div class="text-sm opacity-80">{{ toast.message }}</div>
				</div>
				<!-- Close -->
				<button
					@click="dismiss(toast.id)"
					class="flex-shrink-0 p-1 rounded-lg hover:bg-black/10 dark:hover:bg-white/10 transition opacity-60 hover:opacity-100"
				>
					<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
					</svg>
				</button>
			</div>
		</TransitionGroup>
	</Teleport>
</template>

<script setup>
import { ref } from 'vue'

const toasts = ref([])
let nextId = 0

function toastClass(type) {
	switch (type) {
		case 'success':
			return 'bg-white dark:bg-[#1a1c23] border-green-200 dark:border-green-800/30 text-gray-900 dark:text-white'
		case 'error':
			return 'bg-white dark:bg-[#1a1c23] border-red-200 dark:border-red-800/30 text-gray-900 dark:text-white'
		case 'warning':
			return 'bg-white dark:bg-[#1a1c23] border-amber-200 dark:border-amber-800/30 text-gray-900 dark:text-white'
		default:
			return 'bg-white dark:bg-[#1a1c23] border-blue-200 dark:border-blue-800/30 text-gray-900 dark:text-white'
	}
}

function show({ type = 'info', title = '', message = '', duration = 5000 } = {}) {
	const id = ++nextId
	toasts.value.push({ id, type, title, message })
	if (duration > 0) {
		setTimeout(() => dismiss(id), duration)
	}
	return id
}

function dismiss(id) {
	toasts.value = toasts.value.filter((t) => t.id !== id)
}

function success(message, title = '') { return show({ type: 'success', title, message }) }
function error(message, title = '') { return show({ type: 'error', title, message, duration: 8000 }) }
function warning(message, title = '') { return show({ type: 'warning', title, message }) }
function info(message, title = '') { return show({ type: 'info', title, message }) }

defineExpose({ show, dismiss, success, error, warning, info })
</script>
