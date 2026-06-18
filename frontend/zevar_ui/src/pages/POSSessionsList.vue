<template>
	<AppLayout>
		<div class="max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
			<div class="mb-8 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
				<div>
					<h1 class="premium-title !text-3xl">POS Sessions</h1>
					<p class="premium-subtitle mt-1">View historical shifts, cash drawer balances, and variances</p>
				</div>
				<router-link
					to="/"
					class="px-4 py-2 bg-white dark:bg-warm-dark-700 border border-gray-200 dark:border-warm-border rounded-lg text-sm font-medium hover:bg-gray-50 dark:hover:bg-warm-dark-600 transition"
				>
					Back to Dashboard
				</router-link>
			</div>

			<div v-if="loading" class="flex justify-center py-12">
				<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-[#D4AF37]"></div>
			</div>

			<div v-else-if="error" class="p-6 bg-red-500/10 border border-red-500/30 rounded-xl text-red-500 mb-8">
				{{ error }}
			</div>

			<div v-else class="bg-white dark:bg-warm-card border border-gray-100 dark:border-warm-border/50 rounded-2xl overflow-hidden shadow-sm">
				<div class="overflow-x-auto">
					<table class="w-full text-left text-sm whitespace-nowrap">
						<thead class="bg-gray-50/50 dark:bg-warm-dark-700/50 border-b border-gray-100 dark:border-warm-border/50">
							<tr>
								<th class="px-6 py-4 font-bold text-gray-500 dark:text-gray-400">Session ID</th>
								<th class="px-6 py-4 font-bold text-gray-500 dark:text-gray-400">User</th>
								<th class="px-6 py-4 font-bold text-gray-500 dark:text-gray-400">Profile</th>
								<th class="px-6 py-4 font-bold text-gray-500 dark:text-gray-400">Status</th>
								<th class="px-6 py-4 font-bold text-gray-500 dark:text-gray-400">Start / End Time</th>
								<th class="px-6 py-4 font-bold text-gray-500 dark:text-gray-400 text-right">Variance</th>
							</tr>
						</thead>
						<tbody class="divide-y divide-gray-100 dark:divide-warm-border/50">
							<tr 
								v-for="session in sessions" 
								:key="session.name"
								class="hover:bg-gray-50/50 dark:hover:bg-warm-dark-700/30 transition"
							>
								<td class="px-6 py-4 font-medium text-[#D4AF37]">
									{{ session.name }}
								</td>
								<td class="px-6 py-4 text-gray-700 dark:text-gray-300">
									{{ session.user }}
								</td>
								<td class="px-6 py-4 text-gray-600 dark:text-gray-400">
									{{ session.pos_profile }}
								</td>
								<td class="px-6 py-4">
									<span 
										class="px-2.5 py-1 rounded-full text-xs font-bold"
										:class="session.status === 'Open' ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20' : 'bg-gray-500/10 text-gray-500 border border-gray-500/20'"
									>
										{{ session.status }}
									</span>
								</td>
								<td class="px-6 py-4 text-gray-500 dark:text-gray-400">
									<div>{{ formatDate(session.period_start_date) }}</div>
									<div class="text-xs mt-0.5" v-if="session.period_end_date">to {{ formatDate(session.period_end_date) }}</div>
								</td>
								<td class="px-6 py-4 text-right">
									<template v-if="session.status === 'Closed'">
										<div 
											class="font-bold font-mono"
											:class="{
												'text-emerald-500': session.cash_variance === 0,
												'text-red-500': session.cash_variance < 0,
												'text-amber-500': session.cash_variance > 0
											}"
										>
											{{ formatCurrency(session.cash_variance) }}
										</div>
									</template>
									<span v-else class="text-gray-400">-</span>
								</td>
							</tr>
							<tr v-if="sessions.length === 0">
								<td colspan="6" class="px-6 py-12 text-center text-gray-500">
									No POS sessions found.
								</td>
							</tr>
						</tbody>
					</table>
				</div>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'

const loading = ref(true)
const sessions = ref([])
const error = ref('')

async function fetchSessions() {
	loading.value = true
	error.value = ''
	try {
		const res = await fetch('/api/method/zevar_core.api.pos_session.get_sessions_list', {
			headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' }
		})
		const json = await res.json()
		if (!res.ok) {
			throw new Error(json.message || 'Failed to fetch sessions')
		}
		const data = json.message || json
		sessions.value = data.sessions || []
	} catch (e) {
		error.value = e.message || 'An error occurred while loading sessions'
	} finally {
		loading.value = false
	}
}

function formatDate(dateString) {
	if (!dateString) return ''
	const date = new Date(dateString)
	return date.toLocaleString('en-US', {
		month: 'short',
		day: 'numeric',
		hour: 'numeric',
		minute: '2-digit',
	})
}

function formatCurrency(amount) {
	if (amount === undefined || amount === null) return '$0.00'
	const num = Number(amount)
	const prefix = num > 0 ? '+' : ''
	return prefix + '$' + Math.abs(num).toFixed(2)
}

onMounted(() => {
	fetchSessions()
})
</script>
