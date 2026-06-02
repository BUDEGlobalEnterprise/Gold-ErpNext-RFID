<template>
	<div class="tab-content">
		<div v-if="loading" class="glass-tier-1 p-6 rounded-2xl text-center text-sm text-gray-500">
			<span class="material-symbols-outlined animate-spin align-middle">progress_activity</span>
			Generating insights…
		</div>

		<div v-else-if="error" class="glass-tier-1 p-6 rounded-2xl text-sm text-red-500">
			{{ error }}
		</div>

		<div v-else-if="!brief?.insights?.length" class="glass-tier-1 p-6 rounded-2xl text-sm text-gray-500 text-center">
			No insights available right now. Try refreshing.
		</div>

		<div v-else class="space-y-3">
			<article
				v-for="ins in brief.insights"
				:key="ins.id"
				class="glass-tier-1 p-4 rounded-2xl"
			>
				<div class="flex items-center gap-2 mb-1.5">
					<span class="px-1.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider" :class="sevClass(ins.severity)">
						{{ ins.category }}
					</span>
					<span class="text-[10px] text-gray-500 font-mono">{{ ins.id }}</span>
				</div>
				<p class="text-sm leading-relaxed text-gray-900 dark:text-white">{{ ins.text }}</p>
				<div v-if="ins.grounded_numbers?.length" class="mt-2 flex flex-wrap gap-2">
					<span
						v-for="(g, i) in ins.grounded_numbers"
						:key="i"
						class="text-[10px] font-mono px-2 py-0.5 rounded bg-[color:var(--color-gold)]/10 text-[color:var(--color-gold)]"
						:title="`Source: ${g.source_query || 'n/a'}`"
					>
						{{ g.label }}: <strong>{{ g.value }}</strong>
					</span>
				</div>
				<div v-if="ins.recommended_action" class="mt-2 text-[11px] text-gray-600 dark:text-gray-400">
					<span class="material-symbols-outlined !text-sm align-middle">lightbulb</span>
					{{ ins.recommended_action.description }}
				</div>
				<div class="mt-2 flex gap-2">
					<button class="text-[10px] font-bold text-emerald-500 hover:underline" @click="vote(ins, 1)">👍 Helpful</button>
					<button class="text-[10px] font-bold text-red-500 hover:underline" @click="vote(ins, -1)">👎 Not helpful</button>
				</div>
			</article>
		</div>
	</div>
</template>

<script setup>
/**
 * AIInsightsTab — Plan §7.1, 200 LOC budget.
 * Phase 7 ships the shell; Phase 8 wires the real RAG endpoint.
 */
import { ref, onMounted } from 'vue'
import { useRAGQuery } from '@/composables/analytics/useRAGQuery'

const { data, loading, error, fetchInsights, submitFeedback } = useRAGQuery()
const brief = ref(null)

async function load(scope = 'today') {
	try {
		const res = await fetchInsights({ scope })
		brief.value = res
	} catch (e) {
		console.error('AIInsights load:', e)
	}
}
onMounted(load)

async function vote(ins, rating) {
	try {
		await submitFeedback(ins.id, rating)
	} catch (e) {
		console.warn('feedback submit failed:', e)
	}
}

function sevClass(s) {
	const map = {
		info: 'bg-blue-500/15 text-blue-600 dark:text-blue-400',
		warning: 'bg-amber-500/15 text-amber-600 dark:text-amber-400',
		opportunity: 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400',
		critical: 'bg-red-500/15 text-red-600 dark:text-red-400',
	}
	return map[s] || map.info
}
</script>
