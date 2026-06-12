<template>
	<div class="flex flex-col gap-6">
		<div class="flex items-center justify-between">
			<div>
				<h3 class="premium-title !text-lg">Audit Discrepancies</h3>
				<p class="premium-subtitle">Review and resolve missing or unexpected items.</p>
			</div>
			<div class="flex gap-2">
				<div
					class="flex items-center gap-1.5 px-3 py-1 bg-red-500/10 text-red-500 border border-red-500/20 rounded-full text-[10px] font-bold"
				>
					{{ pendingCount }} Pending
				</div>
				<div
					class="flex items-center gap-1.5 px-3 py-1 bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 rounded-full text-[10px] font-bold"
				>
					{{ resolvedCount }} Resolved
				</div>
			</div>
		</div>

		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
			<!-- Pending Missing -->
			<div class="flex flex-col gap-4">
				<div class="flex items-center gap-2 px-1">
					<div class="w-1.5 h-1.5 rounded-full bg-red-500"></div>
					<h4 class="text-[10px] font-black uppercase tracking-widest text-gray-500">
						Missing Items
					</h4>
				</div>
				<div class="space-y-3">
					<div
						v-for="d in missingItems"
						:key="d.name"
						class="premium-card !p-3 group hover:border-[#D4AF37]/30 transition-all cursor-pointer"
						@click="selectedDiscrepancy = d"
					>
						<div class="flex gap-3">
							<div
								class="w-12 h-12 rounded-lg bg-gray-100 dark:bg-white/5 overflow-hidden shrink-0"
							>
								<img
									v-if="d.image"
									:src="d.image"
									class="w-full h-full object-cover"
								/>
								<div
									v-else
									class="w-full h-full flex items-center justify-center text-gray-300 dark:text-gray-600 text-[10px]"
								>
									IMG
								</div>
							</div>
							<div class="min-w-0 flex-1">
								<div
									class="font-bold text-xs text-gray-900 dark:text-white truncate"
								>
									{{ d.item_name }}
								</div>
								<div class="text-[9px] text-gray-500">{{ d.item_code }}</div>
								<div class="mt-2 flex items-center justify-between">
									<div class="text-[10px] font-bold text-red-500">
										-{{ Math.abs(d.discrepancy_qty) }} pc
									</div>
									<button
										class="text-[9px] font-black uppercase text-[#D4AF37] opacity-0 group-hover:opacity-100 transition-opacity"
									>
										Resolve
									</button>
								</div>
							</div>
						</div>
					</div>
					<div
						v-if="missingItems.length === 0"
						class="py-10 text-center border border-dashed border-gray-200 dark:border-white/10 rounded-xl"
					>
						<p class="text-xs text-gray-400">No missing items.</p>
					</div>
				</div>
			</div>

			<!-- Unexpected Location -->
			<div class="flex flex-col gap-4">
				<div class="flex items-center gap-2 px-1">
					<div class="w-1.5 h-1.5 rounded-full bg-amber-500"></div>
					<h4 class="text-[10px] font-black uppercase tracking-widest text-gray-500">
						Unexpected Items
					</h4>
				</div>
				<div class="space-y-3">
					<div
						v-for="d in unexpectedItems"
						:key="d.name"
						class="premium-card !p-3 group hover:border-[#D4AF37]/30 transition-all cursor-pointer"
						@click="selectedDiscrepancy = d"
					>
						<div class="flex gap-3">
							<div
								class="w-12 h-12 rounded-lg bg-gray-100 dark:bg-white/5 overflow-hidden shrink-0"
							>
								<img
									v-if="d.image"
									:src="d.image"
									class="w-full h-full object-cover"
								/>
								<div
									v-else
									class="w-full h-full flex items-center justify-center text-gray-300 dark:text-gray-600 text-[10px]"
								>
									IMG
								</div>
							</div>
							<div class="min-w-0 flex-1">
								<div
									class="font-bold text-xs text-gray-900 dark:text-white truncate"
								>
									{{ d.item_name }}
								</div>
								<div class="text-[9px] text-gray-500">{{ d.item_code }}</div>
								<div class="mt-2 flex items-center justify-between">
									<div class="text-[10px] font-bold text-amber-500">
										+{{ d.found_qty }} pc
									</div>
									<button
										class="text-[9px] font-black uppercase text-[#D4AF37] opacity-0 group-hover:opacity-100 transition-opacity"
									>
										Relocate
									</button>
								</div>
							</div>
						</div>
					</div>
					<div
						v-if="unexpectedItems.length === 0"
						class="py-10 text-center border border-dashed border-gray-200 dark:border-white/10 rounded-xl"
					>
						<p class="text-xs text-gray-400">No unexpected items.</p>
					</div>
				</div>
			</div>

			<!-- Resolved -->
			<div class="flex flex-col gap-4 opacity-70">
				<div class="flex items-center gap-2 px-1">
					<div class="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
					<h4 class="text-[10px] font-black uppercase tracking-widest text-gray-500">
						Recently Resolved
					</h4>
				</div>
				<div class="space-y-3">
					<div
						v-for="d in resolvedItems"
						:key="d.name"
						class="premium-card !p-3 bg-emerald-500/5 border-emerald-500/10"
					>
						<div class="flex gap-3">
							<div
								class="w-12 h-12 rounded-lg bg-gray-100 dark:bg-white/5 overflow-hidden shrink-0 opacity-50"
							>
								<img
									v-if="d.image"
									:src="d.image"
									class="w-full h-full object-cover"
								/>
							</div>
							<div class="min-w-0 flex-1">
								<div class="font-bold text-xs text-gray-400 truncate">
									{{ d.item_name }}
								</div>
								<div class="text-[9px] text-emerald-600 font-bold uppercase">
									{{ d.resolution_action }}
								</div>
								<div class="mt-1 text-[9px] text-gray-500 truncate">
									{{ d.notes || 'No notes' }}
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- Resolution Modal -->
		<BaseModal
			v-if="selectedDiscrepancy"
			:show="!!selectedDiscrepancy"
			@close="selectedDiscrepancy = null"
		>
			<template #title>Resolve Discrepancy</template>
			<template #body>
				<div class="p-4 flex flex-col gap-4">
					<div
						class="flex items-center gap-4 p-3 bg-gray-50 dark:bg-white/5 rounded-xl border border-gray-100 dark:border-white/5"
					>
						<img
							v-if="selectedDiscrepancy.image"
							:src="selectedDiscrepancy.image"
							class="w-16 h-16 rounded-lg object-cover"
						/>
						<div>
							<div class="font-bold text-sm text-gray-900 dark:text-white">
								{{ selectedDiscrepancy.item_name }}
							</div>
							<div class="text-[10px] text-gray-500">
								{{ selectedDiscrepancy.item_code }}
							</div>
							<div class="mt-1 text-[10px]">
								<span
									class="font-bold text-red-500"
									v-if="selectedDiscrepancy.discrepancy_qty < 0"
									>Missing
									{{ Math.abs(selectedDiscrepancy.discrepancy_qty) }} pc</span
								>
								<span class="font-bold text-amber-500" v-else
									>Surplus {{ selectedDiscrepancy.found_qty }} pc</span
								>
							</div>
						</div>
					</div>

					<div class="space-y-2">
						<label
							class="block text-[10px] font-bold text-gray-500 uppercase tracking-widest px-1"
							>Action</label
						>
						<div class="grid grid-cols-2 gap-2">
							<button
								v-for="action in resolutionOptions"
								:key="action.value"
								@click="resolutionAction = action.value"
								:class="
									resolutionAction === action.value
										? 'bg-[#D4AF37] text-white border-[#D4AF37]'
										: 'bg-white dark:bg-white/5 text-gray-600 dark:text-gray-300 border-gray-200 dark:border-white/10 hover:border-gray-300'
								"
								class="px-3 py-3 text-[11px] font-bold rounded-xl border transition-all text-left flex flex-col gap-1"
							>
								<span>{{ action.label }}</span>
								<span class="text-[8px] font-medium opacity-60">{{
									action.desc
								}}</span>
							</button>
						</div>
					</div>

					<div class="space-y-2">
						<label
							class="block text-[10px] font-bold text-gray-500 uppercase tracking-widest px-1"
							>Notes</label
						>
						<textarea
							v-model="resolutionNotes"
							class="w-full bg-gray-50 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-xl p-3 text-xs outline-none focus:ring-1 focus:ring-[#D4AF37] min-h-[80px]"
							placeholder="Add context for this correction..."
						></textarea>
					</div>
				</div>
			</template>
			<template #actions>
				<button
					@click="submitResolution"
					:disabled="!resolutionAction || isSubmitting"
					class="w-full py-3 bg-[#D4AF37] text-[#0F1115] font-black uppercase tracking-widest text-xs rounded-xl hover:bg-yellow-500 transition-all disabled:opacity-50"
				>
					{{ isSubmitting ? 'Processing...' : 'Apply Correction' }}
				</button>
			</template>
		</BaseModal>
	</div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { createResource } from 'frappe-ui'
