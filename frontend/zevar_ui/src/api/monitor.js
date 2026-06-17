/**
 * Central registry of the Zevar Monitor Suite backend endpoints (Phases 0-4).
 *
 * Use with `useDashboardData(MonitorAPI.salesSummary)` or
 * `createResource({ url: MonitorAPI.teamScorecard })` so there is one place that
 * maps a capability to its dotted frappe method. Add new endpoints here.
 */
export const MonitorAPI = {
	// Command Center (Phase 4) — the role-aware ops wall
	wallState: 'zevar_core.api.command_center.get_wall_state',
	salesTicker: 'zevar_core.api.command_center.get_sales_ticker',
	associateGrid: 'zevar_core.api.command_center.get_associate_grid',
	repairLane: 'zevar_core.api.command_center.get_repair_lane',

	// Sales Monitor (Phase 2)
	salesSummary: 'zevar_core.api.sales_monitor.get_summary',
	salesHourly: 'zevar_core.api.sales_monitor.get_hourly',
	salesLeaderboard: 'zevar_core.api.sales_monitor.get_leaderboard',
	salesBreakdown: 'zevar_core.api.sales_monitor.get_breakdown',
	salesTrend: 'zevar_core.api.sales_monitor.get_trend',
	salesPace: 'zevar_core.api.sales_monitor.get_pace',

	// Workforce Intelligence (Phase 3)
	quotaProgress: 'zevar_core.api.workforce.get_quota_progress',
	projectPayout: 'zevar_core.api.workforce.project_payout',
	teamScorecard: 'zevar_core.api.workforce.get_team_scorecard',
	teamPerformance: 'zevar_core.api.performance.get_team_performance',
	employeeSummary: 'zevar_core.api.performance.get_employee_performance_summary',

	// Profit Intelligence (Phase 1)
	marginWaterfall: 'zevar_core.api.profit_intelligence.get_margin_waterfall',
	simulateWhatIf: 'zevar_core.api.profit_intelligence.simulate_whatif',
	pvmBridge: 'zevar_core.api.profit_intelligence.get_pvm_bridge',
	goldPassThrough: 'zevar_core.api.profit_intelligence.get_gold_pass_through',
	unrealizedGainLoss: 'zevar_core.api.profit_intelligence.get_unrealized_gain_loss',
	marginHeatmap: 'zevar_core.api.profit_intelligence.get_margin_heatmap',
	recommendations: 'zevar_core.api.profit_intelligence.get_recommendations',

	// Live (Q6/Q7)
	commandCenterData: 'zevar_core.api.live_monitor.get_command_center_data',
	repairFeed: 'zevar_core.api.live_monitor.get_repair_live_feed',
}

// Realtime channels (must match zevar_core/api/realtime/events_schema.py CHANNELS).
export const Channels = {
	repairLive: 'repair_live_event',
	anomalyAlert: 'repair_anomaly_alert',
	systemHealth: 'system_health',
	salesTick: 'sales_tick',
	associatePersonal: 'associate_personal',
}
