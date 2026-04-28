/**
 * Audit Store
 *
 * Manages state for the Rapid Inventory Auditing system.
 * Handles barcode/RFID scanning sessions, progress tracking,
 * and audit history.
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

	// --- Actions ---
	function startAudit(warehouse, notes) {
		return startAuditResource.submit({ store_location: warehouse, notes })
	}

	function resumeAudit(sessionName) {
		return progressResource.submit({ session_name: sessionName }).then(() => {
			startPolling()
		})
	}

	function scanBarcode(code) {
		if (!activeSession.value) return
		return submitScanResource.submit({
			session_name: activeSession.value.name,
			barcode_or_epc: code,
		})
	}

	function scanBatch(codes) {
		if (!activeSession.value) return
		return batchScanResource.submit({
			session_name: activeSession.value.name,
			barcodes_or_epcs: JSON.stringify(codes),
		})
	}

	function refreshProgress() {
		if (!activeSession.value) return
		return progressResource.submit({ session_name: activeSession.value.name })
	}

	function finalize() {
		if (!activeSession.value) return
		return finalizeResource.submit({ session_name: activeSession.value.name })
	}

	function cancel() {
		if (!activeSession.value) return
		return cancelResource.submit({ session_name: activeSession.value.name })
	}

	function exportResults() {
		if (!activeSession.value) return
		return exportResource.submit({ session_name: activeSession.value.name })
	}

	function loadHistory(params = {}) {
		return historyResource.submit(params)
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

		// Actions
		startAudit,
		resumeAudit,
		scanBarcode,
		scanBatch,
		refreshProgress,
		finalize,
		cancel,
		exportResults,
		loadHistory,
		addToScanFeed,
		clearSession,
		startPolling,
		stopPolling,
	}
})
