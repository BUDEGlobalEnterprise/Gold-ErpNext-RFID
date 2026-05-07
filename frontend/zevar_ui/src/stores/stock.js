import { defineStore } from 'pinia'
import { createResource } from 'frappe-ui'
import { ref, computed } from 'vue'

export const useStockStore = defineStore('stock', () => {
	const supplierOrders = ref([])
	const supplierOrdersTotal = ref(0)
	const currentOrder = ref(null)

	const memos = ref([])
	const memosTotal = ref(0)

	const assemblies = ref([])
	const assembliesTotal = ref(0)

	const metals = ref([])
	const metalsTotal = ref(0)

	const gems = ref([])
	const gemsTotal = ref(0)

	const warehouses = ref([])
	const warehousesTotal = ref(0)
	const currentWarehouse = ref(null)

	const categories = ref([])
	const categoriesTotal = ref(0)

	const brands = ref([])
	const brandsTotal = ref(0)

	const collections = ref([])
	const collectionsTotal = ref(0)

	const suppliers = ref([])

	// ─── Resources ───────────────────────────────────────────────────────────

	const supplierOrdersResource = createResource({
		url: 'zevar_core.api.stock.get_supplier_orders',
		onSuccess(data) {
			supplierOrders.value = data.orders || []
			supplierOrdersTotal.value = data.total || 0
		},
	})

	const orderDetailResource = createResource({
		url: 'zevar_core.api.stock.get_supplier_order_detail',
		onSuccess(data) {
			currentOrder.value = data.order || null
		},
	})

	const createPOResource = createResource({
		url: 'zevar_core.api.stock.create_purchase_order',
	})

	const submitPOResource = createResource({
		url: 'zevar_core.api.stock.submit_purchase_order',
	})

	const cancelPOResource = createResource({
		url: 'zevar_core.api.stock.cancel_purchase_order',
	})

	const memosResource = createResource({
		url: 'zevar_core.api.stock.get_incoming_memos',
		onSuccess(data) {
			memos.value = data.memos || []
			memosTotal.value = data.total || 0
		},
	})

	const createMemoResource = createResource({
		url: 'zevar_core.api.stock.create_memo',
	})

	const receiveMemoResource = createResource({
		url: 'zevar_core.api.stock.receive_memo',
	})

	const assembliesResource = createResource({
		url: 'zevar_core.api.stock.get_assemblies',
		onSuccess(data) {
			assemblies.value = data.assemblies || []
			assembliesTotal.value = data.total || 0
		},
	})

	const createAssemblyResource = createResource({
		url: 'zevar_core.api.stock.create_assembly',
	})

	const disassembleResource = createResource({
		url: 'zevar_core.api.stock.disassemble',
	})

	const metalsResource = createResource({
		url: 'zevar_core.api.stock.get_metals',
		onSuccess(data) {
			metals.value = data.items || []
			metalsTotal.value = data.total || 0
		},
	})

	const gemsResource = createResource({
		url: 'zevar_core.api.stock.get_gems',
		onSuccess(data) {
			gems.value = data.items || []
			gemsTotal.value = data.total || 0
		},
	})

	const warehousesResource = createResource({
		url: 'zevar_core.api.stock.get_warehouses',
		onSuccess(data) {
			warehouses.value = data.warehouses || []
			warehousesTotal.value = data.total || 0
		},
	})

	const warehouseDetailResource = createResource({
		url: 'zevar_core.api.stock.get_warehouse_details',
		onSuccess(data) {
			currentWarehouse.value = data
		},
	})

	const categoriesResource = createResource({
		url: 'zevar_core.api.stock.get_categories',
		onSuccess(data) {
			categories.value = data.categories || []
			categoriesTotal.value = data.total || 0
		},
	})

	const brandsResource = createResource({
		url: 'zevar_core.api.stock.get_brands',
		onSuccess(data) {
			brands.value = data.brands || []
			brandsTotal.value = data.total || 0
		},
	})

	const collectionsResource = createResource({
		url: 'zevar_core.api.stock.get_collections',
		onSuccess(data) {
			collections.value = data.collections || []
			collectionsTotal.value = data.total || 0
		},
	})

	const suppliersResource = createResource({
		url: 'zevar_core.api.stock.get_suppliers',
		onSuccess(data) {
			suppliers.value = data.suppliers || []
		},
	})

	// ─── Actions ─────────────────────────────────────────────────────────────

	function loadSupplierOrders(params = {}) {
		return supplierOrdersResource.submit(params)
	}

	function loadOrderDetail(name) {
		return orderDetailResource.submit({ name })
	}

	function createPO(supplier, items_json, warehouse, schedule_date) {
		return createPOResource.submit({ supplier, items_json, warehouse, schedule_date })
	}

	function submitPO(name) {
		return submitPOResource.submit({ name })
	}

	function cancelPO(name) {
		return cancelPOResource.submit({ name })
	}

	function loadMemos(params = {}) {
		return memosResource.submit(params)
	}

	function createMemo(supplier, items_json, warehouse) {
		return createMemoResource.submit({ supplier, items_json, warehouse })
	}

	function receiveMemo(name) {
		return receiveMemoResource.submit({ name })
	}

	function loadAssemblies(params = {}) {
		return assembliesResource.submit(params)
	}

	function createAssembly(items_json, source_warehouse, target_warehouse, purpose) {
		return createAssemblyResource.submit({ items_json, source_warehouse, target_warehouse, purpose })
	}

	function disassemble(name) {
		return disassembleResource.submit({ name })
	}

	function loadMetals(params = {}) {
		return metalsResource.submit(params)
	}

	function loadGems(params = {}) {
		return gemsResource.submit(params)
	}

	function loadWarehouses(params = {}) {
		return warehousesResource.submit(params)
	}

	function loadWarehouseDetail(name) {
		return warehouseDetailResource.submit({ name })
	}

	function loadCategories(params = {}) {
		return categoriesResource.submit(params)
	}

	function loadBrands(params = {}) {
		return brandsResource.submit(params)
	}

	function loadCollections(params = {}) {
		return collectionsResource.submit(params)
	}

	function loadSuppliers(search) {
		return suppliersResource.submit({ search })
	}

	return {
		supplierOrders,
		supplierOrdersTotal,
		currentOrder,
		memos,
		memosTotal,
		assemblies,
		assembliesTotal,
		metals,
		metalsTotal,
		gems,
		gemsTotal,
		warehouses,
		warehousesTotal,
		currentWarehouse,
		categories,
		categoriesTotal,
		brands,
		brandsTotal,
		collections,
		collectionsTotal,
		suppliers,

		supplierOrdersResource,
		orderDetailResource,
		createPOResource,
		submitPOResource,
		cancelPOResource,
		memosResource,
		createMemoResource,
		receiveMemoResource,
		assembliesResource,
		createAssemblyResource,
		disassembleResource,
		metalsResource,
		gemsResource,
		warehousesResource,
		warehouseDetailResource,
		categoriesResource,
		brandsResource,
		collectionsResource,
		suppliersResource,

		loadSupplierOrders,
		loadOrderDetail,
		createPO,
		submitPO,
		cancelPO,
		loadMemos,
		createMemo,
		receiveMemo,
		loadAssemblies,
		createAssembly,
		disassemble,
		loadMetals,
		loadGems,
		loadWarehouses,
		loadWarehouseDetail,
		loadCategories,
		loadBrands,
		loadCollections,
		loadSuppliers,
	}
})
