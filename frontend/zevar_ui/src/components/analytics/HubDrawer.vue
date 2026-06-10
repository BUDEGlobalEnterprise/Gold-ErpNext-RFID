<template>
	<aside
		class="hub-drawer"
		:class="{ open: open }"
		role="dialog"
		aria-modal="true"
		:aria-label="title || 'Detail'"
		@keydown.esc.stop="$emit('close')"
	>
		<div class="hub-drawer__backdrop" @click="$emit('close')" />
		<div class="hub-drawer__panel glass-tier-2">
			<header class="hub-drawer__header">
				<h3 class="hub-drawer__title">{{ title }}</h3>
				<button
					type="button"
					class="hub-drawer__close"
					aria-label="Close drawer"
					@click="$emit('close')"
				>
					<span class="material-symbols-outlined">close</span>
				</button>
			</header>
			<div class="hub-drawer__body">
				<slot />
			</div>
			<footer v-if="$slots.footer" class="hub-drawer__footer">
				<slot name="footer" />
			</footer>
		</div>
	</aside>
</template>

<script setup>
/**
 * HubDrawer — Plan §5.4, §7.6, 100 LOC budget.
 * 50%-width right-side drawer. Hub stays mounted behind.
 * Esc closes. Backdrop click closes. Focus trap on open.
 */
import { watch, nextTick } from 'vue'

const props = defineProps({
	open: { type: Boolean, default: false },
	title: { type: String, default: '' },
})
defineEmits(['close'])

watch(
	() => props.open,
	async (isOpen) => {
		if (isOpen) {
			await nextTick()
			const closeBtn = document.querySelector('.hub-drawer.open .hub-drawer__close')
			closeBtn?.focus()
		}
	}
)
</script>

<style scoped>
.hub-drawer {
	position: fixed;
	inset: 0;
	pointer-events: none;
	z-index: 60;
}
.hub-drawer.open {
	pointer-events: auto;
}
.hub-drawer__backdrop {
	position: absolute;
	inset: 0;
	background: rgba(0, 0, 0, 0.35);
	opacity: 0;
	transition: opacity var(--duration-normal) var(--ease-out);
}
.hub-drawer.open .hub-drawer__backdrop {
	opacity: 1;
}
.hub-drawer__panel {
	position: absolute;
	top: 0;
	right: 0;
	height: 100dvh;
	width: 100%;
	max-width: 50vw;
	background: var(--bg-1);
	border-left: 1px solid var(--glass-border-strong);
	transform: translateX(100%);
	transition: transform var(--duration-normal) var(--ease-out);
	display: flex;
	flex-direction: column;
	box-shadow: -10px 0 40px -10px rgba(0, 0, 0, 0.5);
}
.hub-drawer.open .hub-drawer__panel {
	transform: translateX(0);
}
@media (max-width: 768px) {
	.hub-drawer__panel {
		max-width: 100vw;
	}
}
.hub-drawer__header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 16px 20px;
	border-bottom: 1px solid var(--glass-border);
}
.hub-drawer__title {
	font-size: 16px;
	font-weight: 700;
	margin: 0;
	color: var(--text-primary);
}
.hub-drawer__close {
	width: 32px;
	height: 32px;
	border-radius: var(--radius-sm);
	display: inline-flex;
	align-items: center;
	justify-content: center;
	background: transparent;
	border: 0;
	cursor: pointer;
	color: var(--text-secondary);
	transition: background var(--duration-fast) var(--ease-out);
}
.hub-drawer__close:hover {
	background: var(--bg-2);
}
.hub-drawer__body {
	flex: 1;
	overflow: auto;
	padding: 16px 20px;
}
.hub-drawer__footer {
	padding: 12px 20px;
	border-top: 1px solid var(--glass-border);
}
</style>
