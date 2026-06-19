<template>
	<div class="bg-white/70 dark:bg-warm-dark-950/80 backdrop-blur-md rounded-xl border border-gray-200 dark:border-warm-border/50 overflow-hidden">
		<!-- Toolbar ──────────────────────────────────────────────────────────── -->
		<div class="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-warm-border/50">
			<div class="flex items-center gap-3">
				<span class="text-[10px] font-black uppercase tracking-widest text-gray-500 dark:text-gray-400">
					{{ stones.length }} stone{{ stones.length !== 1 ? 's' : '' }}
				</span>
				<!-- Lightspeed memo count badge ────────────────────────────── -->
				<span
					v-if="memoCount > 0"
					class="px-2 py-0.5 rounded-full bg-red-500/10 text-red-500 text-[9px] font-black uppercase tracking-wider border border-red-500/20"
				>
					{{ memoCount }} memo{{ memoCount > 1 ? 's' : '' }}
				</span>
			</div>
			<div class="flex items-center gap-2">
				<Button @click="addEmptyStone" class="px-3 py-1.5 rounded-lg text-[11px] font-bold bg-[#D4AF37] text-[#1E2022] hover:bg-[#CBA358] transition-all">
					+ Add Stone
				</Button>
				<Button
					v-if="stones.length > 0" @click="clearStones"
					class="px-3 py-1.5 rounded-lg text-[11px] font-bold bg-white dark:bg-warm-dark-800 border border-gray-200 dark:border-warm-border text-gray-500 dark:text-gray-400 hover:bg-red-50 dark:hover:bg-red-500/10 hover:text-red-500 transition-all"
				>
					Clear All
				</Button>
			</div>
		</div>

		<!-- Table ────────────────────────────────────────────────────────────── -->
		<div class="overflow-x-auto">
			<table class="w-full text-sm">
				<thead>
					<tr class="text-[10px] font-black uppercase tracking-widest text-gray-500 dark:text-gray-400 border-b border-gray-200 dark:border-warm-border/50">
						<th class="px-4 py-2.5 text-left">Type</th>
						<th class="px-4 py-2.5 text-left">Shape</th>
						<th class="px-4 py-2.5 text-left">Carat</th>
						<th class="px-4 py-2.5 text-left">Cut</th>
						<th class="px-4 py-2.5 text-left">Color</th>
						<th class="px-4 py-2.5 text-left">Clarity</th>
						<th class="px-4 py-2.5 text-left">Source</th>
						<th class="px-4 py-2.5 text-left">Status</th>
						<th class="px-4 py-2.5 text-right">Unit Price</th>
						<th class="px-4 py-2.5 text-right">Line Total</th>
						<th class="px-4 py-2.5 w-10"></th>
					</tr>
				</thead>
				<tbody>
					<tr
						v-for="(stone, idx) in stones"
						:key="stone.id"
						class="border-b border-gray-100 dark:border-warm-border/30 transition-colors"
						:class="isMemoRequest(stone) ? 'bg-red-500/5 dark:bg-red-500/5' : ''"
					>
						<!-- Stone Type -->
						<td class="px-4 py-2">
							<select
								v-model="stone.stoneType"
								@change="store.updateStone(stone.id, 'stoneType', $event.target.value)"
								class="bg-gray-50/50 dark:bg-warm-dark-900/50 border border-gray-200 dark:border-warm-border rounded-md text-xs font-medium text-gray-800 dark:text-gray-200 px-2 py-1.5 focus:ring-2 focus:ring-[#D4AF37] outline-none transition-all"
							>
								<option value="Diamond">Diamond</option>
								<option value="Sapphire">Sapphire</option>
								<option value="Ruby">Ruby</option>
								<option value="Emerald">Emerald</option>
								<option value="Moissanite">Moissanite</option>
								<option value="Other">Other</option>
							</select>
						</td>

						<!-- Shape -->
						<td class="px-4 py-2">
							<select
								v-model="stone.shape"
								@change="store.updateStone(stone.id, 'shape', $event.target.value)"
								class="bg-gray-50/50 dark:bg-warm-dark-900/50 border border-gray-200 dark:border-warm-border rounded-md text-xs font-medium text-gray-800 dark:text-gray-200 px-2 py-1.5 focus:ring-2 focus:ring-[#D4AF37] outline-none transition-all"
							>
								<option value="">—</option>
								<option value="Round">Round</option>
								<option value="Princess">Princess</option>
								<option value="Emerald">Emerald</option>
								<option value="Oval">Oval</option>
								<option value="Marquise">Marquise</option>
								<option value="Pear">Pear</option>
								<option value="Cushion">Cushion</option>
								<option value="Asscher">Asscher</option>
								<option value="Radiant">Radiant</option>
								<option value="Heart">Heart</option>
								<option value="Baguette">Baguette</option>
							</select>
						</td>

						<!-- Carat -->
						<td class="px-4 py-2">
							<input
								v-model.number="stone.caratWeight"
								type="number" step="0.01" min="0"
								@input="store.updateStone(stone.id, 'caratWeight', $event.target.value)"
								class="bg-gray-50/50 dark:bg-warm-dark-900/50 border border-gray-200 dark:border-warm-border rounded-md text-xs font-mono font-medium text-gray-800 dark:text-gray-200 w-20 px-2 py-1.5 focus:ring-2 focus:ring-[#D4AF37] outline-none transition-all"
							/>
						</td>

						<!-- Cut -->
						<td class="px-4 py-2">
							<select
								v-model="stone.cut"
								@change="store.updateStone(stone.id, 'cut', $event.target.value)"
								class="bg-gray-50/50 dark:bg-warm-dark-900/50 border border-gray-200 dark:border-warm-border rounded-md text-xs font-medium text-gray-800 dark:text-gray-200 px-2 py-1.5 focus:ring-2 focus:ring-[#D4AF37] outline-none transition-all"
							>
								<option value="">—</option>
								<option value="Excellent">Excellent</option>
								<option value="Very Good">Very Good</option>
								<option value="Good">Good</option>
								<option value="Fair">Fair</option>
								<option value="Poor">Poor</option>
							</select>
						</td>

						<!-- Color -->
						<td class="px-4 py-2">
							<select
								v-model="stone.color"
								@change="store.updateStone(stone.id, 'color', $event.target.value)"
								class="bg-gray-50/50 dark:bg-warm-dark-900/50 border border-gray-200 dark:border-warm-border rounded-md text-xs font-medium text-gray-800 dark:text-gray-200 px-2 py-1.5 focus:ring-2 focus:ring-[#D4AF37] outline-none transition-all"
							>
								<option value="">—</option>
								<option value="D">D</option>
								<option value="E">E</option>
								<option value="F">F</option>
								<option value="G">G</option>
								<option value="H">H</option>
								<option value="I">I</option>
								<option value="J">J</option>
								<option value="K">K</option>
							</select>
						</td>

						<!-- Clarity -->
						<td class="px-4 py-2">
							<select
								v-model="stone.clarity"
								@change="store.updateStone(stone.id, 'clarity', $event.target.value)"
								class="bg-gray-50/50 dark:bg-warm-dark-900/50 border border-gray-200 dark:border-warm-border rounded-md text-xs font-medium text-gray-800 dark:text-gray-200 px-2 py-1.5 focus:ring-2 focus:ring-[#D4AF37] outline-none transition-all"
							>
								<option value="">—</option>
								<option value="FL">FL</option>
								<option value="IF">IF</option>
								<option value="VVS1">VVS1</option>
								<option value="VVS2">VVS2</option>
								<option value="VS1">VS1</option>
								<option value="VS2">VS2</option>
								<option value="SI1">SI1</option>
								<option value="SI2">SI2</option>
								<option value="I1">I1</option>
							</select>
						</td>

						<!-- Source (vendor) -->
						<td class="px-4 py-2">
							<input
								v-model="stone.source"
								@input="store.updateStone(stone.id, 'source', $event.target.value)"
								type="text" placeholder="Supplier…"
								class="bg-gray-50/50 dark:bg-warm-dark-900/50 border border-gray-200 dark:border-warm-border rounded-md text-xs font-medium text-gray-800 dark:text-gray-200 w-24 px-2 py-1.5 focus:ring-2 focus:ring-[#D4AF37] outline-none transition-all"
							/>
						</td>

						<!-- ── 2. Lightspeed: In-Stock / Memo Request Toggle ────────── -->
						<td class="px-4 py-2">
							<div class="flex flex-col gap-1">
								<button
									@click="toggleMemo(stone.id)"
									class="flex items-center gap-1.5 px-2 py-1 rounded-md border transition-all text-xs font-bold"
									:class="isMemoRequest(stone)
										? 'border-red-500/30 bg-red-500/10 text-red-500 hover:bg-red-500/20'
										: 'border-green-500/30 bg-green-500/10 text-green-600 dark:text-green-400 hover:bg-green-500/20'"
								>
									<!-- Dot indicator -->
									<span class="w-2 h-2 rounded-full" :class="isMemoRequest(stone) ? 'bg-red-500' : 'bg-green-500'"></span>
									{{ isMemoRequest(stone) ? 'Memo Request' : 'In-Stock' }}
								</button>
								<!-- Memo Request red badge (Lightspeed vendor order indicator) -->
								<span
									v-if="isMemoRequest(stone)"
									class="inline-block px-2 py-0.5 rounded-full bg-red-500/10 text-red-500 text-[9px] font-black uppercase tracking-wider text-center mt-1"
								>
									Memo Request
								</span>
								<!-- Phase 2 Supplier Selection -->
								<select
									v-if="isMemoRequest(stone)"
									v-model="stone.supplierId"
									@change="store.updateStone(stone.id, 'supplierId', $event.target.value)"
									class="bg-white dark:bg-warm-dark-900 border border-red-500/30 rounded text-[10px] px-1 py-1 text-gray-800 dark:text-gray-200 outline-none w-full max-w-[120px] mt-1"
								>
									<option value="" disabled>Select Supplier...</option>
									<option v-for="sup in suppliers" :key="sup.value" :value="sup.value">
										{{ sup.label }}
									</option>
								</select>
							</div>
						</td>

						<!-- Unit Price -->
						<td class="px-4 py-2 text-right">
							<input
								v-model.number="stone.unitPrice"
								type="number" step="0.01" min="0"
								@input="store.updateStone(stone.id, 'unitPrice', $event.target.value)"
								class="bg-gray-50/50 dark:bg-warm-dark-900/50 border border-gray-200 dark:border-warm-border rounded-md text-xs font-mono font-medium text-gray-800 dark:text-gray-200 w-24 px-2 py-1.5 text-right focus:ring-2 focus:ring-[#D4AF37] outline-none transition-all"
							/>
						</td>

						<!-- Line Total -->
						<td class="px-4 py-2 text-right">
							<span class="font-mono text-xs font-bold text-gray-800 dark:text-gray-200">
								{{ formatCurrency(lineTotal(stone)) }}
							</span>
						</td>

						<!-- Remove -->
						<td class="px-4 py-2">
							<button
								@click="removeStone(stone.id)"
								class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-500/10 transition-all"
								title="Remove stone"
							>
								<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
								</svg>
							</button>
						</td>
					</tr>

					<!-- Empty state ──────────────────────────────────────────────── -->
					<tr v-if="stones.length === 0">
						<td colspan="11" class="px-4 py-12 text-center">
							<svg class="w-10 h-10 mx-auto text-gray-300 dark:text-gray-600 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
							</svg>
							<p class="text-sm font-medium text-gray-400 dark:text-gray-500">
								No stones added yet. Click "+ Add Stone" to start.
							</p>
						</td>
					</tr>
				</tbody>

				<!-- Footer total ──────────────────────────────────────────────── -->
				<tfoot v-if="stones.length > 0">
					<tr class="border-t-2 border-gray-200 dark:border-warm-border bg-gray-50/50 dark:bg-warm-dark-900/30">
						<td colspan="8" class="px-4 py-3 text-right">
							<span class="text-[10px] font-black uppercase tracking-widest text-gray-500 dark:text-gray-400">
								Total Stone Cost
							</span>
						</td>
						<td class="px-4 py-3 text-right">
							<span class="font-mono font-black text-[#D4AF37] text-lg">
								{{ formatCurrency(totalCost) }}
							</span>
						</td>
						<td></td>
					</tr>
				</tfoot>
			</table>
		</div>
	</div>
