<template>
	<BaseModal :show="true" max-width="max-w-lg" scrollable @close="$emit('close')">
		<template #header>
			<div class="flex items-center gap-3">
				<div class="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
					<svg
						class="w-6 h-6 text-blue-600"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"
						/>
					</svg>
				</div>
				<div>
					<h3 class="text-lg font-bold text-gray-900 dark:text-white">Push to Stores</h3>
					<p class="text-xs text-gray-500">{{ itemCode }}</p>
				</div>
			</div>
		</template>

		<div class="p-6 pt-0">
			<div
				v-for="store in stores"
				:key="store.code"
				class="flex items-center justify-between py-3 border-b border-gray-100 dark:border-warm-border/30 last:border-0"
			>
				<div>
					<div class="text-sm font-medium text-gray-900 dark:text-white">
						{{ store.code }}
					</div>
					<div class="text-xs text-gray-500">{{ store.city }}</div>
				</div>
				<div class="flex items-center gap-3">
					<button
						@click="
							allocation[store.code] = Math.max(0, (allocation[store.code] || 0) - 1);
						"
						class="w-8 h-8 rounded-lg bg-gray-100 dark:bg-warm-dark-700 text-sm font-bold hover:bg-gray-200 transition"
					>
						−
					</button>
					<span class="w-8 text-center text-sm font-bold">{{
						allocation[store.code] || 0
					}}</span>
					<button
						@click="allocation[store.code] = (allocation[store.code] || 0) + 1"
						class="w-8 h-8 rounded-lg bg-gray-100 dark:bg-warm-dark-700 text-sm font-bold hover:bg-gray-200 transition"
					>
						+
					</button>
				</div>
			</div>
			<div class="mt-4 text-sm text-gray-500">Total: {{ totalQty }} piece(s)</div>
		</div>

		<template #footer>
			<button
				@click="$emit('close')"
				class="flex-1 py-2 border rounded-lg text-sm font-medium hover:bg-gray-50"
			>
				Cancel
			</button>
			<button
				@click="push"
				:disabled="submitting || totalQty === 0"
				class="flex-1 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
			>
				{{ submitting ? 'Pushing...' : `Push ${totalQty} Pieces` }}
			</button>
		</template>
	</BaseModal>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { call, toast } from 'frappe-ui'
import BaseModal from './BaseModal.vue'

const props = defineProps({
	itemCode: { type: String, required: true },
})

const emit = defineEmits(['close', 'pushed'])

const submitting = ref(false)
const stores = [
	{ code: 'NY-01', city: 'New York' },
	{ code: 'Miami-01', city: 'Miami' },
	{ code: 'LA-01', city: 'Los Angeles' },
	{ code: 'Houston-01', city: 'Houston' },
	{ code: 'Chicago-01', city: 'Chicago' },
]
const allocation = reactive({
	'NY-01': 0,
	'Miami-01': 0,
	'LA-01': 0,
	'Houston-01': 0,
	'Chicago-01': 0,
})

const totalQty = computed(() => Object.values(allocation).reduce((s, q) => s + q, 0))

async function push() {
	submitting.value = true
	try {
		const alloc = Object.entries(allocation)
			.filter(([, q]) => q > 0)
			.map(([store_code, qty]) => ({ store_code, qty }))
		await call('zevar_core.api.inventory.bulk_push_to_stores', {
			item_code: props.itemCode,
			allocation: alloc,
		})
		toast({
			title: 'Pushed',
			message: `${totalQty.value} pieces pushed to stores`,
			icon: 'check',
			intent: 'success',
		})
		emit('pushed')
	} catch (e) {
		toast({
			title: 'Error',
			message: e.messages?.[0] || e.message,
			icon: 'alert-triangle',
			intent: 'error',
		})
	} finally {
		submitting.value = false
	}
}
</script>
