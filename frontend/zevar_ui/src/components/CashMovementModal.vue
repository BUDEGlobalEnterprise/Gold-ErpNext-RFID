<template>
	<BaseModal :show="true" max-width="max-w-md" :show-close="true" @close="$emit('close')">
		<div class="p-6">
			<div class="flex items-center gap-3 mb-6">
				<div class="w-10 h-10 rounded-full bg-amber-500/10 flex items-center justify-center">
					<svg class="w-5 h-5 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"></path>
					</svg>
				</div>
				<div>
					<h3 class="text-lg font-bold text-gray-900 dark:text-white">Cash In / Out</h3>
					<p class="text-xs text-gray-500 dark:text-gray-400">Record a cash movement</p>
				</div>
			</div>

			<!-- Recent movements -->
			<div v-if="movements.length > 0" class="mb-5 max-h-32 overflow-y-auto custom-scrollbar">
				<div
					v-for="m in movements"
					:key="m.name"
					class="flex items-center justify-between py-1.5 text-xs border-b border-gray-100 dark:border-white/5 last:border-0"
				>
					<span
						:class="m.movement_type === 'Cash In' ? 'text-green-500' : 'text-red-400'"
					>
						{{ m.movement_type === 'Cash In' ? '+' : '-' }}${{ Number(m.amount).toFixed(2) }}
					</span>
					<span class="text-gray-400 dark:text-gray-500 truncate max-w-[140px]">{{ m.reason }}</span>
				</div>
			</div>

			<div class="space-y-4">
				<!-- Movement type toggle -->
				<div class="flex rounded-lg border border-gray-200 dark:border-white/10 overflow-hidden">
					<button
						@click="form.movement_type = 'Cash In'"
						class="flex-1 py-2 text-sm font-bold transition"
						:class="form.movement_type === 'Cash In'
							? 'bg-green-500/10 text-green-600 dark:text-green-400'
							: 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300'"
					>
						Cash In
					</button>
					<button
						@click="form.movement_type = 'Cash Out'"
						class="flex-1 py-2 text-sm font-bold transition border-l border-gray-200 dark:border-white/10"
						:class="form.movement_type === 'Cash Out'
							? 'bg-red-500/10 text-red-500'
							: 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300'"
					>
						Cash Out
					</button>
				</div>

				<!-- Amount -->
				<div>
					<label class="block text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">Amount</label>
					<div class="relative">
						<span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 font-bold">$</span>
						<input
							v-model.number="form.amount"
							type="number"
							min="0.01"
							step="0.01"
							placeholder="0.00"
							class="w-full pl-7 pr-4 py-2.5 rounded-lg border border-gray-200 dark:border-white/10 bg-white dark:bg-white/5 text-gray-900 dark:text-white text-lg font-bold focus:outline-none focus:ring-2 focus:ring-amber-500/50"
						/>
					</div>
				</div>

				<!-- Reason -->
				<div>
					<label class="block text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">Reason</label>
					<select
						v-model="form.reason"
						class="w-full px-3 py-2.5 rounded-lg border border-gray-200 dark:border-white/10 bg-white dark:bg-white/5 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-amber-500/50"
					>
						<option value="" disabled>Select reason...</option>
						<option v-for="r in reasons" :key="r" :value="r">{{ r }}</option>
					</select>
				</div>

				<!-- Notes -->
				<div>
					<label class="block text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1.5">Notes (optional)</label>
					<input
						v-model="form.notes"
						type="text"
						placeholder="Add details..."
						class="w-full px-3 py-2.5 rounded-lg border border-gray-200 dark:border-white/10 bg-white dark:bg-white/5 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-amber-500/50"
					/>
				</div>

				<!-- Manager PIN (for cash out over $100) -->
				<div v-if="form.movement_type === 'Cash Out' && form.amount > 100">
					<label class="block text-xs font-bold text-amber-500 uppercase tracking-wider mb-1.5">Manager PIN Required</label>
					<input
						v-model="form.manager_pin"
						type="password"
						maxlength="6"
						placeholder="Enter manager PIN"
						class="w-full px-3 py-2.5 rounded-lg border border-amber-500/30 bg-amber-500/5 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-amber-500/50"
					/>
				</div>

				<!-- Error -->
				<p v-if="error" class="text-red-500 text-xs font-medium">{{ error }}</p>

				<!-- Submit -->
				<button
					@click="submit"
					:disabled="submitting || !form.amount || !form.reason"
					class="w-full py-2.5 rounded-lg font-bold text-sm transition disabled:opacity-40"
					:class="form.movement_type === 'Cash In'
						? 'bg-green-600 hover:bg-green-700 text-white'
						: 'bg-red-500 hover:bg-red-600 text-white'"
				>
					{{ submitting ? 'Recording...' : `Record ${form.movement_type}` }}
				</button>
			</div>
		</div>
	</BaseModal>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import BaseModal from '@/components/BaseModal.vue'

const props = defineProps({
	sessionName: { type: String, required: true },
})

const emit = defineEmits(['close', 'recorded'])

const form = ref({
	movement_type: 'Cash In',
	amount: null,
	reason: '',
	notes: '',
	manager_pin: '',
})

const movements = ref([])
const error = ref('')
const submitting = ref(false)

const reasons = [
	'Bank Drop',
	'Change Order',
	'Petty Cash',
	'Owner Withdrawal',
	'Safe Deposit',
	'Other',
]

async function loadMovements() {
	try {
		const res = await fetch('/api/method/zevar_core.api.pos_session.get_cash_movements', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-Frappe-CSRF-Token': window.csrf_token || '',
			},
			body: JSON.stringify({ session_name: props.sessionName }),
		})
		const data = await res.json()
		if (data.message) {
			movements.value = (data.message.movements || []).slice(-5).reverse()
		}
	} catch (e) {
		// non-critical
	}
}

async function submit() {
	error.value = ''
	if (!form.value.amount || form.value.amount <= 0) {
		error.value = 'Enter a valid amount'
		return
	}
	if (!form.value.reason) {
		error.value = 'Select a reason'
		return
	}

	// Check manager PIN requirement before API call
	if (form.value.movement_type === 'Cash Out' && form.value.amount > 100) {
		if (!form.value.manager_pin || form.value.manager_pin.length < 4) {
			error.value = 'Manager PIN required for cash out over $100'
			return
		}
	}

	submitting.value = true
	try {
		const res = await fetch('/api/method/zevar_core.api.pos_session.record_cash_movement', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-Frappe-CSRF-Token': window.csrf_token || '',
			},
			body: JSON.stringify({
				session_name: props.sessionName,
				movement_type: form.value.movement_type,
				amount: form.value.amount,
				reason: form.value.reason,
				notes: form.value.notes || undefined,
				manager_pin: form.value.manager_pin || undefined,
			}),
		})
		const data = await res.json()
		if (data.message?.success) {
			emit('recorded')
		} else {
			error.value = data.message?.message || data.exc_type || 'Failed to record movement'
		}
	} catch (e) {
		error.value = 'Network error'
	} finally {
		submitting.value = false
	}
}

onMounted(() => {
	loadMovements()
})
</script>
