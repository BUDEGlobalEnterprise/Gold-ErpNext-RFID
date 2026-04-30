<template>
	<BaseModal :show="true" max-width="max-w-3xl" scrollable @close="$emit('close')">
		<template #header>
			<div class="flex items-center gap-3">
				<div class="p-2 bg-indigo-100 dark:bg-indigo-900/30 rounded-lg">
					<svg
						class="w-6 h-6 text-indigo-600"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
						/>
					</svg>
				</div>
				<div>
					<h3 class="text-lg font-bold text-gray-900 dark:text-white">
						Piece Lifecycle
					</h3>
					<p class="text-xs text-gray-500">{{ serialNo }}</p>
				</div>
			</div>
		</template>

		<div class="p-6 pt-0">
			<div v-if="loading" class="text-center py-8 text-gray-400">Loading...</div>

			<div v-else-if="lifecycle">
				<div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
					<div class="premium-card !p-3 text-center">
						<div class="text-[10px] font-bold text-gray-500 uppercase">Item</div>
						<div class="text-xs font-bold text-gray-900 dark:text-white mt-1 truncate">
							{{ lifecycle.item_name }}
						</div>
					</div>
					<div class="premium-card !p-3 text-center">
						<div class="text-[10px] font-bold text-gray-500 uppercase">Location</div>
						<div class="text-xs font-bold text-gray-900 dark:text-white mt-1 truncate">
							{{ lifecycle.warehouse || 'N/A' }}
						</div>
					</div>
					<div class="premium-card !p-3 text-center">
						<div class="text-[10px] font-bold text-gray-500 uppercase">Status</div>
						<div
							class="text-xs font-bold mt-1"
							:class="
								lifecycle.status === 'Active' ? 'text-green-600' : 'text-gray-500'
							"
						>
							{{ lifecycle.status }}
						</div>
					</div>
					<div class="premium-card !p-3 text-center">
						<div class="text-[10px] font-bold text-gray-500 uppercase">Last Seen</div>
						<div class="text-xs font-bold text-gray-900 dark:text-white mt-1">
							{{ formatDt(lifecycle.last_seen_at) }}
						</div>
					</div>
				</div>

				<div
					v-if="lifecycle.reserved_for"
					class="mb-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg p-3 border border-amber-100"
				>
					<span class="text-xs font-bold text-amber-700">Reserved for:</span>
					<span class="text-xs text-amber-600 ml-1"
						>{{ lifecycle.reserved_for }} until
						{{ formatDt(lifecycle.reserved_until) }}</span
					>
				</div>

				<h4 class="text-sm font-bold text-gray-700 dark:text-gray-300 mb-3">Timeline</h4>
				<div class="space-y-0">
					<div v-for="(evt, i) in lifecycle.events" :key="i" class="flex gap-3 pb-4">
						<div class="flex flex-col items-center">
							<div class="w-3 h-3 rounded-full" :class="eventDotClass(evt.type)" />
							<div
								v-if="i < lifecycle.events.length - 1"
								class="w-0.5 flex-1 bg-gray-200 dark:bg-warm-border/50"
							/>
						</div>
						<div class="flex-1 min-w-0">
							<div class="flex items-center justify-between">
								<span class="text-sm font-medium text-gray-900 dark:text-white">{{
									evt.type
								}}</span>
								<span class="text-[10px] text-gray-400">{{ evt.date }}</span>
							</div>
							<div class="text-xs text-gray-500">
								{{ evt.warehouse }} &middot; Qty: {{ evt.qty_change > 0 ? '+' : ''
								}}{{ evt.qty_change }}
							</div>
							<a
								v-if="evt.voucher_no"
								class="text-[10px] text-blue-500 hover:underline cursor-pointer"
								>{{ evt.voucher_type }}: {{ evt.voucher_no }}</a
							>
						</div>
					</div>
				</div>
			</div>
		</div>
	</BaseModal>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { call } from 'frappe-ui'
import BaseModal from './BaseModal.vue'

const props = defineProps({
	serialNo: { type: String, required: true },
})

defineEmits(['close'])

const lifecycle = ref(null)
const loading = ref(true)

function eventDotClass(type) {
	if (type.includes('Sale')) return 'bg-red-500'
	if (type.includes('Received') || type.includes('Receipt')) return 'bg-green-500'
	if (type.includes('Transfer')) return 'bg-blue-500'
	if (type.includes('Damage') || type.includes('Issue')) return 'bg-orange-500'
	return 'bg-gray-400'
}

function formatDt(val) {
	if (!val) return 'N/A'
	return val.toString().slice(0, 19).replace('T', ' ')
}

onMounted(async () => {
	try {
		lifecycle.value = await call('zevar_core.api.inventory.get_piece_lifecycle', {
			serial_no: props.serialNo,
		})
	} catch {
		lifecycle.value = null
	} finally {
		loading.value = false
	}
})
</script>
