/**
 * Session Store
 *
 * Manages user session state, authentication, warehouse selection,
 * and user roles for role-based dashboard rendering.
 */

import { defineStore } from 'pinia'
import { createResource } from 'frappe-ui'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

export const useSessionStore = defineStore('session', () => {
	const router = useRouter()

	// State
	const user = ref(
		localStorage.getItem('session_user') ? JSON.parse(localStorage.getItem('session_user')) : null
	)
	const isLoggedIn = ref(!!localStorage.getItem('session_user'))
	const userRoles = ref(
		localStorage.getItem('session_roles') ? JSON.parse(localStorage.getItem('session_roles')) : []
	)
	const currentWarehouse = ref(
		localStorage.getItem('active_warehouse') &&
			localStorage.getItem('active_warehouse') !== 'null' &&
			localStorage.getItem('active_warehouse') !== ''
			? localStorage.getItem('active_warehouse')
			: null
	)
	const currentStoreLocation = ref(
		localStorage.getItem('active_store_location') &&
			localStorage.getItem('active_store_location') !== 'null' &&
			localStorage.getItem('active_store_location') !== ''
			? localStorage.getItem('active_store_location')
			: null
	)

	// Computed role checks
	const isAdmin = computed(() => {
		return (
			userRoles.value.includes('System Manager') ||
			userRoles.value.includes('Administrator') ||
			userRoles.value.includes('Store Manager')
		)
	})

	const isManager = computed(() => {
		return (
			userRoles.value.includes('Store Manager') ||
			userRoles.value.includes('System Manager') ||
			userRoles.value.includes('Accounts Manager')
		)
	})

	// Resources
	const userResource = createResource({
		url: 'zevar_core.api.user_info.get_user_info',
		auto: true,
		onSuccess(data) {
			if (!data || data === 'Guest') {
				user.value = null
				isLoggedIn.value = false
				userRoles.value = []
				localStorage.removeItem('session_user')
				localStorage.removeItem('session_roles')
				
				// Only redirect if not already on login page
				if (window.location.pathname !== '/pos/login') {
					router.push('/login')
				}
				return
			}

			user.value = {
				full_name: data.full_name,
				email: data.user,
			}
			userRoles.value = data.roles || []
			isLoggedIn.value = true
			localStorage.setItem('session_user', JSON.stringify(user.value))
			localStorage.setItem('session_roles', JSON.stringify(userRoles.value))
			startActivityTracking()
		},
		onError() {
			user.value = null
			isLoggedIn.value = false
			userRoles.value = []
			localStorage.removeItem('session_user')
			localStorage.removeItem('session_roles')

			if (window.location.pathname !== '/pos/login') {
				router.push('/login')
			}
		},
	})

	const logoutResource = createResource({
		url: 'logout',
		onSuccess() {
			user.value = null
			isLoggedIn.value = false
			userRoles.value = []
			localStorage.removeItem('session_user')
			localStorage.removeItem('session_roles')
			currentWarehouse.value = null
			localStorage.removeItem('active_warehouse')
			stopActivityTracking()
			window.location.href = '/pos/login'
		},
	})

	// Actions
	function hasRole(roleName) {
		return userRoles.value.includes(roleName)
	}

	function hasAnyRole(roleNames) {
		return roleNames.some((r) => userRoles.value.includes(r))
	}

	function setWarehouse(warehouseID) {
		if (!warehouseID || warehouseID === '') {
			currentWarehouse.value = null
			localStorage.removeItem('active_warehouse')
		} else {
			currentWarehouse.value = warehouseID
			localStorage.setItem('active_warehouse', warehouseID)
		}
	}

	function setStoreLocation(storeLocation) {
		if (!storeLocation || storeLocation === '') {
			currentStoreLocation.value = null
			localStorage.removeItem('active_store_location')
		} else {
			currentStoreLocation.value = storeLocation
			localStorage.setItem('active_store_location', storeLocation)
		}
	}

	// Activity tracking for auto logout (4 hours)
	const AUTO_LOGOUT_MS = 4 * 60 * 60 * 1000
	let activityInterval = null

	function updateActivity() {
		localStorage.setItem('last_activity', Date.now().toString())
	}

	function startActivityTracking() {
		if (activityInterval) clearInterval(activityInterval)
		updateActivity()
		
		window.addEventListener('mousemove', updateActivity, { passive: true })
		window.addEventListener('keydown', updateActivity, { passive: true })
		window.addEventListener('click', updateActivity, { passive: true })
		window.addEventListener('scroll', updateActivity, { passive: true })
		
		activityInterval = setInterval(() => {
			const lastActivity = parseInt(localStorage.getItem('last_activity') || '0')
			if (Date.now() - lastActivity > AUTO_LOGOUT_MS && isLoggedIn.value) {
				console.log('Session expired due to inactivity. Logging out.')
				stopActivityTracking()
				logoutResource.submit()
			}
		}, 60 * 1000)
	}

	function stopActivityTracking() {
		if (activityInterval) {
			clearInterval(activityInterval)
			activityInterval = null
		}
		window.removeEventListener('mousemove', updateActivity)
		window.removeEventListener('keydown', updateActivity)
		window.removeEventListener('click', updateActivity)
		window.removeEventListener('scroll', updateActivity)
	}

	if (isLoggedIn.value) {
		startActivityTracking()
	}

	return {
		user,
		isLoggedIn,
		userRoles,
		isAdmin,
		isManager,
		currentWarehouse,
		currentStoreLocation,
		userResource,
		logoutResource,
		hasRole,
		hasAnyRole,
		setWarehouse,
		setStoreLocation,
	}
})
