<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<h2 class="premium-title !text-xl sm:!text-2xl">Metal & Purity Reference</h2>
				<div class="flex items-center gap-2">
					<button
						@click="showAddMetal = true"
						class="px-3 py-1.5 bg-primary-600 text-white rounded-lg text-xs font-semibold hover:bg-primary-700 transition-colors"
					>
						+ Add Metal
					</button>
					<button
						@click="showAddPurity = true"
						class="px-3 py-1.5 border border-primary-600 text-primary-600 rounded-lg text-xs font-semibold hover:bg-primary-50 transition-colors"
					>
						+ Add Purity
					</button>
				</div>
			</div>

			<!-- Metals Table -->
			<div class="mb-6">
				<h3
					class="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3"
				>
					Metals
				</h3>
				<div
					class="bg-white dark:bg-warm-dark-800 border border-gray-200 dark:border-warm-border rounded-xl overflow-hidden"
				>
					<table class="w-full text-sm">
						<thead>
							<tr class="bg-gray-50 dark:bg-warm-dark-900">
								<th
									class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
								>
									Code
								</th>
								<th
									class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
								>
									Name
								</th>
								<th
									class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
								>
									Type
								</th>
								<th
									class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
								>
									Default Purity
								</th>
								<th
									class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
								>
									Color
								</th>
								<th
									class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase"
								>
									Active
								</th>
							</tr>
						</thead>
						<tbody>
							<tr
								v-for="m in metals"
								:key="m.name"
								class="border-t border-gray-100 dark:border-warm-border hover:bg-gray-50 dark:hover:bg-warm-dark-700 cursor-pointer"
								@click="editMetal(m)"
							>
								<td class="px-4 py-3 font-mono font-semibold">
									{{ m.metal_code }}
								</td>
								<td class="px-4 py-3">{{ m.metal_name }}</td>
								<td class="px-4 py-3">
									<span
										class="px-2 py-0.5 bg-blue-50 text-blue-700 rounded text-xs"
										>{{ m.metal_type }}</span
									>
								</td>
								<td class="px-4 py-3 text-gray-500">
									{{ m.default_purity || '—' }}
								</td>
								<td class="px-4 py-3">
									<span class="inline-flex items-center gap-1.5">
										<span
											class="w-4 h-4 rounded-full border"
											:style="{ background: m.color_hex || '#ccc' }"
										></span>
										<span class="text-xs text-gray-400">{{
											m.color_hex
										}}</span>
									</span>
								</td>
								<td class="px-4 py-3 text-center">
									<span
										:class="m.is_active ? 'text-green-600' : 'text-red-400'"
										>{{ m.is_active ? '✓' : '✗' }}</span
									>
								</td>
							</tr>
							<tr v-if="!metals.length">
								<td colspan="6" class="px-4 py-8 text-center text-gray-400">
									No metals configured
								</td>
							</tr>
						</tbody>
					</table>
				</div>
			</div>

			<!-- Purities Table -->
			<div>
				<h3
					class="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3"
				>
					Purities
				</h3>
				<div class="flex gap-2 mb-3">
					<button
						v-for="mt in metalFilters"
						:key="mt"
						@click="purityFilter = mt"
						:class="[
							'px-3 py-1 rounded-lg text-xs font-medium transition-colors',
							purityFilter === mt
								? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300'
								: 'bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-warm-dark-700 dark:text-gray-300',
						]"
					>
						{{ mt || 'All' }}
					</button>
				</div>
				<div
					class="bg-white dark:bg-warm-dark-800 border border-gray-200 dark:border-warm-border rounded-xl overflow-hidden"
				>
					<table class="w-full text-sm">
						<thead>
							<tr class="bg-gray-50 dark:bg-warm-dark-900">
								<th
									class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
								>
									Code
								</th>
								<th
									class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
								>
									Name
								</th>
								<th
									class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
								>
									Metal
								</th>
								<th
									class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
								>
									Fine Content
								</th>
								<th
									class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
								>
									Millesimal
								</th>
								<th
									class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase"
								>
									Active
								</th>
							</tr>
						</thead>
						<tbody>
							<tr
								v-for="p in filteredPurities"
								:key="p.name"
								class="border-t border-gray-100 dark:border-warm-border hover:bg-gray-50 dark:hover:bg-warm-dark-700 cursor-pointer"
								@click="editPurity(p)"
							>
								<td class="px-4 py-3 font-mono font-semibold">
									{{ p.purity_code }}
								</td>
								<td class="px-4 py-3">{{ p.purity_name }}</td>
								<td class="px-4 py-3">{{ p.metal }}</td>
								<td class="px-4 py-3">
									{{ (p.fine_metal_content * 100).toFixed(1) }}%
								</td>
								<td class="px-4 py-3">{{ p.is_millesimal ? 'Yes' : 'No' }}</td>
								<td class="px-4 py-3 text-center">
									<span
										:class="p.is_active ? 'text-green-600' : 'text-red-400'"
										>{{ p.is_active ? '✓' : '✗' }}</span
									>
								</td>
							</tr>
							<tr v-if="!filteredPurities.length">
								<td colspan="6" class="px-4 py-8 text-center text-gray-400">
									No purities found
								</td>
							</tr>
						</tbody>
					</table>
				</div>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { useInventoryV2Store } from '../../stores/inventoryV2'

const store = useInventoryV2Store()
const showAddMetal = ref(false)
const showAddPurity = ref(false)
const purityFilter = ref('')

const metals = computed(() => store.metals || [])
const purities = computed(() => store.purities || [])

const metalFilters = computed(() => ['', ...new Set(purities.value.map((p) => p.metal))])
const filteredPurities = computed(() =>
	purityFilter.value
		? purities.value.filter((p) => p.metal === purityFilter.value)
		: purities.value
)

function editMetal(m) {
	/* TODO: open edit modal */
}
function editPurity(p) {
	/* TODO: open edit modal */
}

onMounted(() => {
	store.fetchMetals()
	store.fetchPurities()
})
</script>
