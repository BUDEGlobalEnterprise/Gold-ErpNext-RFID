import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { createResource } from 'frappe-ui'

export const useProfitStore = defineStore('profit', () => {
	// Date range
	const dateRange = ref({
		from: null,
		to: null,
	})

	// State
	const loading = ref(false)
	const error = ref(null)

	// Resources
	const profitSummary = createResource({
		url: 'zevar_core.api.profit_intelligence.get_profit_summary',
		onSuccess(data) {
			summary.value = data
		},
	})

	const marginAnalysis = createResource({
		url: 'zevar_core.api.profit_intelligence.get_margin_analysis',
		onSuccess(data) {
			margins.value = data
		},
	})

	const profitTrends = createResource({
		url: 'zevar_core.api.profit_intelligence.get_profit_trends',
		onSuccess(data) {
			trends.value = data
		},
	})

	const costComponentTrends = createResource({
		url: 'zevar_core.api.profit_intelligence.get_cost_component_trends',
		onSuccess(data) {
			costTrends.value = data
		},
	})

	const marginHeatmapResource = createResource({
		url: 'zevar_core.api.profit_intelligence.get_margin_heatmap',
		onSuccess(data) {
			heatmap.value = data
		},
	})

	const recommendationsResource = createResource({
		url: 'zevar_core.api.profit_intelligence.get_recommendations',
		onSuccess(data) {
			recommendations.value = data.recommendations || []
		},
	})

	const reviewRecommendationResource = createResource({
		url: 'zevar_core.api.profit_intelligence.review_recommendation',
	})

	// Data refs
	const summary = ref(null)
	const margins = ref(null)
	const trends = ref(null)
	const costTrends = ref(null)
	const heatmap = ref(null)
	const recommendations = ref([])

	// Computed
	const kpiData = computed(() => {
		if (!summary.value) return {}
		const s = summary.value
		const prev = s.previous_period || {}
		const marginChange = s.avg_margin_pct - (prev.margin_pct || 0)
		return {
			totalRevenue: s.total_revenue || 0,
			totalCost: s.total_cost || 0,
			grossProfit: s.gross_profit || 0,
			avgMargin: s.avg_margin_pct || 0,
			marginChange: marginChange,
			invoiceCount: s.invoice_count || 0,
			costBreakdown: s.cost_breakdown || {},
			prevRevenue: prev.total_revenue || 0,
			prevProfit: prev.gross_profit || 0,
		}
	})

	// Actions
	function loadAll(from, to) {
		if (from) dateRange.value.from = from
		if (to) dateRange.value.to = to

		const params = {
			from_date: dateRange.value.from,
			to_date: dateRange.value.to,
		}

		loading.value = true
		error.value = null

		Promise.all([
			profitSummary.fetch(params),
			marginAnalysis.fetch({ ...params, group_by: 'jewelry_type' }),
			trends.value === null ? profitTrends.fetch({ period: 'monthly', months: 12 }) : Promise.resolve(),
			costComponentTrends.fetch({ ...params, granularity: 'weekly' }),
			marginHeatmapResource.fetch(params),
			recommendationsResource.fetch({ status: 'Pending Review', limit: 20 }),
		])
			.catch((err) => {
				error.value = err?.message || 'Failed to load profit data'
			})
			.finally(() => {
				loading.value = false
			})
	}

	function loadRecommendations(status = 'Pending Review') {
		recommendationsResource.fetch({ status, limit: 50 })
	}

	async function reviewRecommendation(name, action, notes = '') {
		try {
			await reviewRecommendationResource.submit({ recommendation: name, action, notes })
			loadRecommendations()
			return true
		} catch (err) {
			error.value = err?.message || 'Failed to review recommendation'
			return false
		}
	}

	return {
		dateRange,
		loading,
		error,
		summary,
		margins,
		trends,
		costTrends,
		heatmap,
		recommendations,
		kpiData,
		loadAll,
		loadRecommendations,
		reviewRecommendation,
		profitSummary,
		marginAnalysis,
		profitTrends,
		costComponentTrends,
		marginHeatmapResource,
		recommendationsResource,
		reviewRecommendationResource,
	}
})
