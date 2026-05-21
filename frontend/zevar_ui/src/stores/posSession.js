import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const usePosSessionStore = defineStore('posSession', () => {
	const status = ref({ has_active_session: false, session: null })
	const loading = ref(false)
	const error = ref(null)

	const hasActiveSession = computed(() => status.value.has_active_session === true)
	const activeSession = computed(() => status.value.session || null)
	const sessionName = computed(() => status.value.session?.name || '')
	const sessionDuration = computed(() => status.value.session?.duration_hours || 0)

	async function fetchStatus() {
		loading.value = true
		error.value = null
		try {
			const res = await fetch('/api/method/zevar_core.api.pos_session.get_session_status', {
				headers: {
					'X-Frappe-CSRF-Token': window.csrf_token || '',
				},
			})
			if (!res.ok) throw new Error('Failed to fetch session status')
			const data = await res.json()
			status.value = data.message || data
		} catch (err) {
			error.value = err.message
		} finally {
			loading.value = false
		}
	}

	async function suspendSession(reason = '') {
		loading.value = true
		error.value = null
		try {
			const res = await fetch('/api/method/zevar_core.api.pos_session.suspend_session', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'X-Frappe-CSRF-Token': window.csrf_token || '',
				},
				body: JSON.stringify({ session_name: sessionName.value, reason }),
			})
			if (!res.ok) throw new Error('Failed to suspend session')
			const data = await res.json()
			if (data.message?.success) {
				await fetchStatus()
				return true
			} else {
				throw new Error(data.message?.message || 'Failed to suspend session')
			}
		} catch (err) {
			error.value = err.message
			return false
		} finally {
			loading.value = false
		}
	}

	async function resumeSession() {
		loading.value = true
		error.value = null
		try {
			const res = await fetch('/api/method/zevar_core.api.pos_session.resume_session', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'X-Frappe-CSRF-Token': window.csrf_token || '',
				},
				body: JSON.stringify({ session_name: sessionName.value }),
			})
			if (!res.ok) throw new Error('Failed to resume session')
			const data = await res.json()
			if (data.message?.success) {
				await fetchStatus()
				return true
			} else {
				throw new Error(data.message?.message || 'Failed to resume session')
			}
		} catch (err) {
			error.value = err.message
			return false
		} finally {
			loading.value = false
		}
	}

	async function fetchPaymentBreakdown(sessionNameVal = null) {
		loading.value = true
		error.value = null
		try {
			const name = sessionNameVal || sessionName.value
			const res = await fetch(
				`/api/method/zevar_core.api.pos_session.get_session_payment_breakdown?session_name=${name}`,
				{
					headers: {
						'X-Frappe-CSRF-Token': window.csrf_token || '',
					},
				}
			)
			if (!res.ok) throw new Error('Failed to fetch payment breakdown')
			const data = await res.json()
			return data.message || data
		} catch (err) {
			error.value = err.message
			throw err
		} finally {
			loading.value = false
		}
	}

	async function fetchLayawayActivity(sessionNameVal = null) {
		loading.value = true
		error.value = null
		try {
			const name = sessionNameVal || sessionName.value
			const res = await fetch(
				`/api/method/zevar_core.api.pos_session.get_session_layaway_activity?session_name=${name}`,
				{
					headers: {
						'X-Frappe-CSRF-Token': window.csrf_token || '',
					},
				}
			)
			if (!res.ok) throw new Error('Failed to fetch layaway activity')
			const data = await res.json()
			return data.message || data
		} catch (err) {
			error.value = err.message
			throw err
		} finally {
			loading.value = false
		}
	}

	async function fetchRepairActivity(sessionNameVal = null) {
		loading.value = true
		error.value = null
		try {
			const name = sessionNameVal || sessionName.value
			const res = await fetch(
				`/api/method/zevar_core.api.pos_session.get_session_repair_activity?session_name=${name}`,
				{
					headers: {
						'X-Frappe-CSRF-Token': window.csrf_token || '',
					},
				}
			)
			if (!res.ok) throw new Error('Failed to fetch repair activity')
			const data = await res.json()
			return data.message || data
		} catch (err) {
			error.value = err.message
			throw err
		} finally {
			loading.value = false
		}
	}

	async function fetchSales(sessionNameVal = null) {
		loading.value = true
		error.value = null
		try {
			const name = sessionNameVal || sessionName.value
			const res = await fetch(
				`/api/method/zevar_core.api.pos_session.get_session_sales?session_name=${name}`,
				{
					headers: {
						'X-Frappe-CSRF-Token': window.csrf_token || '',
					},
				}
			)
			if (!res.ok) throw new Error('Failed to fetch sales activity')
			const data = await res.json()
			return data.message || data
		} catch (err) {
			error.value = err.message
			throw err
		} finally {
			loading.value = false
		}
	}

	return {
		status,
		loading,
		error,
		hasActiveSession,
		activeSession,
		sessionName,
		sessionDuration,
		fetchStatus,
		suspendSession,
		resumeSession,
		fetchPaymentBreakdown,
		fetchLayawayActivity,
		fetchRepairActivity,
		fetchSales,
	}
})
