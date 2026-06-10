<template>
	<Teleport to="body">
		<div v-if="open" class="modal-shell" role="dialog" aria-modal="true">
			<div class="modal-card glass-tier-3">
				<header class="flex items-start justify-between gap-4 mb-4">
					<div>
						<h3 class="text-base font-black text-gray-900 dark:text-white">
							Overage Action
						</h3>
						<p class="text-xs text-gray-500">
							{{ selectedItems.length }} item{{
								selectedItems.length === 1 ? '' : 's'
							}}
							selected
						</p>
					</div>
					<button
						class="icon-btn"
						type="button"
						@click="$emit('close')"
						aria-label="Close"
					>
						<span class="material-symbols-outlined">close</span>
					</button>
				</header>

				<div class="space-y-2 max-h-36 overflow-auto mb-4">
					<div v-for="item in selectedItems" :key="item.item_code" class="item-row">
						<span class="font-bold truncate">{{
							item.item_name || item.item_code
						}}</span>
						<span class="font-mono text-gray-500">{{ item.days_in_inventory }}d</span>
						<OverageScoreBadge :score="Number(item.overage_score || 0)" />
					</div>
				</div>

				<div class="action-grid">
					<button
						v-for="action in actions"
						:key="action.type"
						type="button"
						class="action-card"
						:class="{ 'action-card--active': actionType === action.type }"
						@click="actionType = action.type"
					>
						<span class="material-symbols-outlined">{{ action.icon }}</span>
						<strong>{{ action.label }}</strong>
						<small>{{ action.caption }}</small>
					</button>
				</div>

				<label
					v-if="actionType === 'markdown'"
					class="block mt-4 text-xs font-bold text-gray-600 dark:text-gray-300"
				>
					Markdown %
					<input
						v-model.number="markdownPct"
						min="1"
						max="90"
						type="number"
						class="field"
					/>
				</label>

				<label class="block mt-3 text-xs font-bold text-gray-600 dark:text-gray-300">
					Notes
					<textarea v-model="notes" rows="2" class="field resize-none" />
				</label>

				<footer class="flex justify-end gap-2 mt-5">
					<button type="button" class="btn-secondary" @click="$emit('close')">
						Cancel
					</button>
					<button
						type="button"
						class="btn-primary"
						:disabled="loading || !actionType"
						@click="confirm"
					>
						{{ loading ? 'Applying...' : 'Confirm' }}
					</button>
				</footer>
			</div>
		</div>
	</Teleport>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import OverageScoreBadge from './OverageScoreBadge.vue'

const props = defineProps({
	open: { type: Boolean, default: false },
	items: { type: Array, default: () => [] },
	loading: { type: Boolean, default: false },
})
const emit = defineEmits(['close', 'confirm'])

const actionType = ref('markdown')
const markdownPct = ref(25)
const notes = ref('')
const selectedItems = computed(() => props.items || [])
const actions = [
	{ type: 'markdown', label: 'Markdown', caption: 'Pricing review', icon: 'sell' },
	{ type: 'bundle', label: 'Bundle', caption: 'Pair with mover', icon: 'inventory_2' },
	{ type: 'vault_sale', label: 'Vault Sale', caption: 'Private event', icon: 'lock' },
	{
		type: 'vendor_return',
		label: 'Vendor Return',
		caption: 'Consignment path',
		icon: 'assignment_return',
	},
	{ type: 'repurpose', label: 'Repurpose', caption: 'Bench workflow', icon: 'construction' },
]

watch(
	() => props.open,
	(open) => {
		if (open) {
			actionType.value = 'markdown'
			markdownPct.value = Number(selectedItems.value[0]?.recommended_markdown_pct || 25)
			notes.value = ''
		}
	}
)

function confirm() {
	emit('confirm', {
		actionType: actionType.value,
		params: { markdown_pct: markdownPct.value, notes: notes.value },
	})
}
</script>

<style scoped>
.modal-shell {
	position: fixed;
	inset: 0;
	z-index: 80;
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 18px;
	background: rgba(0, 0, 0, 0.46);
}
.modal-card {
	width: min(760px, 100%);
	max-height: min(86vh, 760px);
	overflow: auto;
	border-radius: var(--radius-lg, 16px);
	padding: 18px;
}
.icon-btn {
	width: 34px;
	height: 34px;
	border-radius: 8px;
	display: inline-flex;
	align-items: center;
	justify-content: center;
	color: #6b7280;
}
.icon-btn:hover {
	background: rgba(148, 163, 184, 0.14);
	color: #d4af37;
}
.item-row {
	display: grid;
	grid-template-columns: minmax(0, 1fr) 54px 44px;
	gap: 8px;
	align-items: center;
	padding: 8px 10px;
	border-radius: 8px;
	background: rgba(148, 163, 184, 0.08);
	font-size: 12px;
}
.action-grid {
	display: grid;
	grid-template-columns: repeat(5, minmax(0, 1fr));
	gap: 8px;
}
.action-card {
	min-height: 86px;
	border-radius: 8px;
	border: 1px solid rgba(148, 163, 184, 0.22);
	padding: 9px;
	display: flex;
	flex-direction: column;
	align-items: flex-start;
	gap: 4px;
	text-align: left;
	color: #6b7280;
	background: rgba(255, 255, 255, 0.04);
}
.action-card strong {
	color: currentColor;
	font-size: 12px;
}
.action-card small {
	font-size: 10px;
	opacity: 0.72;
}
.action-card--active {
	color: #d4af37;
	border-color: rgba(212, 175, 55, 0.55);
	background: rgba(212, 175, 55, 0.09);
}
.field {
	margin-top: 6px;
	width: 100%;
	border-radius: 8px;
	border: 1px solid rgba(148, 163, 184, 0.24);
	background: rgba(255, 255, 255, 0.04);
	padding: 8px 10px;
	outline: none;
}
.field:focus {
	border-color: rgba(212, 175, 55, 0.65);
}
.btn-secondary,
.btn-primary {
	height: 36px;
	border-radius: 8px;
	padding: 0 14px;
	font-size: 12px;
	font-weight: 800;
}
.btn-secondary {
	border: 1px solid rgba(148, 163, 184, 0.28);
	color: #6b7280;
}
.btn-primary {
	background: #d4af37;
	color: #0a0a0f;
}
.btn-primary:disabled {
	opacity: 0.55;
	cursor: not-allowed;
}
@media (max-width: 720px) {
	.action-grid {
		grid-template-columns: repeat(2, minmax(0, 1fr));
	}
}
</style>