</template>

<script setup>
import { computed } from 'vue'
import { useSpecialOrderStore } from '@/stores/specialOrder'

const store = useSpecialOrderStore()
const stones = computed(() => store.draftOrder.stones)
const suppliers = computed(() => store.suppliers)

const memoCount = computed(() => {
	return stones.value.filter(isMemoRequest).length
})

function addEmptyStone() {
	store.addStone({})
}

function removeStone(id) {
	store.removeStone(id)
}

function clearStones() {
	store.clearStones()
}

/**
 * Lightspeed toggle: flip a stone between In-Stock and Memo Request.
 * Memo Request → sets sourcingMethod to "Memo Request" (red badge).
 * In-Stock → sets sourcingMethod to "In-House".
 */
function toggleMemo(stoneId) {
	const stone = stones.value.find((s) => s.id === stoneId)
	if (!stone) return
	const isMemo = stone.sourcingMethod === 'Memo Request'
	store.updateStone(stoneId, 'sourcingMethod', isMemo ? 'In-House' : 'Memo Request')
}

function lineTotal(stone) {
	return Number(((stone.caratWeight || 0) * (stone.unitPrice || 0)).toFixed(2))
}

const totalCost = computed(() => store.totalStoneCost)

function isMemoRequest(stone) {
	return stone.sourcingMethod === 'Memo Request'
}

function formatCurrency(value) {
	return '$' + Number(value || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}
</script>
