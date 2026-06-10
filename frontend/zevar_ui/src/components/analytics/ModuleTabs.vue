<template>
	<nav
		class="module-tabs"
		:class="{ stuck: stuck }"
		role="tablist"
		aria-label="Analytics modules"
	>
		<button
			v-for="t in tabs"
			:key="t.key"
			type="button"
			role="tab"
			:aria-selected="active === t.key"
			:tabindex="active === t.key ? 0 : -1"
			class="module-tab"
			:class="{ active: active === t.key }"
			@click="$emit('change', t.key)"
		>
			<span v-if="t.icon" class="material-symbols-outlined module-tab__icon">{{
				t.icon
			}}</span>
			<span class="module-tab__label">{{ t.label }}</span>
			<span v-if="t.badge" class="module-tab__badge">{{ t.badge }}</span>
		</button>
	</nav>
</template>

<script setup>
/**
 * ModuleTabs — Plan §5.3, §7.6, 80 LOC budget.
 * Tab strip with glass-on-scroll (Bulb Studio).
 */
import { onMounted, onUnmounted, ref } from 'vue'

const props = defineProps({
	tabs: { type: Array, required: true },
	active: { type: String, required: true },
})
defineEmits(['change'])

const stuck = ref(false)
let sentinel = null
let io = null

onMounted(() => {
	if (typeof IntersectionObserver === 'undefined') return
	sentinel = document.createElement('div')
	sentinel.style.height = '1px'
	sentinel.style.width = '100%'
	sentinel.style.position = 'absolute'
	sentinel.style.top = '0'
	document.body.prepend(sentinel)
	io = new IntersectionObserver(
		([entry]) => {
			stuck.value = !entry.isIntersecting
		},
		{ threshold: 0 }
	)
	io.observe(sentinel)
})

onUnmounted(() => {
	if (io) io.disconnect()
	if (sentinel?.parentNode) sentinel.parentNode.removeChild(sentinel)
})
</script>

<style scoped>
.module-tabs {
	position: sticky;
	top: 0;
	z-index: 30;
	display: flex;
	gap: 4px;
	padding: 4px;
	background: var(--bg-1);
	border: 1px solid var(--glass-border);
	border-radius: var(--radius-md);
	overflow-x: auto;
	scrollbar-width: none;
}
.module-tabs::-webkit-scrollbar {
	display: none;
}
.module-tabs.stuck {
	background: var(--glass-tint-dark);
	backdrop-filter: blur(var(--glass-1-blur));
	-webkit-backdrop-filter: blur(var(--glass-1-blur));
	border-color: var(--glass-border-strong);
}
.module-tab {
	display: inline-flex;
	align-items: center;
	gap: 6px;
	padding: 8px 14px;
	border-radius: var(--radius-sm);
	background: transparent;
	border: 0;
	cursor: pointer;
	color: var(--text-secondary);
	font-size: 13px;
	font-weight: 600;
	white-space: nowrap;
	transition: background var(--duration-fast) var(--ease-out),
		color var(--duration-fast) var(--ease-out);
}
.module-tab:hover {
	background: var(--bg-2);
	color: var(--text-primary);
}
.module-tab.active {
	background: var(--color-gold);
	color: #0a0a0f;
}
.module-tab__icon {
	font-size: 16px;
}
.module-tab__badge {
	font-size: 10px;
	font-weight: 800;
	background: rgba(0, 0, 0, 0.18);
	color: inherit;
	padding: 1px 6px;
	border-radius: 999px;
}
.module-tab:not(.active) .module-tab__badge {
	background: var(--bg-3);
	color: var(--text-secondary);
}
</style>
