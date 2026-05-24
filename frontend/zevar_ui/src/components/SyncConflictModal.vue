<template>
	<div v-if="visible" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/50" @click.self="close">
		<div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
			<!-- Header -->
			<div class="px-6 py-4 border-b border-red-200 dark:border-red-800/30 bg-red-50 dark:bg-red-900/20 rounded-t-xl">
				<div class="flex items-center gap-3">
					<div class="w-10 h-10 rounded-full bg-red-100 dark:bg-red-900/40 flex items-center justify-center">
						<svg class="w-5 h-5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
						</svg>
					</div>
					<div>
						<h3 class="text-lg font-semibold text-red-800 dark:text-red-300">Sync Conflict Detected</h3>
						<p class="text-sm text-red-600 dark:text-red-400">Order queued at {{ formattedTime }}</p>
					</div>
				</div>
			</div>

			<!-- Body -->
			<div class="px-6 py-4 space-y-4">
				<!-- Error message -->
				<div class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3">
					<p class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Problem:</p>
					<p class="text-sm text-gray-600 dark:text-gray-400">{{ conflict.server_error || 'Unknown conflict' }}</p>
				</div>

				<!-- Affected items -->
				<div v-if="conflictItems.length > 0" class="space-y-2">
					<p class="text-sm font-medium text-gray-700 dark:text-gray-300">Affected items:</p>
					<div v-for="item in conflictItems" :key="item.item_code" class="flex items-center gap-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3">
						<img v-if="item.image" :src="item.image" class="w-10 h-10 rounded object-cover" />
						<div class="flex-1 min-w-0">
							<p class="text-sm font-medium text-gray-800 dark:text-gray-200 truncate">{{ item.item_name || item.item_code }}</p>
							<p class="text-xs text-gray-500 dark:text-gray-400">
								{{ item.item_code }}
								<span v-if="item.serial_no"> &middot; {{ item.serial_no }}</span>
								&middot; {{ item.qty }}x ${{ item.rate }}
							</p>
						</div>
					</div>
				</div>

				<!-- Resolution options -->
				<div class="space-y-2">
					<p class="text-sm font-medium text-gray-700 dark:text-gray-300">What would you like to do?</p>
					<label
						v-for="option in resolutionOptions"
						:key="option.value"
						class="flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-colors"
						:class="selectedResolution === option.value
							? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 dark:border-blue-600'
							: 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'"
					>
						<input
							type="radio"
							:value="option.value"
							v-model="selectedResolution"
							class="mt-0.5"
						/>
						<div>
							<p class="text-sm font-medium text-gray-800 dark:text-gray-200">{{ option.label }}</p>
							<p class="text-xs text-gray-500 dark:text-gray-400">{{ option.description }}</p>
						</div>
					</label>
				</div>
			</div>

			<!-- Footer -->
			<div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-3">
				<button
					@click="close"
					class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition"
				>
					Close
				</button>
				<button
					@click="resolve"
					:disabled="!selectedResolution || resolving"
					class="px-4 py-2 text-sm font-medium text-white rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
					:class="selectedResolution === 'resolved_cancel'
						? 'bg-red-600 hover:bg-red-700'
						: 'bg-blue-600 hover:bg-blue-700'"
				>
					{{ resolving ? 'Resolving...' : 'Resolve' }}
				</button>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
	visible: Boolean,
	conflict: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['resolve', 'close'])

const selectedResolution = ref('resolved_cancel')
const resolving = ref(false)

const formattedTime = computed(() => {
	if (!props.conflict.created_at) return 'unknown time'
	const d = new Date(props.conflict.created_at)
	return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
})

const conflictItems = computed(() => {
	try {
		const payload = props.conflict.payload || {}
		const items = typeof payload.items === 'string' ? JSON.parse(payload.items) : (payload.items || [])
		return items
	} catch {
		return []
	}
})

const resolutionOptions = computed(() => {
	const options = [
		{ value: 'resolved_cancel', label: 'Cancel entire order', description: 'Remove this offline order completely. No charges will be processed.' },
	]

	if (conflictItems.value.length > 1) {
		options.push({
			value: 'resolved_remove_item',
			label: 'Remove unavailable item, process rest',
			description: 'Remove the conflicting item from the invoice and sync the remaining items.',
		})
	}

	options.push(
		{ value: 'resolved_substitute', label: 'Substitute with similar item', description: 'Replace the unavailable item with another piece from inventory.' },
		{ value: 'escalated', label: 'Escalate to manager', description: 'Flag for manager review. The order stays in conflict queue.' },
	)

	return options
})

async function resolve() {
	if (!selectedResolution.value || resolving.value) return
	resolving.value = true
	try {
		emit('resolve', {
			orderId: props.conflict.id,
			resolution: selectedResolution.value,
			conflictType: props.conflict.conflict_type,
		})
	} finally {
		resolving.value = false
	}
}

function close() {
	emit('close')
}
</script>
