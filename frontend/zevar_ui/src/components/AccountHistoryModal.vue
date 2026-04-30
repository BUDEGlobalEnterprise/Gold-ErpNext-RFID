<template>
	<BaseModal :show="show" @close="close" max-width="max-w-lg">
		<template #header>
			<h2 class="text-lg font-bold text-gray-900 dark:text-white">Recent Activity</h2>
		</template>

		<!-- Today's Summary -->
		<div class="p-6 space-y-6">
			<div
				v-if="summary"
				class="bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-xl p-5"
			>
				<div class="flex justify-around">
					<div class="text-center">
						<span class="block text-2xl font-bold text-white">{{
							summary.transaction_count
						}}</span>
						<span class="block text-xs text-white/60 mt-1">Transactions</span>
					</div>
					<div class="text-center">
						<span class="block text-2xl font-bold text-white"
							>${{ formatAmount(summary.total_sales) }}</span
						>
						<span class="block text-xs text-white/60 mt-1">Total Sales</span>
					</div>
					<div class="text-center">
						<span class="block text-2xl font-bold text-white"
							>${{ formatAmount(summary.average_sale) }}</span
						>
						<span class="block text-xs text-white/60 mt-1">Avg Sale</span>
					</div>
				</div>
			</div>

			<!-- Activity List -->
			<div>
				<h4 class="text-xs text-white/60 uppercase tracking-wider mb-3">
					Recent Transactions
				</h4>
				<div v-if="transactions.length" class="flex flex-col gap-2">
					<div
						v-for="tx in transactions"
						:key="tx.name"
						class="flex items-center gap-3 p-3 bg-white/5 rounded-lg cursor-pointer hover:bg-white/10 transition-colors"
						@click="viewTransaction(tx.name)"
					>
						<div
							class="w-9 h-9 rounded-full flex items-center justify-center text-base bg-white/10"
						>
							{{ tx.type === 'sale' ? '💰' : tx.type === 'return' ? '↩️' : '📋' }}
						</div>
						<div class="flex-1">
							<div class="text-white font-medium">
								{{ tx.customer || 'Walk-In Customer' }}
							</div>
							<div class="flex gap-3 text-xs text-white/50">
								<span>{{ tx.name }}</span>
								<span>{{ formatTime(tx.posting_time) }}</span>
							</div>
						</div>
						<div
							class="font-semibold text-sm"
							:class="{
								'text-green-500': tx.type === 'sale',
								'text-red-500': tx.type === 'return',
							}"
						>
							{{ tx.type === 'return' ? '-' : '' }}${{
								formatAmount(tx.grand_total)
							}}
						</div>
					</div>
				</div>
				<div v-else class="text-center py-6 text-white/50">No recent transactions</div>
			</div>

			<!-- Session Info -->
			<div v-if="session" class="bg-white/5 rounded-lg p-4">
				<h4 class="text-xs text-white/60 uppercase tracking-wider mb-3">
					Current Session
				</h4>
				<div class="flex flex-col gap-2">
					<div class="flex justify-between text-sm text-white/80">
						<span>Started</span>
						<span>{{ formatTime(session.opening_time) }}</span>
					</div>
					<div class="flex justify-between text-sm text-white/80">
						<span>Duration</span>
						<span>{{ session.duration_hours }}h</span>
					</div>
					<div class="flex justify-between text-sm text-white/80">
						<span>Opening Balance</span>
						<span>${{ formatAmount(session.opening_balance) }}</span>
					</div>
					<div class="flex justify-between text-sm text-white/80">
						<span>Sales Count</span>
						<span>{{ session.sales_count }}</span>
					</div>
				</div>
			</div>
		</div>

		<template #footer>
			<router-link
				to="/history"
				class="px-5 py-2.5 rounded-lg font-semibold transition-colors bg-transparent text-white/80 border border-white/20 hover:bg-white/10"
				@click="close"
			>
				View Full History
			</router-link>
			<button
				class="px-5 py-2.5 rounded-lg font-semibold transition-colors bg-blue-500 text-white hover:bg-blue-600"
				@click="close"
			>
				Close
			</button>
		</template>
	</BaseModal>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { createResource } from 'frappe-ui'
import BaseModal from './BaseModal.vue'

const props = defineProps({
	show: { type: Boolean, default: false },
})

const emit = defineEmits(['close'])

const transactions = ref([])
const summary = ref(null)
const session = ref(null)

const historyResource = createResource({
	url: 'zevar_core.api.sales_history.get_sales_history',
	auto: false,
	onSuccess(data) {
		transactions.value = (data.sales || []).map((s) => ({
			...s,
			type: s.status === 'Return' ? 'return' : 'sale',
		}))
	},
})

const summaryResource = createResource({
	url: 'zevar_core.api.sales_history.get_sales_summary',
	auto: false,
	onSuccess(data) {
		summary.value = data.summary
	},
})

const sessionResource = createResource({
	url: 'zevar_core.api.pos_session.get_session_status',
	auto: false,
	onSuccess(data) {
		if (data.has_active_session) {
			session.value = data.session
		}
	},
})

function formatAmount(amount) {
	if (!amount) return '0.00'
	return Number(amount).toFixed(2)
}

function formatTime(timeStr) {
	if (!timeStr) return ''
	const [hours, minutes] = timeStr.split(':')
	const h = parseInt(hours)
	const ampm = h >= 12 ? 'PM' : 'AM'
	const h12 = h % 12 || 12
	return `${h12}:${minutes} ${ampm}`
}

function viewTransaction(name) {
	window.open(`/app/sales-invoice/${name}`, '_blank')
}

function close() {
	emit('close')
}

async function loadData() {
	await Promise.all([
		historyResource.submit({ page: 1, page_size: 10 }),
		summaryResource.submit({}),
		sessionResource.submit({}),
	])
}

watch(
	() => props.show,
	(val) => {
		if (val) loadData()
	}
)

onMounted(() => {
	if (props.show) loadData()
})
</script>
