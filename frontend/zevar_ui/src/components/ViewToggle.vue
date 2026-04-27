<template>
	<div class="flex items-center gap-1 bg-gray-100 dark:bg-[#1C1F26] p-1 rounded-lg">
		<button
			@click="setView('grid')"
			class="p-2 rounded-md transition-all"
			:class="
				modelValue === 'grid'
					? 'bg-white dark:bg-[#2a2d37] shadow-sm text-[#D4AF37]'
					: 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300'
			"
			title="Grid View"
		>
			<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"
				/>
			</svg>
		</button>
		<button
			@click="setView('list')"
			class="p-2 rounded-md transition-all"
			:class="
				modelValue === 'list'
					? 'bg-white dark:bg-[#2a2d37] shadow-sm text-[#D4AF37]'
					: 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300'
			"
			title="List View"
		>
			<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M4 6h16M4 12h16M4 18h16"
				/>
			</svg>
		</button>
	</div>
</template>

<script setup>
const props = defineProps({
	modelValue: { type: String, default: 'grid' },
	storageKey: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue'])

function setView(mode) {
	emit('update:modelValue', mode)
	if (props.storageKey) {
		localStorage.setItem(props.storageKey, mode)
	}
}
</script>
