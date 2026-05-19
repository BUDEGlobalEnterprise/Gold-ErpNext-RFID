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

	return {
		status,
		loading,
		error,
		hasActiveSession,
		activeSession,
		sessionName,
		sessionDuration,
		fetchStatus,
	}
})
