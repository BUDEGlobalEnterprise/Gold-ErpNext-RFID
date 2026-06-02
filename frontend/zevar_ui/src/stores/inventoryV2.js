import { defineStore } from 'pinia'
import { createResource } from 'frappe-ui'
import { ref, computed } from 'vue'

export const useInventoryV2Store = defineStore('inventoryV2', () => {
	// ─── State ────────────────────────────────────────────────────────────────
	const metals = ref([])
	const purities = ref([])
	const gemstoneTypes = ref([])
	const bomList = ref([])
	const currentBom = ref(null)
	const bomCostRollup = ref(null)
	const gemstones = ref([])
	const currentGemstone = ref(null)
	const memoAging = ref({})
	const expiringAppraisals = ref([])
	const benchStatus = ref([])
	const repairParts = ref({})

	// ─── Reference Tables ──────────────────────────────────────────────────────

	const metalsResource = createResource({
		url: 'zevar_core.api.inventory_v2.list_metals',
		onSuccess(data) { metals.value = data || [] },
	})

	const puritiesResource = createResource({
		url: 'zevar_core.api.inventory_v2.list_purities',
		onSuccess(data) { purities.value = data || [] },
	})

	const gemstoneTypesResource = createResource({
		url: 'zevar_core.api.inventory_v2.list_gemstone_types',
		onSuccess(data) { gemstoneTypes.value = data || [] },
	})

	// ─── BOM ───────────────────────────────────────────────────────────────────

	const bomListResource = createResource({
		url: 'zevar_core.api.inventory_v2.list_boms',
		onSuccess(data) { bomList.value = data || [] },
	})

	const bomDetailResource = createResource({
		url: 'zevar_core.api.inventory_v2.get_bom_for_item',
		onSuccess(data) { currentBom.value = data },
	})

	const bomCostResource = createResource({
		url: 'zevar_core.api.inventory_v2.get_bom_cost_rollup',
		onSuccess(data) { bomCostRollup.value = data },
	})

	const assembleResource = createResource({
		url: 'zevar_core.api.inventory_v2.assemble_from_bom',
	})

	const disassembleResource = createResource({
		url: 'zevar_core.api.inventory_v2.disassemble_to_components',
	})

	// ─── Gemstones ─────────────────────────────────────────────────────────────

	const gemstonesResource = createResource({
		url: 'zevar_core.api.inventory_v2.list_gemstones',
		onSuccess(data) { gemstones.value = data || [] },
	})

	const gemstoneDetailResource = createResource({
		url: 'zevar_core.api.inventory_v2.get_gemstone',
		onSuccess(data) { currentGemstone.value = data },
	})

	const registerGemstoneResource = createResource({
		url: 'zevar_core.api.inventory_v2.register_gemstone',
	})

	const attachGemstoneResource = createResource({
		url: 'zevar_core.api.inventory_v2.attach_gemstone_to_serial',
	})

	const detachGemstoneResource = createResource({
		url: 'zevar_core.api.inventory_v2.detach_gemstone_from_serial',
	})

	// ─── Repair Parts ──────────────────────────────────────────────────────────

	const repairPartsResource = createResource({
		url: 'zevar_core.api.inventory_v2.list_repair_parts',
		onSuccess(data) { repairParts.value = data || {} },
	})

	const consumePartResource = createResource({
		url: 'zevar_core.api.inventory_v2.consume_repair_part',
	})

	const returnPartResource = createResource({
		url: 'zevar_core.api.inventory_v2.return_repair_part',
	})

	// ─── External Bench ────────────────────────────────────────────────────────

	const dispatchBenchResource = createResource({
		url: 'zevar_core.api.inventory_v2.dispatch_to_external_bench',
	})

	const receiveBenchResource = createResource({
		url: 'zevar_core.api.inventory_v2.receive_from_external_bench',
	})

	const benchStatusResource = createResource({
		url: 'zevar_core.api.inventory_v2.get_bench_status',
		onSuccess(data) { benchStatus.value = data },
	})

	// ─── Memo Lifecycle ────────────────────────────────────────────────────────

	const createMemoResource = createResource({
		url: 'zevar_core.api.inventory_v2.create_memo',
	})

	const markMemoSoldResource = createResource({
		url: 'zevar_core.api.inventory_v2.mark_memo_item_sold',
	})

	const markMemoReturnedResource = createResource({
		url: 'zevar_core.api.inventory_v2.mark_memo_item_returned',
	})

	const memoAgingResource = createResource({
		url: 'zevar_core.api.inventory_v2.get_memo_aging_dashboard',
		onSuccess(data) { memoAging.value = data },
	})

	// ─── Appraisal ─────────────────────────────────────────────────────────────

	const createAppraisalResource = createResource({
		url: 'zevar_core.api.inventory_v2.create_appraisal',
	})

	const expiringAppraisalsResource = createResource({
		url: 'zevar_core.api.inventory_v2.list_expiring_appraisals',
		onSuccess(data) { expiringAppraisals.value = data || [] },
	})

	const appraisalHistoryResource = createResource({
		url: 'zevar_core.api.inventory_v2.get_appraisal_history',
	})

	// ─── Inventory Locking ─────────────────────────────────────────────────────

	const acquireLockResource = createResource({
		url: 'zevar_core.api.inventory_v2.acquire_inventory_lock',
	})

	const releaseLockResource = createResource({
		url: 'zevar_core.api.inventory_v2.release_inventory_lock',
	})

	const checkLockResource = createResource({
		url: 'zevar_core.api.inventory_v2.check_inventory_lock',
	})

	// ─── Actions ──────────────────────────────────────────────────────────────

	function loadMetals() { return metalsResource.submit() }
	function loadPurities(metal) { return puritiesResource.submit({ metal }) }
	function loadGemstoneTypes() { return gemstoneTypesResource.submit() }

	function loadBomList(itemCode) { return bomListResource.submit({ item_code: itemCode }) }
	function loadBomDetail(itemCode) { return bomDetailResource.submit({ item_code: itemCode }) }
	function loadBomCost(bomName) { return bomCostResource.submit({ bom_name: bomName }) }
	function assemble(bomName, parentSerialNo) {
		return assembleResource.submit({ bom_name: bomName, parent_serial_no: parentSerialNo })
	}
	function disassemble(serialNo, bomName, reason) {
		return disassembleResource.submit({ parent_serial_no: serialNo, bom_name: bomName, reason })
	}

	function loadGemstones(status, gemstoneType) {
		return gemstonesResource.submit({ status, gemstone_type: gemstoneType })
	}
	function loadGemstoneDetail(name) { return gemstoneDetailResource.submit({ name }) }
	function registerGemstone(data) { return registerGemstoneResource.submit({ data }) }
	function attachGemstone(gemstone, serialNo) {
		return attachGemstoneResource.submit({ gemstone, serial_no: serialNo })
	}
	function detachGemstone(gemstone) { return detachGemstoneResource.submit({ gemstone }) }

	function loadRepairParts(repairOrder) { return repairPartsResource.submit({ repair_order: repairOrder }) }
	function consumePart(data) { return consumePartResource.submit({ data }) }
	function returnPart(data) { return returnPartResource.submit({ data }) }

	function dispatchToBench(repairOrder, vendor, estimatedDays) {
		return dispatchBenchResource.submit({ repair_order: repairOrder, vendor, estimated_days: estimatedDays })
	}
	function receiveFromBench(repairOrder, invoiceRef, benchCost) {
		return receiveBenchResource.submit({ repair_order: repairOrder, invoice_ref: invoiceRef, bench_cost: benchCost })
	}
	function loadBenchStatus(vendor) { return benchStatusResource.submit({ vendor }) }

	function createMemoV2(data) { return createMemoResource.submit({ data }) }
	function markMemoSold(memoContract, itemCode, serialNo) {
		return markMemoSoldResource.submit({ memo_contract: memoContract, item_code: itemCode, serial_no: serialNo })
	}
	function markMemoReturned(memoContract, itemCode, serialNo, returnSlipRef) {
		return markMemoReturnedResource.submit({ memo_contract: memoContract, item_code: itemCode, serial_no: serialNo, return_slip_ref: returnSlipRef })
	}
	function loadMemoAging(memoClass) { return memoAgingResource.submit({ memo_class: memoClass }) }

	function createAppraisal(data) { return createAppraisalResource.submit({ data }) }
	function loadExpiringAppraisals(daysAhead) { return expiringAppraisalsResource.submit({ days_ahead: daysAhead }) }
	function loadAppraisalHistory(itemCode, serialNo) {
		return appraisalHistoryResource.submit({ item_code: itemCode, serial_no: serialNo })
	}

	function acquireLock(serialNo, lockOwner) { return acquireLockResource.submit({ serial_no: serialNo, lock_owner: lockOwner }) }
	function releaseLock(serialNo, lockToken) { return releaseLockResource.submit({ serial_no: serialNo, lock_token: lockToken }) }
	function checkLock(serialNo) { return checkLockResource.submit({ serial_no: serialNo }) }

	// ─── Computed ─────────────────────────────────────────────────────────────

	const loading = computed(() =>
		metalsResource.loading || bomListResource.loading || gemstonesResource.loading ||
		memoAgingResource.loading || expiringAppraisalsResource.loading
	)

	return {
		// state
		metals, purities, gemstoneTypes, bomList, currentBom, bomCostRollup,
		gemstones, currentGemstone, memoAging, expiringAppraisals,
		benchStatus, repairParts,
		// computed
		loading,
		// resources
		metalsResource, puritiesResource, gemstoneTypesResource,
		bomListResource, bomDetailResource, bomCostResource,
		assembleResource, disassembleResource,
		gemstonesResource, gemstoneDetailResource, registerGemstoneResource,
		attachGemstoneResource, detachGemstoneResource,
		repairPartsResource, consumePartResource, returnPartResource,
		dispatchBenchResource, receiveBenchResource, benchStatusResource,
		createMemoResource, markMemoSoldResource, markMemoReturnedResource, memoAgingResource,
		createAppraisalResource, expiringAppraisalsResource, appraisalHistoryResource,
		acquireLockResource, releaseLockResource, checkLockResource,
		// actions
		loadMetals, loadPurities, loadGemstoneTypes,
		loadBomList, loadBomDetail, loadBomCost, assemble, disassemble,
		loadGemstones, loadGemstoneDetail, registerGemstone, attachGemstone, detachGemstone,
		loadRepairParts, consumePart, returnPart,
		dispatchToBench, receiveFromBench, loadBenchStatus,
		createMemoV2, markMemoSold, markMemoReturned, loadMemoAging,
		createAppraisal, loadExpiringAppraisals, loadAppraisalHistory,
		acquireLock, releaseLock, checkLock,
	}
})
