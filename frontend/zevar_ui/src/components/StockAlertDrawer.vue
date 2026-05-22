<template>
	<Teleport to="body">
		<Transition name="slide">
			<div v-if="items.length > 0" class="fixed inset-0 z-[90] flex justify-end">
				<div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="$emit('close')"></div>
				<div
					class="relative w-full max-w-lg bg-white dark:bg-warm-card shadow-2xl overflow-y-auto flex flex-col h-full"
				>
					<div
						class="sticky top-0 bg-white dark:bg-warm-card border-b border-gray-100 dark:border-warm-border/50 p-4 flex items-center justify-between z-10"
					>
						<div>
							<h3 class="text-lg font-bold text-gray-900 dark:text-white">{{ title }}</h3>
							<p class="text-xs text-gray-500">
								{{ subtitle }} - {{ items.length }} {{ items.length === 1 ? 'item' : 'items' }}
							</p>
						</div>
						<button
							@click="$emit('close')"
							class="p-2 hover:bg-gray-100 dark:hover:bg-warm-dark-700 rounded-full"
						>
							<svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M6 18L18 6M6 6l12 12"
								/>
							</svg>
						</button>
					</div>

					<div class="flex-1 p-4 overflow-y-auto space-y-2">
						<div v-if="quickAction" class="mb-4 flex gap-2">
							<button
								@click="$emit('quick-action', quickAction.key, items)"
								class="flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-lg text-xs font-bold transition"
								:class="quickAction.btnClass"
							>
								<svg
									v-if="quickAction.icon === 'cart'"
									class="w-4 h-4"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 100 4 2 2 0 000-4z"
									/>
								</svg>
								<svg
									v-else-if="quickAction.icon === 'adjust'"
									class="w-4 h-4"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
									/>
								</svg>
								<svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M12 6v6m0 0v6m0-6h6m-6 0H6"
									/>
								</svg>
								{{ quickAction.label }}
							</button>
						</div>

						<div
							v-for="item in items"
							:key="item.code"
							class="flex items-center justify-between p-3 bg-gray-50 dark:bg-warm-dark-900 rounded-lg hover:bg-gray-100 dark:hover:bg-warm-dark-800 cursor-pointer transition"
							@click="$emit('item-click', item)"
						>
							<div class="min-w-0 flex-1 pr-3">
								<div class="text-xs font-bold text-gray-900 dark:text-white truncate">{{ item.name }}</div>
								<div class="text-[10px] text-gray-500 font-mono">{{ item.code }}</div>
								<div class="flex flex-wrap gap-1 mt-1">
									<span
										v-if="item.metal && item.metal !== '-'"
										class="text-[9px] font-bold px-1.5 py-0.5 rounded bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400"
									>
										{{ item.metal }}
									</span>
									<span
										v-if="item.category"
										class="text-[9px] font-bold px-1.5 py-0.5 rounded bg-gray-100 dark:bg-warm-dark-700 text-gray-600 dark:text-gray-400"
									>
										{{ item.category }}
									</span>
								</div>
							</div>
							<div class="text-right ml-3 shrink-0">
								<div class="text-sm font-bold" :class="item.stock <= 0 ? 'text-red-500' : 'text-amber-500'">
									{{ item.stock }} pcs
								</div>
								<div class="text-[10px] font-bold text-[#D4AF37]">{{ fmtCur(itemValue(item)) }}</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</Transition>
	</Teleport>
</template>

<script setup>
defineProps({
	title: { type: String, required: true },
	subtitle: { type: String, required: true },
	items: { type: Array, required: true },
	quickAction: { type: Object, default: null },
})

defineEmits(['close', 'item-click', 'quick-action'])

function itemValue(item) {
	return (item.price || 0) * Math.max(item.stock || 0, 0)
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
