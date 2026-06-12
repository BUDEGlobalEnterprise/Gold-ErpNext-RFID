<template>
	<form @submit.prevent="$emit('submit')" class="space-y-4">
		<!-- Customer Section -->
		<div class="bg-gray-50 dark:bg-warm-dark-900 rounded-lg p-4">
			<div class="flex items-center justify-between mb-2">
				<label class="block text-sm font-medium">Customer *</label>
				<button
					type="button"
					@click="$emit('toggle-new-customer')"
					class="text-xs px-2 py-1 bg-[#D4AF37] text-black rounded hover:bg-[#c9a432] flex items-center gap-1"
				>
					<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 4v16m8-8H4"
						/>
					</svg>
					{{ showNewCustomer ? 'Cancel' : 'New Customer' }}
				</button>
			</div>

			<!-- Inline New Customer Form -->
			<div
				v-if="showNewCustomer"
				class="mb-3 p-3 bg-white dark:bg-warm-dark-900 rounded-lg border border-[#D4AF37]/30 space-y-3"
			>
				<div class="grid grid-cols-2 gap-3">
					<div>
						<label class="block text-xs font-medium mb-1">Full Name *</label>
						<input
							v-model="newCustomerForm.customer_name"
							type="text"
							placeholder="Customer full name"
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						/>
					</div>
					<div>
						<label class="block text-xs font-medium mb-1">Phone *</label>
						<input
							v-model="newCustomerForm.phone"
							type="tel"
							placeholder="(555) 123-4567"
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						/>
					</div>
				</div>
				<div>
					<label class="block text-xs font-medium mb-1">Email</label>
					<input
						v-model="newCustomerForm.email"
						type="email"
						placeholder="customer@example.com"
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
					/>
				</div>
				<div>
					<label class="block text-xs font-medium mb-1">Address</label>
					<input
						v-model="newCustomerForm.address"
						type="text"
						placeholder="Street, City, State, ZIP"
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
					/>
				</div>
				<div class="flex justify-end">
					<button
						type="button"
						@click="$emit('create-customer')"
						:disabled="newCustomerSubmitting"
						class="px-4 py-1.5 bg-[#D4AF37] text-black rounded-lg text-sm font-bold hover:bg-[#c9a432] disabled:opacity-50"
					>
						{{ newCustomerSubmitting ? 'Creating...' : 'Create & Select' }}
					</button>
				</div>
			</div>

			<!-- Customer Search -->
			<div class="relative">
				<input
					:value="customerSearch"
					@input="$emit('update:customer-search', $event.target.value) $emit('search-customers')"
					type="text"
					placeholder="Search customer by name or phone..."
					class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
				/>
				<div
					v-if="customerResults.length > 0"
					class="absolute z-10 w-full mt-1 bg-white dark:bg-warm-dark-900 border rounded-lg shadow-lg max-h-48 overflow-y-auto"
				>
					<button
						v-for="c in customerResults"
						:key="c.name"
						type="button"
						@click="$emit('select-customer', c)"
						class="w-full px-3 py-2 text-left text-sm hover:bg-gray-50 dark:hover:bg-warm-dark-800 border-b last:border-0 flex justify-between"
					>
						<span>{{ c.customer_name }}</span>
						<span class="text-gray-400 text-xs">{{ c.phone || c.mobile || '' }}</span>
					</button>
				</div>
			</div>
			<p v-if="form.customer" class="mt-2 text-xs text-green-600 flex items-center gap-2">
				<span>Selected: {{ form.customer_name }}</span>
				<button
					v-if="customerRepairHistory.length > 0"
					type="button"
					@click="$emit('toggle-history')"
					class="text-blue-600 hover:underline"
				>
					{{ showHistory ? 'Hide' : 'View' }} History ({{
						customerRepairHistory.length
					}})
				</button>
			</p>

			<!-- Customer Repair History -->
			<div
				v-if="showHistory && customerRepairHistory.length > 0"
				class="mt-3 p-2 bg-white dark:bg-warm-dark-900 rounded text-xs"
			>
				<p class="font-medium text-gray-700 mb-2">Previous Repairs</p>
				<div class="space-y-1 max-h-24 overflow-y-auto">
					<div
						v-for="h in customerRepairHistory"
						:key="h.name"
						class="flex justify-between text-gray-600"
					>
						<span>{{ h.repair_type_name }}</span>
						<span>{{ h.creation?.split(' ')[0] }} - {{ h.status }}</span>
					</div>
				</div>
			</div>
		</div>

		<!-- Customer Phone -->
		<div>
			<label class="block text-sm font-medium mb-1">Customer Phone</label>
			<input
				v-model="form.customer_phone"
				type="tel"
				placeholder="(555) 123-4567"
				class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
			/>
		</div>

		<!-- Repair Type with Categories -->
		<div>
			<label class="block text-sm font-medium mb-1">Repair Type *</label>
			<div class="flex gap-2 mb-2">
				<select
					:value="selectedCategory"
					@change="$emit('update:selected-category', $event.target.value)"
					class="px-3 py-1 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
				>
					<option value="">All Categories</option>
					<option v-for="cat in repairCategories" :key="cat" :value="cat">
						{{ cat }}
					</option>
				</select>
				<input
					:value="repairTypeSearch"
					@input="$emit('update:repair-type-search', $event.target.value)"
					type="text"
					placeholder="Search repair types..."
					class="flex-1 px-3 py-1 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
				/>
			</div>
			<select
				v-model="form.repair_type"
				required
				class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
			>
				<option value="">Select...</option>
				<optgroup
					v-for="(types, category) in groupedRepairTypes"
					:key="category"
					:label="category"
				>
					<option v-for="rt in types" :key="rt.name" :value="rt.name">
						{{ rt.repair_name || rt.name }} - ${{ rt.base_price || 0 }}
					</option>
				</optgroup>
			</select>
			<div
				v-if="selectedRepairType"
				class="mt-2 p-2 bg-blue-50 dark:bg-blue-900/20 rounded text-xs"
			>
				<div class="flex justify-between">
					<span class="text-gray-600">Base Price:</span>
					<span class="font-medium">${{ selectedRepairType.base_price || 0 }}</span>
				</div>
				<div v-if="selectedRepairType.estimated_days" class="flex justify-between">
					<span class="text-gray-600">Est. Days:</span>
					<span class="font-medium">{{ selectedRepairType.estimated_days }} days</span>
				</div>
				<p v-if="selectedRepairType.description" class="mt-1 text-gray-500">
					{{ selectedRepairType.description }}
				</p>
			</div>
		</div>

		<!-- Quick Notes Templates -->
		<div v-if="form.repair_type">
			<label class="block text-sm font-medium mb-1">Quick Notes</label>
			<div class="flex flex-wrap gap-1 mb-2">
				<button
					v-for="(template, idx) in noteTemplates"
					:key="idx"
					type="button"
					@click="$emit('add-note-template', template)"
					class="px-2 py-1 text-xs bg-gray-100 dark:bg-warm-dark-900 rounded hover:bg-gray-200"
				>
					{{ template.label }}
				</button>
			</div>
		</div>

		<!-- Item Details Grid -->
		<div class="grid grid-cols-2 gap-3">
			<div>
				<label class="block text-sm font-medium mb-1">Item Type</label>
				<select
					v-model="form.item_type"
					class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
				>
					<option value="">Select...</option>
					<option>Ring</option>
					<option>Necklace</option>
					<option>Bracelet</option>
					<option>Earring</option>
					<option>Watch</option>
					<option>Chain</option>
					<option>Pendant</option>
					<option>Brooch</option>
					<option>Other</option>
				</select>
			</div>
			<div>
				<label class="block text-sm font-medium mb-1">Priority</label>
				<select
					v-model="form.priority"
					class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
				>
					<option value="Low">Low</option>
					<option value="Medium">Medium</option>
					<option value="High">High</option>
					<option value="Urgent">Urgent</option>
				</select>
			</div>
		</div>

		<!-- Brand & Serial Number -->
		<div class="grid grid-cols-2 gap-3">
			<div>
				<label class="block text-sm font-medium mb-1">Brand</label>
				<input
					v-model="form.item_brand"
					type="text"
					placeholder="e.g., Rolex, Tiffany"
					class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
				/>
			</div>
			<div>
				<label class="block text-sm font-medium mb-1">Serial Number</label>
				<input
					v-model="form.serial_number"
					type="text"
					placeholder="For watches, etc."
					class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
				/>
			</div>
		</div>

		<!-- Description -->
		<div>
			<label class="block text-sm font-medium mb-1">Item Description</label>
			<textarea
				v-model="form.item_description"
				rows="2"
				placeholder="Describe the item and repair needed..."
				class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm resize-none"
			></textarea>
		</div>

		<!-- Weight & Stones -->
		<div class="grid grid-cols-2 gap-3">
			<div>
				<label class="block text-sm font-medium mb-1">Item Weight (g)</label>
				<input
					v-model.number="form.item_weight"
					type="number"
					step="0.01"
					placeholder="0.00"
					class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
				/>
			</div>
			<div>
				<label class="block text-sm font-medium mb-1">Stone Weight (ct)</label>
				<input
					v-model.number="form.stone_weight"
					type="number"
					step="0.01"
					placeholder="0.00"
					class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
				/>
			</div>
		</div>

		<!-- Item Condition -->
		<div>
			<label class="block text-sm font-medium mb-1">Item Condition (at intake)</label>
			<textarea
				v-model="form.item_condition"
				rows="1"
				placeholder="Scratches, worn prongs, loose stones, etc."
				class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm resize-none"
			></textarea>
		</div>

		<!-- Metal Type & Purity -->
		<div class="grid grid-cols-2 gap-3">
			<div>
				<label class="block text-sm font-medium mb-1">Metal Type</label>
				<select
					v-model="form.metal_type"
					class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
				>
					<option value="">None</option>
					<option v-for="m in metals" :key="m.name" :value="m.name">{{ m.name }}</option>
				</select>
			</div>
			<div>
				<label class="block text-sm font-medium mb-1">Purity</label>
				<select
					v-model="form.purity"
					class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
				>
					<option value="">Select...</option>
					<option>10K</option>
					<option>14K</option>
					<option>18K</option>
					<option>22K</option>
					<option>24K</option>
					<option>925</option>
					<option>950</option>
					<option>999</option>
				</select>
			</div>
		</div>

		<!-- Gemstones Section -->
		<div
			class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-3 border border-purple-100 dark:border-purple-800/30"
		>
			<div class="flex items-center justify-between mb-2">
				<h4 class="text-sm font-bold text-purple-700 dark:text-purple-400">Gemstones</h4>
				<button
					type="button"
					@click="$emit('add-gemstone')"
					class="text-xs px-2 py-1 bg-purple-500 text-white rounded hover:bg-purple-600"
				>
					+ Add Stone
				</button>
			</div>
			<div
				v-if="form.gemstones.length === 0"
				class="text-xs text-purple-600 dark:text-purple-400 text-center py-2"
			>
				No gemstones added
			</div>
			<div v-else class="space-y-2 max-h-40 overflow-y-auto">
				<div
					v-for="(stone, idx) in form.gemstones"
					:key="idx"
					class="bg-white dark:bg-warm-dark-900 rounded p-2 text-xs"
				>
					<div class="grid grid-cols-3 gap-2">
						<select
							v-model="stone.type"
							class="px-2 py-1 border rounded bg-white dark:bg-warm-dark-900"
						>
							<option value="">Type</option>
							<option>Diamond</option>
							<option>Ruby</option>
							<option>Sapphire</option>
							<option>Emerald</option>
							<option>Pearl</option>
							<option>Other</option>
						</select>
						<input
							v-model.number="stone.count"
							type="number"
							min="1"
							placeholder="Qty"
							class="px-2 py-1 border rounded bg-white dark:bg-warm-dark-900"
						/>
						<input
							v-model.number="stone.carat_weight"
							type="number"
							step="0.01"
							placeholder="Carat"
							class="px-2 py-1 border rounded bg-white dark:bg-warm-dark-900"
						/>
					</div>
					<div class="grid grid-cols-3 gap-2 mt-1">
						<select
							v-model="stone.color"
							class="px-2 py-1 border rounded bg-white dark:bg-warm-dark-900"
						>
							<option value="">Color</option>
							<option>D</option>
							<option>E</option>
							<option>F</option>
							<option>G</option>
							<option>H</option>
							<option>I</option>
							<option>J</option>
							<option>K+</option>
						</select>
						<select
							v-model="stone.clarity"
							class="px-2 py-1 border rounded bg-white dark:bg-warm-dark-900"
						>
							<option value="">Clarity</option>
							<option>FL</option>
							<option>IF</option>
							<option>VVS1</option>
							<option>VVS2</option>
							<option>VS1</option>
							<option>VS2</option>
							<option>SI1</option>
							<option>SI2</option>
						</select>
						<button
							type="button"
							@click="$emit('remove-gemstone', idx)"
							class="text-red-500 hover:text-red-700"
						>
							Remove
						</button>
					</div>
				</div>
			</div>
		</div>

		<!-- Compliance Section -->
		<div
			class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-3 border border-orange-100 dark:border-orange-800/30"
		>
			<h4 class="text-sm font-bold text-orange-700 dark:text-orange-400 mb-2">
				Customer ID Verification (JVC Compliance)
			</h4>
			<div class="grid grid-cols-2 gap-2">
				<select
					v-model="form.customer_id_type"
					class="px-2 py-1 border rounded text-sm bg-white dark:bg-warm-dark-900"
				>
					<option value="">ID Type</option>
					<option>Driver's License</option>
					<option>State ID</option>
					<option>Passport</option>
					<option>Other</option>
				</select>
				<input
					v-model="form.customer_id_number"
					type="text"
					placeholder="ID Number"
					class="px-2 py-1 border rounded text-sm bg-white dark:bg-warm-dark-900"
				/>
			</div>
			<input
				v-model="form.customer_id_state"
				type="text"
				placeholder="Issuing State (if applicable)"
				class="mt-2 px-2 py-1 border rounded text-sm w-full bg-white dark:bg-warm-dark-900"
			/>
		</div>

		<!-- Warranty Repair Link -->
		<div
			class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 border border-green-100 dark:border-green-800/30"
		>
			<label class="flex items-center gap-2">
				<input v-model="form.is_warranty_repair" type="checkbox" class="rounded" />
				<span class="text-sm font-medium text-green-800 dark:text-green-400"
					>Warranty Repair</span
				>
			</label>
			<div v-if="form.is_warranty_repair" class="mt-2">
				<input
					v-model="form.original_repair_order"
					type="text"
					placeholder="Original Repair # (e.g., RPR-2026-001)"
					class="w-full px-2 py-1 border rounded text-sm bg-white dark:bg-warm-dark-900"
				/>
				<select
					v-model="form.warranty_claim_type"
					class="mt-2 w-full px-2 py-1 border rounded text-sm bg-white dark:bg-warm-dark-900"
				>
					<option value="">Claim Type</option>
					<option>Full Warranty</option>
					<option>Partial</option>
					<option>Not Covered</option>
				</select>
			</div>
		</div>

		<!-- Promised Date -->
		<div>
			<label class="block text-sm font-medium mb-1">Promised Date</label>
			<input
				v-model="form.promised_date"
				type="date"
				class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
			/>
		</div>

		<!-- Estimated Cost -->
		<div>
			<label class="block text-sm font-medium mb-1">Estimated Cost ($)</label>
			<input
				v-model.number="form.estimated_cost"
				type="number"
				step="0.01"
				min="0"
				placeholder="0.00"
				class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
			/>
		</div>

		<!-- Deposit Collection -->
		<div
			class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3 border border-blue-100 dark:border-blue-800/30"
		>
			<label class="flex items-center gap-2">
				<input v-model="form.collect_deposit" type="checkbox" class="rounded" />
				<span class="text-sm font-medium text-blue-800 dark:text-blue-400"
					>Collect Deposit Now</span
				>
			</label>
			<div v-if="form.collect_deposit" class="mt-2 grid grid-cols-2 gap-2">
				<input
					v-model.number="form.deposit_amount"
					type="number"
					step="0.01"
					placeholder="Deposit amount"
					class="px-2 py-1 border rounded text-sm bg-white dark:bg-warm-dark-900"
				/>
				<select
					v-model="form.deposit_method"
					class="px-2 py-1 border rounded text-sm bg-white dark:bg-warm-dark-900"
				>
					<option value="Cash">Cash</option>
					<option value="Credit Card">Credit Card</option>
					<option value="Check">Check</option>
				</select>
			</div>
		</div>

		<!-- Actions -->
		<div class="flex gap-3 pt-2">
			<button
				type="button"
				@click="$emit('cancel')"
				class="flex-1 py-2 border rounded-lg text-sm font-medium hover:bg-gray-50 dark:hover:bg-gray-800"
			>
				Cancel
			</button>
			<button
				type="submit"
				:disabled="submitting"
				class="flex-1 py-2 bg-[#D4AF37] text-black rounded-lg text-sm font-bold hover:bg-[#c9a432] disabled:opacity-50"
			>
				{{ submitting ? 'Creating...' : 'Create Repair' }}
			</button>
		</div>
	</form>
</template>

<script setup>
defineProps({
	form: Object,
	customerSearch: String,
	customerResults: Array,
	allRepairTypes: Array,
	repairTypes: Array,
	repairCategories: Array,
	groupedRepairTypes: Object,
	selectedRepairType: Object,
	selectedCategory: String,
	repairTypeSearch: String,
	metals: Array,
	noteTemplates: Array,
	showHistory: Boolean,
	customerRepairHistory: Array,
	showNewCustomer: Boolean,
	newCustomerForm: Object,
	newCustomerSubmitting: Boolean,
	submitting: Boolean,
	inlineMode: Boolean,
})

defineEmits([
	'toggle-new-customer',
	'update:customer-search',
	'search-customers',
	'select-customer',
	'toggle-history',
	'update:selected-category',
	'update:repair-type-search',
	'filter-repair-types',
	'add-note-template',
	'add-gemstone',
	'remove-gemstone',
	'create-customer',
	'submit',
	'cancel',
])
</script>
