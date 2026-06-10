<template>
	<transition name="drawer-slide">
		<div v-if="visible" class="drawer-overlay" @click.self="$emit('close')">
			<div class="drawer-panel">
				<div class="drawer-header">
					<h3 class="drawer-title">
						{{ mode === 'assemble' ? '🔧 Assemble Piece' : '🔨 Disassemble Piece' }}
					</h3>
					<button class="drawer-close" @click="$emit('close')">&times;</button>
				</div>

				<div class="drawer-body">
					<!-- Mode Toggle -->
					<div class="mode-toggle">
						<button
							:class="['mode-btn', { active: mode === 'assemble' }]"
							@click="mode = 'assemble'"
						>
							<span class="mode-icon">⚙️</span> Assemble
						</button>
						<button
							:class="['mode-btn', { active: mode === 'disassemble' }]"
							@click="mode = 'disassemble'"
						>
							<span class="mode-icon">🔩</span> Disassemble
						</button>
					</div>

					<!-- Assemble Mode -->
					<div v-if="mode === 'assemble'" class="section">
						<label class="field-label">BOM</label>
						<select v-model="form.bom_name" class="field-input">
							<option value="">Select BOM...</option>
							<option v-for="b in bomList" :key="b.name" :value="b.name">
								{{ b.bom_name }} — {{ b.parent_item_code }}
							</option>
						</select>

						<label class="field-label">Target Warehouse</label>
						<select v-model="form.target_warehouse" class="field-input">
							<option value="">Select warehouse...</option>
							<option v-for="w in warehouses" :key="w" :value="w">{{ w }}</option>
						</select>

						<div v-if="selectedBom" class="component-checklist">
							<h4 class="checklist-title">Components Required</h4>
							<div
								v-for="(comp, idx) in selectedBom.components || []"
								:key="idx"
								class="checklist-row"
							>
								<span class="comp-badge" :class="typeClass(comp.component_type)">{{
									comp.component_type
								}}</span>
								<span class="comp-name">{{ comp.component_item_name }}</span>
								<span class="comp-qty">× {{ comp.qty_per_build }}</span>
								<input
									v-if="comp.serial_required"
									v-model="componentSerials[idx]"
									class="serial-input"
									placeholder="Serial #"
								/>
								<span v-else class="no-serial">Bulk</span>
							</div>
						</div>

						<label class="field-label">Labor (minutes)</label>
						<input
							v-model.number="form.labor_minutes"
							type="number"
							min="0"
							class="field-input"
						/>

						<label class="field-label">Notes</label>
						<textarea
							v-model="form.notes"
							class="field-input field-textarea"
							rows="2"
						></textarea>
					</div>

					<!-- Disassemble Mode -->
					<div v-if="mode === 'disassemble'" class="section">
						<label class="field-label">Parent Serial No</label>
						<input
							v-model="form.parent_serial_no"
							class="field-input"
							placeholder="Scan or type serial..."
						/>

						<label class="field-label">Target Warehouse</label>
						<select v-model="form.target_warehouse" class="field-input">
							<option value="">Select warehouse...</option>
							<option v-for="w in warehouses" :key="w" :value="w">{{ w }}</option>
						</select>

						<label class="field-label">Cost Allocation</label>
						<div class="radio-group">
							<label class="radio-option">
								<input
									type="radio"
									v-model="form.cost_allocation"
									value="by_cost_share"
								/>
								By Cost Share %
							</label>
							<label class="radio-option">
								<input
									type="radio"
									v-model="form.cost_allocation"
									value="manual"
								/>
								Manual
							</label>
						</div>

						<label class="field-label">Notes</label>
						<textarea
							v-model="form.notes"
							class="field-input field-textarea"
							rows="2"
						></textarea>
					</div>
				</div>

				<div class="drawer-footer">
					<button class="btn-cancel" @click="$emit('close')">Cancel</button>
					<button class="btn-submit" :disabled="submitting" @click="handleSubmit">
						<span v-if="submitting" class="spinner"></span>
						{{ mode === 'assemble' ? 'Assemble' : 'Disassemble' }}
					</button>
				</div>
			</div>
		</div>
	</transition>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'

const props = defineProps({
	visible: { type: Boolean, default: false },
	bomList: { type: Array, default: () => [] },
	warehouses: { type: Array, default: () => [] },
	initialMode: { type: String, default: 'assemble' },
})

const emit = defineEmits(['close', 'assemble', 'disassemble'])

const mode = ref(props.initialMode)
const submitting = ref(false)
const componentSerials = reactive({})

const form = reactive({
	bom_name: '',
	target_warehouse: '',
	parent_serial_no: '',
	labor_minutes: 0,
	cost_allocation: 'by_cost_share',
	notes: '',
})

const selectedBom = computed(() => props.bomList.find((b) => b.name === form.bom_name))

watch(
	() => form.bom_name,
	() => {
		Object.keys(componentSerials).forEach((k) => delete componentSerials[k])
	}
)

function typeClass(type) {
	const map = {
		Setting: 'type-setting',
		'Center Stone': 'type-center',
		Melee: 'type-melee',
		Finding: 'type-finding',
	}
	return map[type] || 'type-other'
}

