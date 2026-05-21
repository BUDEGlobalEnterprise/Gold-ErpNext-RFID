<template>
	<Teleport to="body">
		<Transition name="slide">
			<div v-if="show" class="fixed inset-0 z-[80] flex justify-end">
				<div
					class="absolute inset-0 bg-black/40 backdrop-blur-sm"
					@click="$emit('close')"
				></div>
				<div
					class="relative w-full max-w-md bg-white dark:bg-warm-card shadow-2xl overflow-y-auto flex flex-col h-full"
				>
					<!-- Header -->
					<div
						class="sticky top-0 bg-white dark:bg-warm-card border-b border-gray-100 dark:border-warm-border/50 p-4 flex items-center justify-between z-10"
					>
						<div>
							<h3
								class="text-base font-bold text-gray-900 dark:text-white flex items-center gap-2"
							>
								<span
									class="w-2.5 h-2.5 rounded-full"
									:class="
										type === 'out'
											? 'bg-red-500 animate-pulse'
											: 'bg-amber-500'
									"
								></span>
								{{ type === 'out' ? 'Out of Stock Alert' : 'Low Stock Alert' }}
							</h3>
							<p class="text-[10px] text-gray-500 font-medium mt-0.5">
								{{ items.length }}
								{{ items.length === 1 ? 'item' : 'items' }} require attention
							</p>
						</div>
						<button
							@click="$emit('close')"
							class="p-2 hover:bg-gray-100 dark:hover:bg-warm-dark-700 rounded-full"
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

					<!-- Content -->
					<div class="flex-1 p-4 overflow-y-auto space-y-3">
						<div
							v-for="item in items"
							:key="item.code"
							@click="$emit('select-item', item)"
							class="p-3 bg-gray-50 dark:bg-warm-dark-900 rounded-xl border border-transparent hover:border-gray-200 dark:hover:border-warm-border/50 hover:bg-gray-100/50 dark:hover:bg-warm-dark-800/50 cursor-pointer transition-all duration-200 flex items-center justify-between group"
						>
							<div class="min-w-0 flex-1 pr-3">
								<div
									class="font-bold text-xs text-gray-900 dark:text-white truncate group-hover:text-[#D4AF37] transition-colors"
								>
									{{ item.name }}
								</div>
								<div class="text-[10px] text-gray-500 font-mono mt-0.5">
									{{ item.code }}
								</div>
								<div class="flex items-center gap-1.5 mt-2">
									<span
										v-if="item.metal"
										class="text-[8px] font-bold px-1.5 py-0.5 rounded bg-yellow-100/60 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400 border border-yellow-200/20"
										>{{ item.metal }}</span
									>
									<span
										v-if="item.purity"
										class="text-[8px] font-semibold px-1.5 py-0.5 rounded bg-gray-100/80 dark:bg-warm-dark-800 text-gray-600 dark:text-gray-400 border border-gray-200/20"
										>{{ item.purity }}</span
									>
								</div>
							</div>
							<div class="flex flex-col items-end gap-1.5 shrink-0">
								<span
									class="text-[10px] font-bold px-2 py-0.5 rounded-full"
									:class="
										item.stock <= 0
											? 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400'
											: 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400'
									"
								>
									{{ item.stock }} pcs
								</span>
								<span
									class="text-xs font-mono font-bold text-gray-900 dark:text-white"
								>
									{{ fmtCur(item.price) }}
								</span>
							</div>
						</div>
					</div>

					<!-- Global Action Button at the bottom -->
					<div
						class="p-4 border-t border-gray-100 dark:border-warm-border/50 sticky bottom-0 bg-white dark:bg-warm-card z-10"
					>
						<button
							@click="triggerGlobalAction"
							class="w-full flex items-center justify-center gap-2 py-3 text-xs font-bold text-white rounded-xl shadow-md transition-all duration-200"
							:class="
								type === 'out'
									? 'bg-red-600 hover:bg-red-700 shadow-red-500/10'
									: 'bg-amber-600 hover:bg-amber-700 shadow-amber-500/10'
							"
						>
							<svg
								class="w-4 h-4"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z"
								/>
							</svg>
							{{
								type === 'out'
									? 'Create Adjustment Entry for All'
									: 'Initiate Reorder for All'
							}}
						</button>
					</div>
				</div>
			</div>
		</Transition>
	</Teleport>
</template>

<script setup>
defineProps({
	show: { type: Boolean, default: false },
	type: { type: String, default: 'low' }, // 'low' or 'out'
	items: { type: Array, default: () => [] },
})

const emit = defineEmits(['close', 'select-item', 'action-all'])

function triggerGlobalAction() {
	emit('action-all')
}

function fmtCur(val) {
	if (!val) return '$0'
	return new Intl.NumberFormat('en-US', {
		style: 'currency',
		currency: 'USD',
		maximumFractionDigits: 0,
	}).format(val)
}
</script>

<style scoped>
.slide-enter-active,
.slide-leave-active {
	transition: transform 0.25s ease, opacity 0.2s ease;
}
.slide-enter-from,
.slide-leave-to {
	transform: translateX(100%);
	opacity: 0;
}
</style>
