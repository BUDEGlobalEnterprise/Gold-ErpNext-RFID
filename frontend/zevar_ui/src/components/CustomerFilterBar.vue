<template>
	<BaseFilterBar context="customers">
		<template #filters>
			<!-- Group -->
			<div ref="groupDropdownRef" class="relative flex-shrink-0">
				<button
					@click.stop="toggleDropdown('group')"
					:class="
						activeFilters.customer_group
							? 'bg-[#D4AF37]/10 text-[#D4AF37] border-[#D4AF37]/50'
							: 'bg-gray-50 dark:bg-warm-dark-700 text-gray-600 dark:text-gray-300 border-gray-200 dark:border-warm-border hover:border-gray-300 dark:hover:border-white/20'
					"
					class="flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-bold transition-all"
				>
					Group
					<svg
						class="w-3 h-3 transition-transform"
						:class="{ 'rotate-180': openDropdown === 'group' }"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M19 9l-7 7-7-7"
						/>
					</svg>
				</button>
			</div>

			<!-- Territory -->
			<div ref="territoryDropdownRef" class="relative flex-shrink-0">
				<button
					@click.stop="toggleDropdown('territory')"
					:class="
						activeFilters.territory
							? 'bg-[#D4AF37]/10 text-[#D4AF37] border-[#D4AF37]/50'
							: 'bg-gray-50 dark:bg-warm-dark-700 text-gray-600 dark:text-gray-300 border-gray-200 dark:border-warm-border hover:border-gray-300 dark:hover:border-white/20'
					"
					class="flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-bold transition-all"
				>
					Territory
					<svg
						class="w-3 h-3 transition-transform"
						:class="{ 'rotate-180': openDropdown === 'territory' }"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M19 9l-7 7-7-7"
						/>
					</svg>
				</button>
			</div>

			<!-- Activity -->
			<div ref="activityDropdownRef" class="relative flex-shrink-0">
				<button
					@click.stop="toggleDropdown('activity')"
					:class="
						activeFilters.activity
							? 'bg-[#D4AF37]/10 text-[#D4AF37] border-[#D4AF37]/50'
							: 'bg-gray-50 dark:bg-warm-dark-700 text-gray-600 dark:text-gray-300 border-gray-200 dark:border-warm-border hover:border-gray-300 dark:hover:border-white/20'
					"
					class="flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-bold transition-all"
				>
					Activity
					<svg
						class="w-3 h-3 transition-transform"
						:class="{ 'rotate-180': openDropdown === 'activity' }"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M19 9l-7 7-7-7"
						/>
					</svg>
				</button>
			</div>
		</template>

		<template #dropdowns>
			<Teleport to="body">
				<!-- Group Dropdown -->
				<div
					v-if="openDropdown === 'group'"
					ref="groupDropdown"
					class="fixed bg-white dark:bg-warm-card border border-gray-200 dark:border-warm-border rounded-xl shadow-2xl p-2 z-[99999] flex flex-col gap-1 text-gray-700 dark:text-white"
					:style="dropdownStyle.group"
				>
					<button
						@click="toggleFilter('customer_group', '')"
						:class="
							!activeFilters.customer_group
								? 'bg-[#D4AF37] text-white font-bold'
								: 'hover:bg-gray-100 dark:hover:bg-warm-dark-700 text-gray-500 dark:text-gray-300'
						"
						class="px-3 py-2 text-[11px] rounded-lg text-left transition-colors"
					>
						All Groups
					</button>
					<button
						v-for="group in groups"
						:key="group"
						@click="toggleFilter('customer_group', group)"
						:class="
							activeFilters.customer_group === group
								? 'bg-[#D4AF37] text-white font-bold'
								: 'hover:bg-gray-100 dark:hover:bg-warm-dark-700 text-gray-500 dark:text-gray-300'
						"
						class="px-3 py-2 text-[11px] rounded-lg text-left transition-colors"
					>
						{{ group }}
					</button>
				</div>

				<!-- Territory Dropdown -->
				<div
					v-if="openDropdown === 'territory'"
					ref="territoryDropdown"
					class="fixed bg-white dark:bg-warm-card border border-gray-200 dark:border-warm-border rounded-xl shadow-2xl p-2 z-[99999] flex flex-col gap-1 text-gray-700 dark:text-white"
					:style="dropdownStyle.territory"
				>
					<button
						@click="toggleFilter('territory', '')"
						:class="
							!activeFilters.territory
								? 'bg-[#D4AF37] text-white font-bold'
								: 'hover:bg-gray-100 dark:hover:bg-warm-dark-700 text-gray-500 dark:text-gray-300'
						"
						class="px-3 py-2 text-[11px] rounded-lg text-left transition-colors"
					>
						All Territories
					</button>
					<button
						v-for="t in territories"
						:key="t"
						@click="toggleFilter('territory', t)"
						:class="
							activeFilters.territory === t
								? 'bg-[#D4AF37] text-white font-bold'
								: 'hover:bg-gray-100 dark:hover:bg-warm-dark-700 text-gray-500 dark:text-gray-300'
						"
						class="px-3 py-2 text-[11px] rounded-lg text-left transition-colors"
					>
						{{ t }}
					</button>
				</div>

				<!-- Activity Dropdown -->
				<div
					v-if="openDropdown === 'activity'"
					ref="activityDropdown"
					class="fixed bg-white dark:bg-warm-card border border-gray-200 dark:border-warm-border rounded-xl shadow-2xl p-2 z-[99999] flex flex-col gap-1 text-gray-700 dark:text-white"
					:style="dropdownStyle.activity"
				>
					<button
						@click="toggleFilter('activity', '')"
						:class="
							!activeFilters.activity
								? 'bg-[#D4AF37] text-white font-bold'
								: 'hover:bg-gray-100 dark:hover:bg-warm-dark-700 text-gray-500 dark:text-gray-300'
						"
						class="px-3 py-2 text-[11px] rounded-lg text-left transition-colors"
					>
						Any Activity
					</button>
					<button
						v-for="a in activities"
						:key="a.label"
						@click="toggleFilter('activity', a.label)"
						:class="
							activeFilters.activity === a.label
								? 'bg-[#D4AF37] text-white font-bold'
								: 'hover:bg-gray-100 dark:hover:bg-warm-dark-700 text-gray-500 dark:text-gray-300'
						"
						class="px-3 py-2 text-[11px] rounded-lg text-left transition-colors"
					>
						{{ a.label }}
					</button>
				</div>
			</Teleport>
		</template>
	</BaseFilterBar>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, nextTick } from 'vue'