async function handleSubmit() {
	submitting.value = true
	try {
		if (mode.value === 'assemble') {
			const serials = Object.entries(componentSerials).map(([idx, sn]) => ({
				component_item: selectedBom.value.components[idx].component_item,
				serial_no: sn,
			}))
			emit('assemble', { ...form, component_serials: serials })
		} else {
			emit('disassemble', { ...form })
		}
	} finally {
		submitting.value = false
	}
}
</script>

<style scoped>
.drawer-overlay {
	position: fixed;
	inset: 0;
	background: rgba(0, 0, 0, 0.4);
	z-index: 1000;
	display: flex;
	justify-content: flex-end;
}
.drawer-panel {
	width: 480px;
	max-width: 90vw;
	background: white;
	display: flex;
	flex-direction: column;
	box-shadow: -4px 0 24px rgba(0, 0, 0, 0.12);
}
.drawer-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 16px 20px;
	border-bottom: 1px solid #e2e8f0;
}
.drawer-title {
	font-size: 16px;
	font-weight: 700;
	margin: 0;
}
.drawer-close {
	background: none;
	border: none;
	font-size: 24px;
	cursor: pointer;
	color: #94a3b8;
}
.drawer-body {
	flex: 1;
	overflow-y: auto;
	padding: 20px;
}
.drawer-footer {
	display: flex;
	gap: 12px;
	justify-content: flex-end;
	padding: 16px 20px;
	border-top: 1px solid #e2e8f0;
}
.mode-toggle {
	display: flex;
	gap: 8px;
	margin-bottom: 20px;
}
.mode-btn {
	flex: 1;
	padding: 10px;
	border: 1px solid #e2e8f0;
	border-radius: 8px;
	background: white;
	cursor: pointer;
	font-size: 13px;
	font-weight: 600;
	transition: all 0.15s;
}
.mode-btn.active {
	border-color: #3b82f6;
	background: #eff6ff;
	color: #3b82f6;
	box-shadow: 0 0 0 1px #3b82f6;
}
.mode-icon {
	font-size: 16px;
}
.section {
	display: flex;
	flex-direction: column;
	gap: 12px;
}
.field-label {
	font-size: 12px;
	font-weight: 600;
	color: #64748b;
	text-transform: uppercase;
	letter-spacing: 0.05em;
}
.field-input {
	padding: 8px 12px;
	border: 1px solid #e2e8f0;
	border-radius: 6px;
	font-size: 13px;
}
.field-input:focus {
	outline: none;
	border-color: #3b82f6;
	box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.15);
}
.field-textarea {
	resize: vertical;
}
.component-checklist {
	background: #f8fafc;
	border-radius: 8px;
	padding: 12px;
}
.checklist-title {
	font-size: 13px;
	font-weight: 600;
	margin: 0 0 8px;
}
.checklist-row {
	display: flex;
	align-items: center;
	gap: 8px;
	padding: 6px 0;
	border-bottom: 1px solid #f1f5f9;
}
.comp-badge {
	font-size: 10px;
	padding: 2px 6px;
	border-radius: 4px;
	font-weight: 600;
	text-transform: uppercase;
}
.type-setting {
	background: #fef3c7;
	color: #92400e;
}
.type-center {
	background: #dbeafe;
	color: #1e40af;
}
.type-melee {
	background: #e0e7ff;
	color: #3730a3;
}
.type-finding {
	background: #f3e8ff;
	color: #6b21a8;
}
.type-other {
	background: #f1f5f9;
	color: #475569;
}
.comp-name {
	flex: 1;
	font-size: 12px;
}
.comp-qty {
	color: #94a3b8;
	font-size: 12px;
}
.serial-input {
	width: 120px;
	padding: 4px 8px;
	border: 1px solid #e2e8f0;
	border-radius: 4px;
	font-size: 12px;
}
.no-serial {
	color: #94a3b8;
	font-size: 11px;
	font-style: italic;
}
.radio-group {
	display: flex;
	gap: 16px;
}
.radio-option {
	display: flex;
	align-items: center;
	gap: 6px;
	font-size: 13px;
	cursor: pointer;
}
.btn-cancel {
	padding: 8px 16px;
	border: 1px solid #e2e8f0;
	border-radius: 6px;
	background: white;
	cursor: pointer;
	font-size: 13px;
}
.btn-submit {
	padding: 8px 20px;
	border: none;
	border-radius: 6px;
	background: #3b82f6;
	color: white;
	cursor: pointer;
	font-size: 13px;
	font-weight: 600;
	display: flex;
	align-items: center;
	gap: 8px;
}
.btn-submit:disabled {
	opacity: 0.6;
	cursor: not-allowed;
}
.btn-submit:hover:not(:disabled) {
	background: #2563eb;
}
.spinner {
	width: 14px;
	height: 14px;
	border: 2px solid rgba(255, 255, 255, 0.3);
	border-top-color: white;
	border-radius: 50%;
	animation: spin 0.6s linear infinite;
}
@keyframes spin {
	to {
		transform: rotate(360deg);
	}
}
.drawer-slide-enter-active,
.drawer-slide-leave-active {
	transition: opacity 0.25s;
}
.drawer-slide-enter-active .drawer-panel,
.drawer-slide-leave-active .drawer-panel {
	transition: transform 0.25s ease;
}
.drawer-slide-enter-from,
.drawer-slide-leave-to {
	opacity: 0;
}
.drawer-slide-enter-from .drawer-panel {
	transform: translateX(100%);
}
.drawer-slide-leave-to .drawer-panel {
	transform: translateX(100%);
}
</style>
