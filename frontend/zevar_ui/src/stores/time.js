import { computed, ref, watch } from 'vue'
import { defineStore } from 'pinia'

function ymd(d) {
	const x = new Date(d)
	const m = `${x.getMonth() + 1}`.padStart(2, '0')
	const day = `${x.getDate()}`.padStart(2, '0')
	return `${x.getFullYear()}-${m}-${day}`
}

/**
 * useTimeStore — the single global time-range source for the dashboards.
 *
 * Replaces the per-dashboard chaos (Profit from/to, Repair 7/30/90, hardcoded
 * 'today', AdminMonitor 4/8/24h). A widget that calls useDashboardData with
 * `respectTime: true` refetches whenever this range changes.
 */
export const useTimeStore = defineStore('zevar-time', () => {
	const from = ref(ymd(new Date()))
	const to = ref(ymd(new Date()))
	const granularity = ref('daily') // daily | weekly | monthly
	const compareMode = ref('none') // none | prior_period | yoy | wow
	const presetKind = ref('7d')

	const saved = localStorage.getItem('zevar_report_range_v2')
	if (saved) {
		try {
			const data = JSON.parse(saved)
			const todayStr = ymd(new Date())
			if (data.savedAtDate !== todayStr && data.presetKind !== 'custom') {
				presetKind.value = data.presetKind || 'today'
				granularity.value = data.granularity || 'daily'
				compareMode.value = data.compareMode || 'none'
			} else {
				from.value = data.from || todayStr
				to.value = data.to || todayStr
				granularity.value = data.granularity || 'daily'
				compareMode.value = data.compareMode || 'none'
				presetKind.value = data.presetKind || 'today'
			}
		} catch (e) {
			// ignore
		}
	}

	const range = computed(() => ({ from: from.value, to: to.value, granularity: granularity.value, compareMode: compareMode.value, presetKind: presetKind.value }))

	function save() {
		localStorage.setItem('zevar_report_range_v2', JSON.stringify({
			from: from.value,
			to: to.value,
			granularity: granularity.value,
			compareMode: compareMode.value,
			presetKind: presetKind.value,
			savedAtDate: ymd(new Date())
		}))
	}

	watch([from, to, granularity, compareMode, presetKind], save, { deep: true })

	function setRange(f, t) {
		if (f) from.value = f
		if (t) to.value = t
		presetKind.value = 'custom'
	}

	function setGranularity(g) {
		granularity.value = g
	}

	function setCompare(c) {
		compareMode.value = c
	}

	function quickPreset(preset, updateKind = true) {
		if (updateKind) presetKind.value = preset
		const today = new Date()
		const toStr = ymd(today)
		let fromStr = toStr
		if (preset === 'today') fromStr = toStr
		else if (preset === 'week') {
			const d = new Date(today)
			const day = d.getDay()
			const diff = d.getDate() - day + (day === 0 ? -6 : 1) // adjust when day is sunday
			d.setDate(diff)
			fromStr = ymd(d)
		}
		else if (preset === 'month') {
			fromStr = ymd(new Date(today.getFullYear(), today.getMonth(), 1))
		}
		else if (preset === '7d') fromStr = ymd(new Date(Date.now() - 6 * 86400000))
		else if (preset === '30d') fromStr = ymd(new Date(Date.now() - 29 * 86400000))
		else if (preset === '90d') fromStr = ymd(new Date(Date.now() - 89 * 86400000))
		else if (preset === 'ytd') fromStr = ymd(new Date(today.getFullYear(), 0, 1))
		else if (preset === 'qtd') {
			const q = Math.floor(today.getMonth() / 3)
			fromStr = ymd(new Date(today.getFullYear(), q * 3, 1))
		}
		from.value = fromStr
		to.value = toStr
	}

	if (presetKind.value !== 'custom') {
		quickPreset(presetKind.value, false)
	}

	return { from, to, granularity, compareMode, presetKind, range, setRange, setGranularity, setCompare, quickPreset }
})
