<template>
	<!--
		ChartWrapper — the single chart surface for the Reports suite.
		Renders the shared ECharts wrapper (`components/charts/EChart.vue`) from an
		`:option` prop, wrapped in a loading/error/empty tri-state with an
		error-capture boundary so one bad option never blanks the page.
	-->
	<div class="w-full h-full">
		<SkeletonState v-if="loading" />
		<ErrorState v-else-if="displayError" :message="displayError" @retry="$emit('retry')" />
		<EmptyState v-else-if="empty" />
		<EChart v-else :option="option" :height="height" />
	</div>
</template>

<script setup>
import { onErrorCaptured, ref, computed } from 'vue'
import EChart from '@/components/charts/EChart.vue'
import SkeletonState from './SkeletonState.vue'
import ErrorState from './ErrorState.vue'
import EmptyState from './EmptyState.vue'

const props = defineProps({
	option: { type: Object, default: () => ({}) },
	loading: { type: Boolean, default: false },
	error: { type: String, default: null },
	empty: { type: Boolean, default: false },
	height: { type: String, default: '100%' },
})

defineEmits(['retry'])

const internalError = ref(null)
const displayError = computed(() => props.error || internalError.value)

// A malformed ECharts option throws synchronously on render — catch it here so
// the surrounding card survives and shows a retry affordance.
onErrorCaptured((err) => {
	internalError.value = (err && err.message) || String(err)
	return false
})
</script>
