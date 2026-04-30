/**
 * Audit Store
 *
 * Manages state for the Inventory Auditing system.
 * Handles barcode/RFID scanning sessions, progress tracking,
 * audit history, dashboard KPIs, and policy-driven workflows.
 */

import { defineStore } from 'pinia'
import { createResource } from 'frappe-ui'
import { ref, computed } from 'vue'

export const useAuditStore = defineStore('audit', () => {
	// --- State ---
	const activeSession = ref(null)
	const progress = ref(null)
	const recentScans = ref([])
	const scanFeed = ref([])
	const isScanning = ref(false)
	const scanMode = ref('barcode') // 'barcode' or 'rfid'
	const lastScanResult = ref(null)
	const isPolling = ref(false)
	const dashboard = ref(null)
	const auditPlans = ref([])
	let pollTimer = null

	// --- Computed ---
	const isActive = computed(() => {
		return activeSession.value &&
			['Draft', 'In Progress'].includes(activeSession.value.status)
	})

	const progressPercent = computed(() => {
		if (!progress.value) return 0
		const expected = progress.value.session?.expected_count || 0
		const scanned = progress.value.session?.scanned_count || 0
		if (!expected) return 0
		return Math.min(100, Math.round((scanned / expected) * 100))
	})

	const counts = computed(() => {
		return progress.value?.counts || { matched: 0, unexpected: 0, missing: 0, duplicates: 0 }
	})

	const missingItems = computed(() => progress.value?.missing_items || [])
	const unexpectedItems = computed(() => progress.value?.unexpected_items || [])

	// --- Resources ---
	const startAuditResource = createResource({
		url: 'zevar_core.api.inventory_audit.start_audit',
		onSuccess(data) {
			activeSession.value = {
				name: data.session_name,
				status: 'Draft',
				expected_count: data.expected_count,
				total_value_expected: data.total_value_expected,
				scope: data.scope,
			}
		},
	})

	const submitScanResource = createResource({
		url: 'zevar_core.api.inventory_audit.submit_scan',
		onSuccess(data) {
			lastScanResult.value = data
			if (data.match_status !== 'Duplicate') {
				addToScanFeed(data)
			}
		},
	})

	const batchScanResource = createResource({
		url: 'zevar_core.api.inventory_audit.batch_scan',
		onSuccess(data) {
			lastScanResult.value = { match_status: 'Batch', ...data }
			if (data.results) {
				data.results.forEach(r => addToScanFeed(r))
			}
		},
	})

	const progressResource = createResource({
		url: 'zevar_core.api.inventory_audit.get_audit_progress',
		onSuccess(data) {
			progress.value = data
			recentScans.value = data.recent_scans || []
			if (data.session) {
				activeSession.value = data.session
			}
		},
	})

	const finalizeResource = createResource({
		url: 'zevar_core.api.inventory_audit.finalize_audit',
		onSuccess(data) {
			stopPolling()
			if (activeSession.value) {
				activeSession.value.status = data.status
				activeSession.value.variance_dollar_total = data.variance_dollar_total
			}
		},
	})

	const cancelResource = createResource({
		url: 'zevar_core.api.inventory_audit.cancel_audit',
		onSuccess() {
			stopPolling()
			if (activeSession.value) {
				activeSession.value.status = 'Cancelled'
			}
		},
	})

	const historyResource = createResource({
		url: 'zevar_core.api.inventory_audit.get_audit_history',
		auto: false,
	})

	const exportResource = createResource({
		url: 'zevar_core.api.inventory_audit.export_audit_results',
		onSuccess(data) {
			if (data.file_url) {
				window.open(data.file_url, '_blank')
			}
		},
	})

	const dashboardResource = createResource({
		url: 'zevar_core.api.inventory_audit.get_audit_dashboard',
		onSuccess(data) {
			dashboard.value = data
		},
	})

	const auditPlansResource = createResource({
		url: 'zevar_core.api.inventory_audit.get_audit_plans',
		onSuccess(data) {
			auditPlans.value = data.plans || []
		},
	})

	const approveVarianceResource = createResource({
		url: 'zevar_core.api.inventory_audit.approve_variance',
	})

	// --- Actions ---
	function startAudit(warehouse, notes, scope, auditPlan) {
		return startAuditResource.submit({
			display_case: warehouse,
			store_location: warehouse,
			scope: scope || 'Spot',
			audit_plan: auditPlan || undefined,
		})
	}

	function resumeAudit(sessionName) {
		return progressResource.submit({ session: sessionName }).then(() => {
			startPolling()
		})
	}

	function scanBarcode(code) {
		if (!activeSession.value) return
		return submitScanResource.submit({
			session: activeSession.value.name,
			barcode_or_epc: code,
		})
	}

	function scanBatch(codes) {
		if (!activeSession.value) return
		return batchScanResource.submit({
			session: activeSession.value.name,
			epcs_json: JSON.stringify(codes),
		})
	}

	function refreshProgress() {
		if (!activeSession.value) return
		return progressResource.submit({ session: activeSession.value.name })
	}

	function finalize(twoPersonSignoffBy) {
		if (!activeSession.value) return
		return finalizeResource.submit({
			session: activeSession.value.name,
			two_person_signoff_by: twoPersonSignoffBy || undefined,
		})
	}

	function approveVariance(session, reason) {
		return approveVarianceResource.submit({
			session: session,
			approve_reason: reason,
		})
	}

	function cancel() {
		if (!activeSession.value) return
		return cancelResource.submit({ session: activeSession.value.name })
	}

	function exportResults() {
		if (!activeSession.value) return
		return exportResource.submit({ session: activeSession.value.name })
	}

	function loadHistory(params = {}) {
		return historyResource.submit(params)
	}

	function loadDashboard(store) {
		return dashboardResource.submit({ store: store || undefined })
	}

	function loadAuditPlans(store, status) {
		return auditPlansResource.submit({
			store: store || undefined,
			status: status || 'Scheduled',
		})
	}

	function addToScanFeed(result) {
		scanFeed.value.unshift({
			...result,
			timestamp: new Date().toISOString(),
		})
		if (scanFeed.value.length > 50) {
			scanFeed.value = scanFeed.value.slice(0, 50)
		}
	}

	function clearSession() {
		stopPolling()
		activeSession.value = null
		progress.value = null
		recentScans.value = []
		scanFeed.value = []
		lastScanResult.value = null
		isScanning.value = false
	}

	// --- Polling ---
	function startPolling() {
		if (pollTimer) return
		isPolling.value = true
		pollTimer = setInterval(() => {
			if (isActive.value) {
				refreshProgress()
			} else {
				stopPolling()
			}
		}, 3000)
	}

	function stopPolling() {
		isPolling.value = false
		if (pollTimer) {
			clearInterval(pollTimer)
			pollTimer = null
		}
	}

	return {
		// State
		activeSession,
		progress,
		recentScans,
		scanFeed,
		isScanning,
		scanMode,
		lastScanResult,
		isPolling,
		dashboard,
		auditPlans,

		// Computed
		isActive,
		progressPercent,
		counts,
		missingItems,
		unexpectedItems,

		// Resources (for loading states)
		startAuditResource,
		submitScanResource,
		batchScanResource,
		progressResource,
		finalizeResource,
		cancelResource,
		historyResource,
		exportResource,
		dashboardResource,
		auditPlansResource,
		approveVarianceResource,

		// Actions
		startAudit,
		resumeAudit,
		scanBarcode,
		scanBatch,
		refreshProgress,
		finalize,
		approveVariance,
		cancel,
		exportResults,
		loadHistory,
		loadDashboard,
		loadAuditPlans,
		addToScanFeed,
		clearSession,
		startPolling,
		stopPolling,
	}
})
