<template>
	<button
		type="button"
		:class="['metric-card', 'surface-1', `size-${size}`]"
		:aria-label="ariaLabel"
		:disabled="!clickable"
		@click="onClick"
		@keydown.enter.prevent="onClick"
		@keydown.space.prevent="onClick"
	>
		<div class="metric-card__header">
			<div class="metric-card__icon" :style="{ color: iconColor }">
				<span class="material-symbols-outlined">{{ icon }}</span>
			</div>
			<div class="metric-card__label">{{ label }}</div>
			<BadgeCounter v-if="badge !== null && badge !== undefined" :value="badge" :severity="badgeSeverity" />
		</div>

		<div class="metric-card__value" :class="valueColor">{{ formattedValue }}</div>

		<div v-if="trend !== null && trend !== undefined" class="metric-card__trend">
			<span class="material-symbols-outlined trend-icon" :class="trendClass">
				{{ trend > 0 ? 'trending_up' : trend < 0 ? 'trending_down' : 'trending_flat' }}
			</span>
			<span :class="trendClass">{{ trendLabel }}</span>
		</div>

		<div v-if="sparkline && sparkline.length" class="metric-card__spark">
			<Sparkline :points="sparkline" :stroke-color="iconColor" :width="100" :height="22" />
		</div>

		<div v-if="$slots.footer" class="metric-card__footer">
			<slot name="footer" />
		</div>
	</button>
</template>

<script setup>
/**
 * MetricCard — Plan §7.6, 120 LOC budget.
 * Reusable hero card: number + sparkline + trend + badge.
 * Pixel Show two-font: label is sans, value is monospaced.
 */
import { computed } from 'vue'
import Sparkline from './Sparkline.vue'
import BadgeCounter from './BadgeCounter.vue'
import { useFormatters } from '@/composables/useFormatters'

const props = defineProps({
	label: { type: String, required: true },
	value: { type: [Number, String], default: 0 },
	format: { type: String, default: 'currency' }, // 'currency' | 'number' | 'percent' | 'plain'
	icon: { type: String, default: 'analytics' },
	iconColor: { type: String, default: 'var(--color-gold)' },
	trend: { type: Number, default: null },
	trendSuffix: { type: String, default: '%' },
	trendLabel: { type: String, default: '' },
	sparkline: { type: Array, default: () => [] },
	badge: { type: [Number, String], default: null },
	badgeSeverity: { type: String, default: 'low' },
	size: { type: String, default: 'lg' }, // 'lg' | 'md' | 'sm'
	variant: { type: String, default: 'default' }, // 'default' | 'success' | 'warning' | 'danger'
	clickable: { type: Boolean, default: true },
	ariaLabel: { type: String, default: '' },
})

const emit = defineEmits(['click'])

const { formatCurrency } = useFormatters()

const formattedValue = computed(() => {
	const v = Number(props.value) || 0
	if (props.format === 'currency') return formatCurrency(v, { compact: false })
	if (props.format === 'percent') return `${v.toFixed(1)}%`
	if (props.format === 'plain') return v.toString()
	return v.toLocaleString()
})

const trendClass = computed(() => {
	if (props.trend == null) return ''
	if (props.trend > 0) return 'trend-up'
	if (props.trend < 0) return 'trend-down'
	return 'trend-flat'
})

const valueColor = computed(() => {
	if (props.variant === 'success') return 'text-emerald-500'
	if (props.variant === 'warning') return 'text-amber-500'
	if (props.variant === 'danger') return 'text-red-500'
	return 'text-[color:var(--text-primary)]'
})

function onClick() {
	if (props.clickable) emit('click')
}
</script>

<style scoped>
.metric-card {
	display: flex;
	flex-direction: column;
	gap: 8px;
	text-align: left;
	padding: 14px 16px;
	border-radius: var(--radius-md);
	cursor: pointer;
	transition:
		background var(--duration-fast) var(--ease-out),
		border-color var(--duration-fast) var(--ease-out),
		transform var(--duration-fast) var(--ease-out);
}
.metric-card:hover:not(:disabled) {
	background: var(--bg-2);
}
.metric-card:focus-visible {
	outline: 2px solid var(--color-gold);
	outline-offset: 2px;
}
.metric-card:disabled {
	cursor: default;
	opacity: 0.85;
}
.metric-card__header {
	display: flex;
	align-items: center;
	gap: 8px;
}
.metric-card__icon {
	display: inline-flex;
}
.metric-card__icon .material-symbols-outlined {
	font-size: 16px;
}
.metric-card__label {
	font-size: 10px;
	font-weight: 600;
	letter-spacing: 0.05em;
	text-transform: uppercase;
	color: var(--text-tertiary);
	flex: 1;
}
.metric-card__value {
	font-size: 20px;
	font-weight: 700;
	line-height: 1.05;
}
.size-md .metric-card__value { font-size: 17px; }
.size-sm .metric-card__value { font-size: 14px; }
.metric-card__trend {
	display: inline-flex;
	align-items: center;
	gap: 4px;
	font-size: 10px;
	font-weight: 600;
	color: var(--text-secondary);
}
.trend-icon { font-size: 13px; }
.trend-up { color: var(--green); }
.trend-down { color: var(--red); }
.trend-flat { color: var(--text-tertiary); }
.metric-card__spark {
	margin-top: 2px;
	opacity: 0.9;
}
.metric-card__footer {
	font-size: 9px;
	color: var(--text-tertiary);
}
</style>
