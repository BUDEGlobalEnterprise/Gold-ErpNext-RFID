<template>
	<div class="bench-tracker">
		<div class="tracker-header">
			<h4 class="tracker-title">🏗️ External Bench Items</h4>
			<span class="item-count">{{ items.length }} items out</span>
		</div>

		<div v-if="!items.length" class="empty-state">
			<span class="empty-icon">✅</span>
			<p>No items currently at external bench vendors</p>
		</div>

		<div v-else class="tracker-list">
			<div
				v-for="item in sortedItems"
				:key="item.serial_no || item.repair_order"
				class="tracker-row"
				:class="agingClass(item)"
			>
				<div class="row-main">
					<span class="serial">{{ item.serial_no || '—' }}</span>
					<span class="item-name">{{ item.item_name }}</span>
					<span class="vendor-badge">{{ item.vendor_name }}</span>
				</div>
				<div class="row-meta">
					<span class="dispatched">Sent: {{ formatDate(item.dispatched_at) }}</span>
					<span v-if="item.expected_return" class="expected"
						>Due: {{ formatDate(item.expected_return) }}</span
					>
					<span class="days-out" :class="agingClass(item)"> {{ daysOut(item) }}d </span>
				</div>
				<div class="row-actions">
					<button class="btn-action btn-receive" @click="$emit('receive', item)">
						📥 Receive
					</button>
					<button
						v-if="daysOut(item) >= 15"
						class="btn-action btn-escalate"
						@click="$emit('escalate', item)"
					>
						⚠️ Escalate
					</button>
					<a
						v-if="item.repair_order"
						class="btn-action btn-link"
						:href="`/app/repair-order/${item.repair_order}`"
					>
						RO#{{ item.repair_order }}
					</a>
				</div>
			</div>
		</div>

		<!-- Summary Strip -->
		<div v-if="items.length" class="summary-strip">
			<div class="summary-item">
				<span class="summary-label">0–7d</span>
				<span class="summary-value aging-green">{{ countByAging('green') }}</span>
			</div>
			<div class="summary-item">
				<span class="summary-label">8–14d</span>
				<span class="summary-value aging-amber">{{ countByAging('amber') }}</span>
			</div>
			<div class="summary-item">
				<span class="summary-label">15d+</span>
				<span class="summary-value aging-red">{{ countByAging('red') }}</span>
			</div>
		</div>
	</div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
	items: { type: Array, default: () => [] },
})

defineEmits(['receive', 'escalate'])

function daysOut(item) {
	const dispatched = new Date(item.dispatched_at)
	const now = new Date()
	return Math.floor((now - dispatched) / (1000 * 60 * 60 * 24))
}

function agingClass(item) {
	const days = daysOut(item)
	if (days >= 15) return 'aging-red'
	if (days >= 8) return 'aging-amber'
	return 'aging-green'
}

function countByAging(level) {
	return props.items.filter((i) => agingClass(i) === `aging-${level}`).length
}

function formatDate(dt) {
	if (!dt) return '—'
	return new Date(dt).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

const sortedItems = computed(() => [...props.items].sort((a, b) => daysOut(b) - daysOut(a)))
</script>

<style scoped>
.bench-tracker {
	border: 1px solid var(--border-color, #e2e8f0);
	border-radius: 8px;
	overflow: hidden;
}
.tracker-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 12px 16px;
	background: var(--bg-light, #f8fafc);
	border-bottom: 1px solid #e2e8f0;
}
.tracker-title {
	font-size: 14px;
	font-weight: 700;
	margin: 0;
}
.item-count {
	font-size: 12px;
	color: #64748b;
	background: #e2e8f0;
	padding: 2px 8px;
	border-radius: 10px;
}
.empty-state {
	padding: 32px;
	text-align: center;
	color: #94a3b8;
}
.empty-icon {
	font-size: 32px;
	display: block;
	margin-bottom: 8px;
}
.tracker-row {
	padding: 12px 16px;
	border-bottom: 1px solid #f1f5f9;
	display: flex;
	flex-direction: column;
	gap: 6px;
}
.tracker-row:hover {
	background: #f8fafc;
}
.row-main {
	display: flex;
	align-items: center;
	gap: 8px;
}
.serial {
	font-weight: 600;
	font-size: 13px;
	font-family: monospace;
}
.item-name {
	flex: 1;
	font-size: 13px;
	color: #475569;
}
.vendor-badge {
	font-size: 11px;
	padding: 2px 8px;
	border-radius: 4px;
	background: #e0e7ff;
	color: #3730a3;
	font-weight: 600;
}
.row-meta {
	display: flex;
	gap: 12px;
	font-size: 11px;
	color: #94a3b8;
}
.days-out {
	font-weight: 700;
	padding: 1px 6px;
	border-radius: 3px;
}
.aging-green {
	color: #16a34a;
}
.aging-green.days-out {
	background: #dcfce7;
}
.aging-amber {
	color: #d97706;
}
.aging-amber.days-out {
	background: #fef3c7;
}
.aging-red {
	color: #dc2626;
}
.aging-red.days-out {
	background: #fef2f2;
}
.row-actions {
	display: flex;
	gap: 6px;
}
.btn-action {
	padding: 4px 10px;
	border: 1px solid #e2e8f0;
	border-radius: 4px;
	background: white;
	font-size: 11px;
	cursor: pointer;
	text-decoration: none;
	color: inherit;
	transition: all 0.15s;
}
.btn-receive:hover {
	border-color: #22c55e;
	background: #f0fdf4;
}
.btn-escalate {
	border-color: #fbbf24;
}
.btn-escalate:hover {
	background: #fffbeb;
}
.btn-link {
	color: #6366f1;
}
.summary-strip {
	display: flex;
	border-top: 1px solid #e2e8f0;
}
.summary-item {
	flex: 1;
	padding: 10px;
	text-align: center;
	border-right: 1px solid #f1f5f9;
}
.summary-item:last-child {
	border-right: none;
}
.summary-label {
	display: block;
	font-size: 10px;
	color: #94a3b8;
	text-transform: uppercase;
}
.summary-value {
	display: block;
	font-size: 20px;
	font-weight: 700;
}
</style>
