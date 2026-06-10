<template>
	<div class="tab-content">
		<div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
			<KPICard
				label="Net Profit MTD"
				:value="`$${fmt(finance.net_profit_mtd)}`"
				icon="trending_up"
				color="emerald"
				:loading="loading"
			/>
			<KPICard
				label="AR Outstanding"
				:value="`$${fmt(finance.ar_outstanding)}`"
				icon="account_circle"
				color="blue"
				:loading="loading"
			/>
			<KPICard
				label="AP Outstanding"
				:value="`$${fmt(finance.ap_outstanding)}`"
				icon="account_balance_wallet"
				color="amber"
				:loading="loading"
			/>
			<KPICard
				label="Cash Balance"
				:value="`$${fmt(finance.cash_balance)}`"
				icon="payments"
				color="purple"
				:loading="loading"
			/>
		</div>

		<div class="premium-card mt-4">
			<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3">Standard Reports</h3>
			<p class="text-[10px] text-gray-500 mb-3">
				Opens the native ERPNext report viewer (per Plan §6.7, we wrap, not re-implement).
			</p>
			<div class="grid grid-cols-2 lg:grid-cols-3 gap-2">
				<a
					v-for="r in reports"
					:key="r.id"
					:href="r.href"
					target="_blank"
					class="flex items-center gap-2 px-3 py-2.5 rounded-lg border border-gray-200 dark:border-warm-border hover:border-[#D4AF37] transition-colors"
				>
					<span class="material-symbols-outlined !text-base text-[#D4AF37]"
						>description</span
					>
					<span class="text-xs font-bold text-gray-900 dark:text-white">{{
						r.label
					}}</span>
					<span class="material-symbols-outlined !text-sm ml-auto text-gray-400"
						>open_in_new</span
					>
				</a>
			</div>
		</div>

		<div class="premium-card mt-4">
			<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3">All Reports</h3>
			<p class="text-[10px] text-gray-500 mb-2">Browse the full 60+ report catalog.</p>
			<button class="text-xs font-bold text-[#D4AF37] hover:underline" @click="goHub">
				View all reports →
			</button>
		</div>
	</div>
</template>

<script setup>
/**
 * FinanceTab — Plan §7.1, 140 LOC budget.
 * Wraps the existing ERPNext script reports (Plan §6.7).
 */
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { call } from 'frappe-ui'
import KPICard from '@/components/reports/KPICard.vue'

const router = useRouter()
const loading = ref(true)
const finance = ref({})

const reports = [
	{ id: 'trial_balance', label: 'Trial Balance', href: '/app/query-report/Trial%20Balance' },
	{
		id: 'pnl',
		label: 'Profit and Loss',
		href: '/app/query-report/Profit%20and%20Loss%20Statement',
	},
	{ id: 'cash_flow', label: 'Cash Flow', href: '/app/query-report/Cash%20Flow' },
	{
		id: 'ar_aging',
		label: 'AR Aging',
		href: '/app/query-report/Accounts%20Receivable%20Summary',
	},
	{ id: 'ap_aging', label: 'AP Aging', href: '/app/query-report/Accounts%20Payable%20Summary' },
	{ id: 'gl', label: 'General Ledger', href: '/app/query-report/General%20Ledger' },
	{ id: 'balance_sheet', label: 'Balance Sheet', href: '/app/query-report/Balance%20Sheet' },
	{ id: 'gross_profit', label: 'Gross Profit', href: '/app/query-report/Gross%20Profit' },
	{ id: 'sales_register', label: 'Sales Register', href: '/app/query-report/Sales%20Register' },
	{
		id: 'purchase_register',
		label: 'Purchase Register',
		href: '/app/query-report/Purchase%20Register',
	},
	{ id: 'stock_ledger', label: 'Stock Ledger', href: '/app/query-report/Stock%20Ledger' },
	{
		id: 'financial_report_analyser',
		label: 'Financial Report Analyser',
		href: '/app/financial-report-analyser',
	},
]

async function load() {
	loading.value = true
	try {
		const data = await call('zevar_core.api.finance.get_dashboard_summary', {}).catch(
			() => ({})
		)
		finance.value = data || {}
	} catch (e) {
		console.error('FinanceTab load:', e)
	} finally {
		loading.value = false
	}
}
onMounted(load)

function fmt(n) {
	if (n == null) return '0.00'
	return Number(n).toFixed(2)
}
function goHub() {
	router.push('/reports/all')
}
</script>
