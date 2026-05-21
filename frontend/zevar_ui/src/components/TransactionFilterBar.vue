<template>
	<BaseFilterBar context="transactions">
		<template #filters>
			<!-- Date Range -->
			<div ref="dateDropdownRef" class="relative flex-shrink-0">
				<button
					@click.stop="toggleDropdown('date')"
					:class="
						hasActiveDate
							? 'bg-[#D4AF37]/10 text-[#D4AF37] border-[#D4AF37]/50'
							: 'bg-gray-50 dark:bg-warm-dark-700 text-gray-600 dark:text-gray-300 border-gray-200 dark:border-warm-border hover:border-gray-300 dark:hover:border-white/20'
					"
					class="flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-bold transition-all"
				>
					{{ dateLabel }}
					<svg
						class="w-3 h-3 transition-transform"
						:class="{ 'rotate-180': openDropdown === 'date' }"
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

			<!-- Status -->
			<div ref="statusDropdownRef" class="relative flex-shrink-0">
				<button
					@click.stop="toggleDropdown('status')"
					:class="
						activeFilters.status
							? 'bg-[#D4AF37]/10 text-[#D4AF37] border-[#D4AF37]/50'
							: 'bg-gray-50 dark:bg-warm-dark-700 text-gray-600 dark:text-gray-300 border-gray-200 dark:border-warm-border hover:border-gray-300 dark:hover:border-white/20'
					"
					class="flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-bold transition-all"
				>
					Status
					<svg
						class="w-3 h-3 transition-transform"
						:class="{ 'rotate-180': openDropdown === 'status' }"
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

			<!-- Mode of Payment -->
			<div ref="paymentDropdownRef" class="relative flex-shrink-0">
				<button
					@click.stop="toggleDropdown('payment')"
					:class="
						activeFilters.mode_of_payment
							? 'bg-[#D4AF37]/10 text-[#D4AF37] border-[#D4AF37]/50'
							: 'bg-gray-50 dark:bg-warm-dark-700 text-gray-600 dark:text-gray-300 border-gray-200 dark:border-warm-border hover:border-gray-300 dark:hover:border-white/20'
					"
					class="flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-bold transition-all"
				>
					Payment Mode
					<svg
						class="w-3 h-3 transition-transform"
						:class="{ 'rotate-180': openDropdown === 'payment' }"
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
				<!-- Date Dropdown -->
				<div
					v-if="openDropdown === 'date'"
					ref="dateDropdown"
					class="fixed bg-white dark:bg-warm-card border border-gray-200 dark:border-warm-border rounded-xl shadow-2xl p-2 z-[99999] flex flex-col gap-1 text-gray-700 dark:text-white"
					:style="dropdownStyle.date"
				>
					<button
						v-for="preset in datePresets"
						:key="preset.label"
						@click="applyDatePreset(preset)"
						:class="
							activeFilters.date_preset === preset.label
								? 'bg-[#D4AF37] text-white font-bold'
								: 'hover:bg-gray-100 dark:hover:bg-warm-dark-700 text-gray-500 dark:text-gray-300'
						"
						class="px-3 py-2 text-[11px] rounded-lg text-left transition-colors"
					>
						{{ preset.label }}
					</button>
				</div>

				<!-- Status Dropdown -->
				<div
					v-if="openDropdown === 'status'"
					ref="statusDropdown"
					class="fixed bg-white dark:bg-warm-card border border-gray-200 dark:border-warm-border rounded-xl shadow-2xl p-2 z-[99999] flex flex-col gap-1 text-gray-700 dark:text-white"
					:style="dropdownStyle.status"
				>
					<button
						@click="toggleStatus('')"
						:class="
							!activeFilters.status
								? 'bg-[#D4AF37] text-white font-bold'
								: 'hover:bg-gray-100 dark:hover:bg-warm-dark-700 text-gray-500 dark:text-gray-300'
						"
						class="px-3 py-2 text-[11px] rounded-lg text-left transition-colors"
					>
						All Statuses
					</button>
					<button
						v-for="status in statuses"
						:key="status"
						@click="toggleStatus(status)"
						:class="
							activeFilters.status === status
								? 'bg-[#D4AF37] text-white font-bold'
								: 'hover:bg-gray-100 dark:hover:bg-warm-dark-700 text-gray-500 dark:text-gray-300'
						"
						class="px-3 py-2 text-[11px] rounded-lg text-left transition-colors"
					>
						{{ status }}
					</button>
				</div>

				<!-- Payment Dropdown -->
				<div
					v-if="openDropdown === 'payment'"
					ref="paymentDropdown"
					class="fixed bg-white dark:bg-warm-card border border-gray-200 dark:border-warm-border rounded-xl shadow-2xl p-2 z-[99999] flex flex-col gap-1 text-gray-700 dark:text-white"
					:style="dropdownStyle.payment"
				>
					<button
						@click="togglePaymentMode('')"
						:class="
							!activeFilters.mode_of_payment
								? 'bg-[#D4AF37] text-white font-bold'
								: 'hover:bg-gray-100 dark:hover:bg-warm-dark-700 text-gray-500 dark:text-gray-300'
						"
						class="px-3 py-2 text-[11px] rounded-lg text-left transition-colors"
					>
						All Payments
					</button>
					<button
						v-for="mode in paymentModes"
						:key="mode"
						@click="togglePaymentMode(mode)"
						:class="
							activeFilters.mode_of_payment === mode
								? 'bg-[#D4AF37] text-white font-bold'
								: 'hover:bg-gray-100 dark:hover:bg-warm-dark-700 text-gray-500 dark:text-gray-300'
						"
						class="px-3 py-2 text-[11px] rounded-lg text-left transition-colors"
					>
						{{ mode }}
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

