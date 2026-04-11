/**
 * Session Store
 *
 * Manages user session state, authentication, and warehouse selection.
 */

import { defineStore } from 'pinia'
import { createResource } from 'frappe-ui'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

export const useSessionStore = defineStore('session', () => {
	const router = useRouter()

	// State
	const user = ref(null)
	const isLoggedIn = ref(false)
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

	// Resources
	const userResource = createResource({
		url: 'frappe.auth.get_logged_user',
		auto: true,
		onSuccess(data) {
			// Handle case where server returns just a string (e.g., "Administrator")
			if (typeof data === 'string') {
				user.value = {
					full_name: data,
					email: data,
				}
			} else {
				user.value = data
			}
			isLoggedIn.value = true
		},
		onError() {
			user.value = null
			isLoggedIn.value = false

			// Only redirect if not already on login page
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
			currentWarehouse.value = null
			localStorage.removeItem('active_warehouse')
			window.location.href = '/pos/login'
		},
	})

	// Actions
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

	return {
		user,
		isLoggedIn,
		currentWarehouse,
		currentStoreLocation,
		userResource,
		logoutResource,
		setWarehouse,
		setStoreLocation,
	}
})
