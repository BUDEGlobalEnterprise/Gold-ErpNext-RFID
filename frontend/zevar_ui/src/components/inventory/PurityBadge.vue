<template>
	<span class="purity-badge" :class="badgeClass" :title="`${purityCode} — ${fineContent}`">
		{{ purityCode }}
	</span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
	purityCode: { type: String, default: '' },
	metalType: { type: String, default: '' },
	fineMetalContent: { type: Number, default: 0 },
})

const fineContent = computed(() =>
	props.fineMetalContent ? `${(props.fineMetalContent * 100).toFixed(1)}% pure` : ''
)

const badgeClass = computed(() => {
	const code = props.purityCode?.toUpperCase() || ''
	if (code.includes('24K')) return 'purity-24k'
	if (code.includes('22K')) return 'purity-22k'
	if (code.includes('18K')) return 'purity-18k'
	if (code.includes('14K')) return 'purity-14k'
	if (code.includes('10K')) return 'purity-10k'
	if (code.includes('925') || code.includes('STERLING')) return 'purity-925'
	if (code.includes('950') || code.includes('PLAT')) return 'purity-plat'
	return 'purity-default'
})
</script>

<style scoped>
.purity-badge {
	display: inline-flex;
	padding: 2px 8px;
	border-radius: 4px;
	font-size: 11px;
	font-weight: 700;
	letter-spacing: 0.03em;
}
.purity-24k {
	background: #fef3c7;
	color: #92400e;
}
.purity-22k {
	background: #fef9c3;
	color: #854d0e;
}
.purity-18k {
	background: #fefce8;
	color: #a16207;
}
.purity-14k {
	background: #fff7ed;
	color: #c2410c;
}
.purity-10k {
	background: #fff1f2;
	color: #be123c;
}
.purity-925 {
	background: #f1f5f9;
	color: #475569;
}
.purity-plat {
	background: #e2e8f0;
	color: #334155;
}
.purity-default {
	background: #f8fafc;
	color: #64748b;
}
</style>
