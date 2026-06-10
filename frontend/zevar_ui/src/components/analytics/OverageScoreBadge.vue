<template>
	<span class="score-badge" :class="tone">{{ score }}</span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
	score: { type: Number, default: 0 },
})

const tone = computed(() => {
	if (props.score >= 85) return 'score-badge--critical'
	if (props.score >= 75) return 'score-badge--high'
	if (props.score >= 65) return 'score-badge--medium'
	return 'score-badge--watch'
})
</script>

<style scoped>
.score-badge {
	min-width: 34px;
	height: 24px;
	border-radius: 6px;
	display: inline-flex;
	align-items: center;
	justify-content: center;
	padding: 0 8px;
	font: 800 11px/1 var(--font-mono, monospace);
}
.score-badge--watch {
	background: rgba(59, 130, 246, 0.14);
	color: #3b82f6;
}
.score-badge--medium {
	background: rgba(245, 158, 11, 0.16);
	color: #d97706;
}
.score-badge--high {
	background: rgba(249, 115, 22, 0.16);
	color: #ea580c;
}
.score-badge--critical {
	background: rgba(239, 68, 68, 0.16);
	color: #dc2626;
}
</style>
