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

	const createTaskResource = createResource({
		url: 'zevar_core.api.clienteling.create_crm_task_from_pos',
		auto: false,
	})

	const createLeadResource = createResource({
		url: 'zevar_core.api.crm_hooks.create_lead_for_customer',
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

	async function createTask(customerName, title, dueDate, description) {
		if (!customerName || !title?.trim()) return
		try {
			const result = await createTaskResource.submit({
				customer: customerName,
				title: title.trim(),
				due_date: dueDate || null,
				description: description || null,
			})
			await loadIntelligence(customerName)
			return result
		} catch (e) {
			console.error('Create task error:', e)
			throw e
		}
	}

	async function createLead(customerName) {
		if (!customerName) return
		try {
			const result = await createLeadResource.submit({
				customer: customerName,
			})
			await loadIntelligence(customerName)
			return result
		} catch (e) {
			console.error('Create lead error:', e)
			throw e
		}
	}

	// Core data
	const upcomingOccasions = computed(() => customerData.value?.upcoming_occasions || [])
	const hasUrgentOccasion = computed(() =>
		upcomingOccasions.value.some((o) => o.days_until <= 14)
	)
	const profile = computed(() => customerData.value?.profile || null)
	const recentPurchases = computed(() => customerData.value?.recent_purchases || [])
	const pipeline = computed(() => customerData.value?.pipeline || { lead: null, deal: null, tasks: [] })
	const hasCRMLead = computed(() => !!pipeline.value?.lead)
	const hasCRMDeal = computed(() => !!pipeline.value?.deal)
	const openTasks = computed(() => pipeline.value?.tasks || [])

	// Enhanced profile computed properties
	const customerStatus = computed(() => profile.value?.customer_status || 'Regular')
	const lifetimeValue = computed(() => profile.value?.lifetime_value || profile.value?.total_spent || 0)
	const ytdSpend = computed(() => profile.value?.ytd_spend || 0)
	const discountRate = computed(() => profile.value?.discount_rate || 0)
	const totalInvoices = computed(() => profile.value?.visit_count || 0)
	const avgTicket = computed(() => profile.value?.avg_order_value || 0)
	const lastVisit = computed(() => profile.value?.last_purchase_date || null)
	const jewelryPreferences = computed(() => profile.value?.jewelry_preferences || '')

	return {
		customerData,
		loading,
		error,
		loadIntelligence,
		addNote,
		createTask,
		createLead,
		upcomingOccasions,
		hasUrgentOccasion,
		profile,
		recentPurchases,
		pipeline,
		hasCRMLead,
		hasCRMDeal,
		openTasks,
		// Enhanced profile
		customerStatus,
		lifetimeValue,
		ytdSpend,
		discountRate,
		totalInvoices,
		avgTicket,
		lastVisit,
		jewelryPreferences,
	}
}
