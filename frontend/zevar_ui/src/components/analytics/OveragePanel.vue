<template>
	<section class="premium-card mt-4">
		<div class="flex items-center justify-between gap-3 mb-3">
			<div>
				<h3 class="text-sm font-bold text-gray-900 dark:text-white">
					Overage Clearance Queue
				</h3>
				<p class="text-[10px] text-gray-500">
					Dead-stock score based on age, velocity, margin, and carrying cost.
				</p>
			</div>
			<button class="refresh-btn" type="button" :disabled="loading" @click="load">
				<span class="material-symbols-outlined" :class="{ 'animate-spin': loading }"
					>refresh</span
				>
			</button>
		</div>

		<div v-if="loading" class="space-y-2">
			<div
				v-for="n in 4"
				:key="n"
				class="h-11 bg-gray-100 dark:bg-gray-800 rounded animate-pulse"
			/>
		</div>
		<div v-else-if="error" class="text-xs text-red-500 py-4">{{ error }}</div>
		<div v-else-if="!items.length" class="text-xs text-gray-400 text-center py-6">
			No overage items above threshold.
		</div>
		<div v-else class="queue-list">
			<button
				v-for="item in items"
				:key="item.item_code"
				type="button"
				class="queue-row"
				@click="openAction(item)"
			>
				<div class="min-w-0">
					<div class="font-bold truncate text-gray-900 dark:text-white">
						{{ item.item_name || item.item_code }}
					</div>
					<div class="meta">
						{{ item.item_code }} - {{ item.age_bucket }} days -
						{{ item.recommended_action }}
					</div>
				</div>
				<div class="text-right">
					<div class="font-mono text-xs text-gray-700 dark:text-gray-300">
						${{ fmt(item.stock_value) }}
					</div>
					<div class="meta">{{ Number(item.actual_qty || 0).toFixed(0) }} qty</div>
				</div>
				<OverageScoreBadge :score="Number(item.overage_score || 0)" />
			</button>
		</div>

		<OverageActionModal
			:open="modalOpen"
			:items="selected ? [selected] : []"
			:loading="submitting"
			@close="modalOpen = false"
			@confirm="submit"
		/>
	</section>
</template>

<script setup>
import { fmt } from '@/utils/format'
import { onMounted, ref } from 'vue'
import { useOverageActions } from '@/composables/analytics/useOverageActions'
import OverageActionModal from './OverageActionModal.vue'
import OverageScoreBadge from './OverageScoreBadge.vue'

const { loading, error, score, submitAction } = useOverageActions()
const items = ref([])
const selected = ref(null)
const modalOpen = ref(false)
const submitting = ref(false)

onMounted(load)

async function load() {
	const res = await score({ days_threshold: 90, min_score: 50, limit: 10 })
	items.value = res?.items || []
}

function openAction(item) {
	selected.value = item
	modalOpen.value = true
}

async function submit({ actionType, params }) {
	if (!selected.value) return
	submitting.value = true
	try {
		await submitAction(actionType, [selected.value.item_code], params)
		modalOpen.value = false
		await load()
	} finally {
		submitting.value = false
	}
}
</script>

<style scoped>
.refresh-btn {
	width: 34px;
	height: 34px;
	border-radius: 8px;
	display: inline-flex;
	align-items: center;
	justify-content: center;
	border: 1px solid rgba(148, 163, 184, 0.22);
	color: #6b7280;
}
.refresh-btn:hover {
	color: #d4af37;
	border-color: rgba(212, 175, 55, 0.5);
}
.queue-list {
	display: flex;
	flex-direction: column;
	gap: 6px;
}
.queue-row {
	width: 100%;
	display: grid;
	grid-template-columns: minmax(0, 1fr) 90px 44px;
	align-items: center;
	gap: 10px;
	padding: 9px 10px;
	border-radius: 8px;
	text-align: left;
	background: rgba(148, 163, 184, 0.06);
	border: 1px solid transparent;
}
.queue-row:hover {
	border-color: rgba(212, 175, 55, 0.38);
	background: rgba(212, 175, 55, 0.06);
}
.meta {
	margin-top: 2px;
	font-size: 10px;
	color: #6b7280;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}
@media (max-width: 640px) {
	.queue-row {
		grid-template-columns: minmax(0, 1fr) 42px;
	}
	.queue-row > div:nth-child(2) {
		display: none;
	}
}
</style>
