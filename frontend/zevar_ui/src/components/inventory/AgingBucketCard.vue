<template>
	<div class="aging-bucket-card" :class="bucketClass">
		<div class="bucket-header">
			<span class="bucket-label">{{ label }}</span>
			<span class="bucket-count">{{ count }}</span>
		</div>
		<div class="bucket-value">${{ formatCurrency(value) }}</div>
		<div v-if="pctOfTotal" class="bucket-pct">{{ pctOfTotal }}% of total</div>
	</div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
	bucket: { type: String, default: '0-30' }, // 0-30 | 31-60 | 61-90 | 90+
	count: { type: Number, default: 0 },
	value: { type: Number, default: 0 },
	totalValue: { type: Number, default: 0 },
})

const label = computed(() => {
	const map = {
		'0-30': '0–30 days',
		'31-60': '31–60 days',
		'61-90': '61–90 days',
		'90+': '90+ days',
	}
	return map[props.bucket] || props.bucket
})

const bucketClass = computed(() => `bucket-${props.bucket.replace('+', 'plus')}`)

const pctOfTotal = computed(() => {
	if (!props.totalValue) return 0
	return Math.round((props.value / props.totalValue) * 100)
})

function formatCurrency(v) {
	return new Intl.NumberFormat('en-US', {
		minimumFractionDigits: 0,
		maximumFractionDigits: 0,
	}).format(v)
}
</script>

<style scoped>
.aging-bucket-card {
	padding: 16px;
	border-radius: 8px;
	border: 1px solid var(--border-color, #e2e8f0);
	transition: transform 0.15s, box-shadow 0.15s;
}
.aging-bucket-card:hover {
	transform: translateY(-2px);
	box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}
.bucket-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 8px;
}
.bucket-label {
	font-size: 12px;
	font-weight: 600;
	text-transform: uppercase;
	letter-spacing: 0.04em;
}
.bucket-count {
	font-size: 20px;
	font-weight: 700;
}
.bucket-value {
	font-size: 18px;
	font-weight: 600;
	margin-bottom: 4px;
}
.bucket-pct {
	font-size: 11px;
	opacity: 0.7;
}
.bucket-0-30 {
	background: #f0fdf4;
	border-color: #bbf7d0;
}
.bucket-0-30 .bucket-label {
	color: #166534;
}
.bucket-0-30 .bucket-value {
	color: #15803d;
}
.bucket-31-60 {
	background: #fefce8;
	border-color: #fef08a;
}
.bucket-31-60 .bucket-label {
	color: #854d0e;
}
.bucket-31-60 .bucket-value {
	color: #a16207;
}
.bucket-61-90 {
	background: #fff7ed;
	border-color: #fed7aa;
}
.bucket-61-90 .bucket-label {
	color: #9a3412;
}
.bucket-61-90 .bucket-value {
	color: #c2410c;
}
.bucket-90plus {
	background: #fef2f2;
	border-color: #fecaca;
}
.bucket-90plus .bucket-label {
	color: #991b1b;
}
.bucket-90plus .bucket-value {
	color: #dc2626;
}
</style>
