<template>
	<div class="flex gap-4 border-b border-gray-200 dark:border-gray-800 overflow-x-auto no-scrollbar px-6 pt-4">
		<router-link
			v-for="tab in visibleTabs"
			:key="tab.path"
			:to="tab.path"
			class="pb-3 text-sm font-medium whitespace-nowrap transition-colors border-b-2"
			:class="[
				$route.path.startsWith(tab.path)
					? 'border-[#D4AF37] text-[#D4AF37]'
					: 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
			]"
		>
			{{ tab.label }}
		</router-link>
	</div>
</template>

<script setup>
import { computed } from 'vue'
import { useSessionStore } from '@/stores/session.js'

const tabs = [
	{ path: '/reports/executive', label: 'Executive Overview', roles: ['Store Manager', 'Administrator', 'System Manager', 'Accounts Manager', 'Sales Manager', 'HR Manager', 'Sales User', 'Employee'] },
	{ path: '/reports/sales', label: 'Sales Monitor', roles: ['Store Manager', 'Administrator', 'System Manager', 'Accounts Manager', 'Sales Manager', 'HR Manager', 'Sales User', 'Employee'] },
	{ path: '/reports/profit', label: 'Profit Intelligence', roles: ['Administrator', 'System Manager', 'Accounts Manager'] },
	{ path: '/reports/workforce', label: 'Workforce Intelligence', roles: ['Store Manager', 'Administrator', 'System Manager', 'Sales Manager', 'HR Manager'] },
	// End of Day is the daily Z-Report / cash closeout — a full-page report, not an
	// analytics tab. Surfaced here for discoverability; clicking it opens /reports/eod.
	{ path: '/reports/eod', label: 'End of Day', roles: ['Store Manager', 'Administrator', 'System Manager', 'Accounts Manager', 'Sales Manager'] },
]

const visibleTabs = computed(() => {
	const session = useSessionStore()
	const userRoles = session.userRoles || []
	const isSysMan = userRoles.includes('System Manager') || userRoles.includes('Administrator')
	return tabs.filter((t) => {
		if (isSysMan) return true
		return t.roles.some((r) => userRoles.includes(r))
	})
})
</script>