import { useAuditStore } from '../stores/audit'
import BaseModal from './BaseModal.vue'

const props = defineProps({
	auditSession: {
		type: String,
		required: true,
	},
})

const emit = defineEmits(['resolved'])

const auditStore = useAuditStore()
const selectedDiscrepancy = ref(null)
const resolutionAction = ref('')
const resolutionNotes = ref('')
const isSubmitting = ref(false)

const missingItems = computed(() =>
	auditStore.discrepancies.filter((d) => d.status === 'Pending' && d.discrepancy_qty < 0)
)
const unexpectedItems = computed(() =>
	auditStore.discrepancies.filter((d) => d.status === 'Pending' && d.discrepancy_qty >= 0)
)
const resolvedItems = computed(() =>
	auditStore.discrepancies.filter((d) => d.status === 'Resolved').slice(0, 10)
)

const pendingCount = computed(
	() => auditStore.discrepancies.filter((d) => d.status === 'Pending').length
)
const resolvedCount = computed(
	() => auditStore.discrepancies.filter((d) => d.status === 'Resolved').length
)

const resolutionOptions = computed(() => {
	if (!selectedDiscrepancy.value) return []

	if (selectedDiscrepancy.value.discrepancy_qty < 0) {
		return [
			{ label: 'Stock Entry', value: 'Stock Entry', desc: 'Mark as shrinkage / write-off' },
			{
				label: 'Manual Correction',
				value: 'Manual Correction',
				desc: 'Resolved outside the system',
			},
			{ label: 'Ignore', value: 'Ignored', desc: 'False positive, no action' },
		]
	} else {
		return [
			{
				label: 'Transfer',
				value: 'Warehouse Transfer',
				desc: 'Move to correct physical case',
			},
			{ label: 'Stock Entry', value: 'Stock Entry', desc: 'Add missing stock to system' },
			{ label: 'Ignore', value: 'Ignored', desc: 'False positive, no action' },
		]
	}
})

async function submitResolution() {
	if (!selectedDiscrepancy.value || !resolutionAction.value) return

	isSubmitting.value = true
	try {
		await createResource({
			url: 'zevar_core.api.inventory_audit.resolve_discrepancy',
			params: {
				discrepancy_name: selectedDiscrepancy.value.name,
				action: resolutionAction.value,
				notes: resolutionNotes.value,
			},
		}).submit()

		selectedDiscrepancy.value = null
		resolutionAction.value = ''
		resolutionNotes.value = ''
		auditStore.loadDiscrepancies(props.auditSession)
		emit('resolved')
	} catch (e) {
		console.error(e)
	} finally {
		isSubmitting.value = false
	}
}

onMounted(() => {
	auditStore.loadDiscrepancies(props.auditSession)
})
</script>
