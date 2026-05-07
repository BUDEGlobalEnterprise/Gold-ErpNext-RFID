import { defineStore } from 'pinia'
import { createResource } from 'frappe-ui'
import { ref } from 'vue'

export const useSettingsStore = defineStore('settings', () => {
	const settings = ref(null)
	const loading = ref(false)

	const settingsResource = createResource({
		url: 'zevar_core.api.settings.get_settings',
		onSuccess(data) {
			settings.value = data
		},
	})

	const posProfileResource = createResource({
		url: 'zevar_core.api.settings.get_pos_profile',
		auto: false,
	})

	const createPosProfileResource = createResource({
		url: 'zevar_core.api.settings.create_pos_profile',
	})

	const updatePosProfileResource = createResource({
		url: 'zevar_core.api.settings.update_pos_profile',
	})

	const deletePosProfileResource = createResource({
		url: 'zevar_core.api.settings.delete_pos_profile',
	})

	const usersResource = createResource({
		url: 'zevar_core.api.settings.get_users_with_roles',
		auto: false,
	})

	const createUserResource = createResource({
		url: 'zevar_core.api.settings.create_user',
	})

	const updateUserRolesResource = createResource({
		url: 'zevar_core.api.settings.update_user_roles',
	})

	const printFormatsResource = createResource({
		url: 'zevar_core.api.settings.get_print_formats',
		auto: false,
	})

	const companySettingsResource = createResource({
		url: 'zevar_core.api.settings.get_company_settings',
		auto: false,
	})

	const systemInfoResource = createResource({
		url: 'zevar_core.api.settings.get_system_info',
		auto: false,
	})

	function loadSettings() {
		loading.value = true
		return settingsResource.submit().finally(() => {
			loading.value = false
		})
	}

	function loadPosProfile(name) {
		return posProfileResource.submit({ name })
	}

	function createPosProfile(data) {
		return createPosProfileResource.submit(data)
	}

	function updatePosProfile(name, data) {
		return updatePosProfileResource.submit({ name, ...data })
	}

	function deletePosProfile(name) {
		return deletePosProfileResource.submit({ name })
	}

	function loadUsers(page = 1) {
		return usersResource.submit({ page, page_size: 50 })
	}

	function createUser(data) {
		return createUserResource.submit(data)
	}

	function updateUserRoles(userEmail, roles) {
		return updateUserRolesResource.submit({
			user_email: userEmail,
			roles_json: JSON.stringify(roles),
		})
	}

	function loadPrintFormats(doctype) {
		return printFormatsResource.submit({ doctype })
	}

	function loadCompanySettings() {
		return companySettingsResource.submit()
	}

	function loadSystemInfo() {
		return systemInfoResource.submit()
	}

	return {
		settings,
		loading,
		settingsResource,
		posProfileResource,
		createPosProfileResource,
		updatePosProfileResource,
		deletePosProfileResource,
		usersResource,
		createUserResource,
		updateUserRolesResource,
		printFormatsResource,
		companySettingsResource,
		systemInfoResource,
		loadSettings,
		loadPosProfile,
		createPosProfile,
		updatePosProfile,
		deletePosProfile,
		loadUsers,
		createUser,
		updateUserRoles,
		loadPrintFormats,
		loadCompanySettings,
		loadSystemInfo,
	}
})
