<template>
	<Transition name="slide-down">
		<div
			v-if="show"
			class="mb-5 p-4 bg-gradient-to-r from-[#D4AF37]/10 to-[#D4AF37]/5 border border-[#D4AF37]/30 rounded-xl"
		>
			<div class="flex items-center justify-between mb-3">
				<h4 class="text-sm font-bold text-gray-900 dark:text-white flex items-center gap-2">
					<svg class="w-4 h-4 text-[#D4AF37]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
					</svg>
					ID Document Scanner
				</h4>
				<button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
					</svg>
				</button>
			</div>
			<div class="grid grid-cols-2 gap-3">
				<div>
					<label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">ID Type</label>
					<select
						v-model="modelValue.type"
						class="w-full px-3 py-2 text-sm bg-white dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg focus:ring-2 focus:ring-[#D4AF37]"
					>
						<option value="">Select Type</option>
						<option value="drivers_license">Driver's License</option>
						<option value="passport">Passport</option>
						<option value="national_id">National ID</option>
						<option value="state_id">State ID</option>
					</select>
				</div>
				<div>
					<label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">ID Number</label>
					<input
						v-model="modelValue.number"
						type="text"
						placeholder="Scan or enter ID number"
						class="w-full px-3 py-2 text-sm bg-white dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg focus:ring-2 focus:ring-[#D4AF37]"
					/>
				</div>
			</div>
			<div class="mt-3 flex gap-2">
				<button
					@click="simulateIdScan"
					class="flex-1 px-3 py-2 text-xs font-medium bg-[#D4AF37] text-black rounded-lg hover:bg-[#c9a432] transition flex items-center justify-center gap-1.5"
				>
					<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
					</svg>
					Scan Document
				</button>
				<button
					@click="$emit('apply-data')"
					:disabled="!modelValue.number"
					class="flex-1 px-3 py-2 text-xs font-medium bg-gray-900 dark:bg-warm-dark-800 text-white rounded-lg hover:bg-gray-800 disabled:opacity-50 transition"
				>
					Apply Data
				</button>
			</div>
		</div>
	</Transition>
</template>

<script setup>
defineProps({
	show: {
		type: Boolean,
		required: true
	}
})

const modelValue = defineModel({
	type: Object,
	default: () => ({ type: '', number: '', name: '', address: '', dob: '' })
})

defineEmits(['close', 'apply-data'])

function simulateIdScan() {
	const mockData = {
		drivers_license: {
			name: 'John Doe',
			address: '123 Main St, Springfield, IL 62701',
			number: 'D123456789',
			dob: '1990-01-15',
		},
		passport: {
			name: 'Jane Smith',
			address: '456 Oak Ave, Chicago, IL 60601',
			number: 'P987654321',
			dob: '1985-05-20',
		},
	}

	const data = mockData[modelValue.value.type] || mockData.drivers_license
	modelValue.value.number = data.number
	modelValue.value.name = data.name
	modelValue.value.address = data.address
	modelValue.value.dob = data.dob
}
</script>
