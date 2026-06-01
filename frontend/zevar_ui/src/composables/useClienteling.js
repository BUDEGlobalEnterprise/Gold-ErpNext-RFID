import { ref, computed } from 'vue'
import { createResource } from 'frappe-ui'

export function useClienteling() {
	const customerData = ref(null)
	const loading = ref(false)
	const error = ref(null)

	const intelligenceResource = createResource({
		url: 'zevar_core.api.clienteling.get_customer_intelligence',
		auto: false,
	})

	const addNoteResource = createResource({
		url: 'zevar_core.api.clienteling.add_customer_note',
		auto: false,
	})

	async function loadIntelligence(customerName) {
		if (!customerName) return
		loading.value = true
		error.value = null
		try {
			const result = await intelligenceResource.submit({ customer: customerName })
			customerData.value = result
		} catch (e) {
			error.value = e.message || 'Failed to load customer data'
			console.error('Clienteling load error:', e)
		} finally {
			loading.value = false
		}
	}

	async function addNote(customerName, noteText) {
		if (!customerName || !noteText?.trim()) return
		try {
			const result = await addNoteResource.submit({
				customer: customerName,
				note: noteText.trim(),
			})
			if (customerData.value) {
				customerData.value.notes = result.notes
			}
			return result
		} catch (e) {
			console.error('Add note error:', e)
			throw e
		}
	}

	const upcomingOccasions = computed(() => customerData.value?.upcoming_occasions || [])
	const hasUrgentOccasion = computed(() =>
		upcomingOccasions.value.some((o) => o.days_until <= 14),
	)
	const profile = computed(() => customerData.value?.profile || null)
	const recentPurchases = computed(() => customerData.value?.recent_purchases || [])

	return {
		customerData,
		loading,
		error,
		loadIntelligence,
		addNote,
		upcomingOccasions,
		hasUrgentOccasion,
		profile,
		recentPurchases,
	}
}
