<template>
	<div class="bom-tree" v-if="bom">
		<div class="bom-header" @click="expanded = !expanded">
			<span class="tree-toggle">{{ expanded ? '▼' : '▶' }}</span>
			<span class="parent-label">{{ bom.bom_name }}</span>
			<span class="parent-item">{{ bom.parent_item_code }}</span>
			<span class="cost-badge" v-if="totalCost > 0">${{ totalCost.toFixed(2) }}</span>
		</div>

		<transition name="slide">
			<div v-if="expanded" class="bom-children">
				<div
					v-for="(comp, idx) in bom.components || []"
					:key="idx"
					class="component-row"
					:class="{ selected: selectedIndex === idx }"
					@click="
						$emit('select-component', comp, idx);
						selectedIndex = idx;
					"
				>
					<span class="component-type-badge" :class="typeClass(comp.component_type)">
						{{ comp.component_type }}
					</span>
					<span class="component-name">{{
						comp.component_item_name || comp.component_item
					}}</span>
					<span class="component-qty">× {{ comp.qty_per_build }}</span>
					<span class="component-uom">{{ comp.uom }}</span>
					<span v-if="comp.serial_required" class="serial-tag">SN</span>
					<span v-if="comp.cost_share_pct" class="share-pct"
						>{{ comp.cost_share_pct }}%</span
					>
				</div>

				<div v-if="!bom.components?.length" class="empty-state">
					No components added yet
				</div>
			</div>
		</transition>
	</div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
	bom: { type: Object, required: true },
})

defineEmits(['select-component'])

const expanded = ref(true)
const selectedIndex = ref(-1)

const totalCost = computed(() => {
	if (!props.bom?.components) return 0
	return (
		props.bom.components.reduce(
			(sum, c) => sum + (c.qty_per_build || 0) * (c.valuation_rate || 0),
			0
		) +
		(props.bom.labor_minutes || 0) * (props.bom.labor_cost_per_minute || 0)
	)
})

function typeClass(type) {
	const map = {
		Setting: 'type-setting',
		'Center Stone': 'type-center',
		Melee: 'type-melee',
		Finding: 'type-finding',
		Labor: 'type-labor',
	}
	return map[type] || 'type-other'
}
</script>

<style scoped>
.bom-tree {
	border: 1px solid var(--border-color, #e2e8f0);
	border-radius: 8px;
	overflow: hidden;
}
.bom-header {
	display: flex;
	align-items: center;
	gap: 8px;
	padding: 12px 16px;
	background: var(--bg-light, #f8fafc);
	cursor: pointer;
	font-weight: 600;
}
.bom-header:hover {
	background: var(--bg-hover, #f1f5f9);
}
.tree-toggle {
	width: 16px;
	font-size: 10px;
	color: var(--text-muted, #94a3b8);
}
.parent-item {
	color: var(--text-muted, #94a3b8);
	font-weight: 400;
	font-size: 13px;
}
.cost-badge {
	margin-left: auto;
	background: var(--green-50, #f0fdf4);
	color: var(--green-700, #15803d);
	padding: 2px 8px;
	border-radius: 4px;
	font-size: 12px;
}
.bom-children {
	border-top: 1px solid var(--border-color, #e2e8f0);
}
.component-row {
	display: flex;
	align-items: center;
	gap: 8px;
	padding: 10px 16px 10px 32px;
	border-bottom: 1px solid var(--border-color-light, #f1f5f9);
	cursor: pointer;
	transition: background 0.15s;
}
.component-row:hover {
	background: var(--bg-hover, #f8fafc);
}
.component-row.selected {
	background: var(--primary-50, #eff6ff);
	border-left: 3px solid var(--primary, #3b82f6);
}
.component-type-badge {
	font-size: 11px;
	padding: 2px 6px;
	border-radius: 4px;
	font-weight: 600;
	text-transform: uppercase;
	letter-spacing: 0.02em;
}
.type-setting {
	background: #fef3c7;
	color: #92400e;
}
.type-center {
	background: #dbeafe;
	color: #1e40af;
}
.type-melee {
	background: #e0e7ff;
	color: #3730a3;
}
.type-finding {
	background: #f3e8ff;
	color: #6b21a8;
}
.type-labor {
	background: #fce7f3;
	color: #9d174d;
}
.type-other {
	background: #f1f5f9;
	color: #475569;
}
.component-name {
	flex: 1;
	font-size: 13px;
}
.component-qty {
	color: var(--text-muted, #64748b);
	font-size: 13px;
}
.component-uom {
	color: var(--text-muted, #94a3b8);
	font-size: 12px;
}
.serial-tag {
	background: var(--orange-100, #ffedd5);
	color: var(--orange-700, #c2410c);
	font-size: 10px;
	padding: 1px 4px;
	border-radius: 3px;
	font-weight: 600;
}
.share-pct {
	color: var(--text-muted, #94a3b8);
	font-size: 11px;
}
.empty-state {
	padding: 24px;
	text-align: center;
	color: var(--text-muted, #94a3b8);
	font-size: 13px;
}
.slide-enter-active,
.slide-leave-active {
	transition: all 0.2s ease;
	overflow: hidden;
}
.slide-enter-from,
.slide-leave-to {
	max-height: 0;
	opacity: 0;
}
</style>
