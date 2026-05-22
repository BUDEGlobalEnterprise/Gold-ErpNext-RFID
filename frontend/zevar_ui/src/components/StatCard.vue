<template>
	<div
		class="premium-card !p-4 transition duration-200"
		:class="[clickable ? 'cursor-pointer hover:ring-2 active:scale-[0.98]' : '', clickable ? ringColor : '']"
		:role="clickable ? 'button' : undefined"
		:tabindex="clickable ? 0 : undefined"
		@click="handleClick"
		@keydown.enter.prevent="handleClick"
		@keydown.space.prevent="handleClick"
	>
		<div class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">
			{{ label }}
		</div>
		<div class="text-2xl font-bold" :class="valueColor">{{ value }}</div>
		<div v-if="subtext || clickable" class="text-[10px] font-bold mt-1" :class="subtextColor">
			<span v-if="subtext">{{ subtext }}</span>
			<span v-if="clickable" :class="{ 'ml-1': subtext }" class="underline">View &rarr;</span>
		</div>
	</div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
	label: { type: String, required: true },
	value: { type: [String, Number], required: true },
	subtext: { type: String, default: '' },
	variant: { type: String, default: 'default' },
	clickable: { type: Boolean, default: false },
})

const emit = defineEmits(['click'])

const variantClasses = {
	default: {
		value: 'text-gray-900 dark:text-white',
		subtext: 'text-gray-500 dark:text-gray-400',
		ring: 'hover:ring-gray-300 dark:hover:ring-gray-600',
	},
	gold: {
		value: 'text-[#D4AF37]',
		subtext: 'text-[#D4AF37]/80',
		ring: 'hover:ring-yellow-300 dark:hover:ring-yellow-500/40',
	},
	warning: {
		value: 'text-amber-500',
		subtext: 'text-amber-500',
		ring: 'hover:ring-amber-300 dark:hover:ring-amber-500/40',
	},
	danger: {
		value: 'text-red-500',
		subtext: 'text-red-500',
		ring: 'hover:ring-red-300 dark:hover:ring-red-500/40',
	},
	success: {
		value: 'text-emerald-500',
		subtext: 'text-emerald-500',
		ring: 'hover:ring-emerald-300 dark:hover:ring-emerald-500/40',
	},
	info: {
		value: 'text-blue-500',
		subtext: 'text-blue-500',
		ring: 'hover:ring-blue-300 dark:hover:ring-blue-500/40',
	},
}

const activeVariant = computed(() => variantClasses[props.variant] || variantClasses.default)
const valueColor = computed(() => activeVariant.value.value)
const subtextColor = computed(() => activeVariant.value.subtext)
const ringColor = computed(() => activeVariant.value.ring)

function handleClick() {
	if (!props.clickable) return
	emit('click')
}
</script>