const activeFilters = computed(() => ui.activeFilters.transactions || {})

// Button refs
const dateDropdownRef = ref(null)
const statusDropdownRef = ref(null)
const paymentDropdownRef = ref(null)

// Panel refs (teleported)
const dateDropdown = ref(null)
const statusDropdown = ref(null)
const paymentDropdown = ref(null)

const dropdownStyle = ref({
	date: { display: 'none' },
	status: { display: 'none' },
	payment: { display: 'none' },
})

const datePresets = [
	{ label: 'Today', days: 0 },
	{ label: 'Yesterday', days: 1 },
	{ label: 'Last 7 Days', days: 7 },
	{ label: 'This Month', days: 30 },
	{ label: 'Last 90 Days', days: 90 },
	{ label: 'All Time', days: null },
]

const statuses = ['Paid', 'Unpaid', 'Overdue', 'Cancelled', 'Return']
const paymentModes = ['Cash', 'Credit Card', 'Debit Card', 'Layaway', 'Gift Card']

const hasActiveDate = computed(() => activeFilters.value.date_preset != null)
const dateLabel = computed(() => activeFilters.value.date_preset || 'Date Range')

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
		date: { button: dateDropdownRef, panel: dateDropdown, width: 160 },
		status: { button: statusDropdownRef, panel: statusDropdown, width: 160 },
		payment: { button: paymentDropdownRef, panel: paymentDropdown, width: 160 },
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
		dateDropdownRef,
		statusDropdownRef,
		paymentDropdownRef,
		dateDropdown,
		statusDropdown,
		paymentDropdown,
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

	// G9 Fix: Default to "Today" if no date filter is active on first load
	if (!activeFilters.value.date_preset && !activeFilters.value.from_date) {
		applyDatePreset({ label: 'Today', days: 0 })
	}
})

onUnmounted(() => {
	document.removeEventListener('click', handleGlobalClick)
	window.removeEventListener('scroll', handleScroll, true)
	window.removeEventListener('resize', handleScroll)
})

function applyDatePreset(preset) {
	if (preset.days === null) {
		ui.setFilter('transactions', 'from_date', null)
		ui.setFilter('transactions', 'to_date', null)
		ui.setFilter('transactions', 'date_preset', null)
	} else {
		const to = new Date()
		const from = new Date()
		from.setDate(to.getDate() - preset.days)

		ui.setFilter('transactions', 'from_date', from.toISOString().split('T')[0])
		ui.setFilter('transactions', 'to_date', to.toISOString().split('T')[0])
		ui.setFilter('transactions', 'date_preset', preset.label)
	}
	openDropdown.value = null
}

function toggleStatus(status) {
	if (activeFilters.value.status === status) {
		ui.setFilter('transactions', 'status', null)
	} else {
		ui.setFilter('transactions', 'status', status || null)
	}
	openDropdown.value = null
}

function togglePaymentMode(mode) {
	if (activeFilters.value.mode_of_payment === mode) {
		ui.setFilter('transactions', 'mode_of_payment', null)
	} else {
		ui.setFilter('transactions', 'mode_of_payment', mode || null)
	}
	openDropdown.value = null
}
</script>