import { useUIStore } from '@/stores/ui.js'
import BaseFilterBar from './BaseFilterBar.vue'

const ui = useUIStore()
const openDropdown = ref(null)

const activeFilters = computed(() => ui.activeFilters.customers || {})

// Button refs
const groupDropdownRef = ref(null)
const territoryDropdownRef = ref(null)
const activityDropdownRef = ref(null)

// Panel refs (teleported)
const groupDropdown = ref(null)
const territoryDropdown = ref(null)
const activityDropdown = ref(null)

const dropdownStyle = ref({
	group: { display: 'none' },
	territory: { display: 'none' },
	activity: { display: 'none' },
})

const groups = ['Individual', 'VIP', 'Corporate', 'Government']
const territories = ['North America', 'Europe', 'Asia', 'Middle East', 'Australia']
const activities = [
	{ label: 'Recently Joined', value: 'recent' },
	{ label: 'High Value (VIP)', value: 'vip' },
	{ label: 'Inactive (90+ Days)', value: 'inactive' },
]

function toggleDropdown(key) {
	if (openDropdown.value === key) {
		openDropdown.value = null
	} else {
		openDropdown.value = key
		nextTick(() => {
			updateDropdownPosition(key)
		})
	}
}

function updateDropdownPosition(key) {
	const refs = {
		group: { button: groupDropdownRef, panel: groupDropdown, width: 160 },
		territory: { button: territoryDropdownRef, panel: territoryDropdown, width: 180 },
		activity: { button: activityDropdownRef, panel: activityDropdown, width: 160 },
	}

	const ref = refs[key]
	if (!ref || !ref.button.value || !ref.panel.value) return

	const buttonRect = ref.button.value.getBoundingClientRect()

	// Prevent horizontal overflow on smaller screens
	let left = buttonRect.left
	if (left + ref.width > window.innerWidth) {
		left = Math.max(8, buttonRect.right - ref.width)
	}

	dropdownStyle.value[key] = {
		top: `${buttonRect.bottom + 8}px`,
		left: `${left}px`,
		width: `${ref.width}px`,
		maxWidth: 'calc(100vw - 16px)',
		display: 'block',
	}
}

function closeAllDropdowns() {
	openDropdown.value = null
}

function handleGlobalClick(event) {
	const allRefs = [
		groupDropdownRef,
		territoryDropdownRef,
		activityDropdownRef,
		groupDropdown,
		territoryDropdown,
		activityDropdown,
	]

	const clickedInside = allRefs.some((ref) => {
		return ref.value && ref.value.contains(event.target)
	})

	if (!clickedInside) {
		closeAllDropdowns()
	}
}

function handleScroll() {
	if (openDropdown.value) {
		updateDropdownPosition(openDropdown.value)
	}
}

onMounted(() => {
	document.addEventListener('click', handleGlobalClick)
	window.addEventListener('scroll', handleScroll, true)
	window.addEventListener('resize', handleScroll)
})

onUnmounted(() => {
	document.removeEventListener('click', handleGlobalClick)
	window.removeEventListener('scroll', handleScroll, true)
	window.removeEventListener('resize', handleScroll)
})

function toggleFilter(key, value) {
	if (activeFilters.value[key] === value) {
		ui.setFilter('customers', key, null)
	} else {
		ui.setFilter('customers', key, value || null)
	}
	openDropdown.value = null
}
</script>
