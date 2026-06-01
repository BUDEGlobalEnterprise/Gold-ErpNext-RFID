import { defineStore } from 'pinia'
import { createResource } from 'frappe-ui'
import { ref } from 'vue'

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

	const catalogVendors = ref([])
	const catalogVendorsTotal = ref(0)

	// ─── Read resources ────────────────────────────────────────────────────────

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

	const memosResource = createResource({
		url: 'zevar_core.api.stock.get_incoming_memos',
		onSuccess(data) {
			memos.value = data.memos || []
			memosTotal.value = data.total || 0
		},
	})

	const assembliesResource = createResource({
		url: 'zevar_core.api.stock.get_assemblies',
		onSuccess(data) {
			assemblies.value = data.assemblies || []
			assembliesTotal.value = data.total || 0
		},
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

	// ─── Existing write resources (PO / Memo / Assembly) ──────────────────────

	const createPOResource = createResource({
		url: 'zevar_core.api.stock.create_purchase_order',
	})
	const submitPOResource = createResource({
		url: 'zevar_core.api.stock.submit_purchase_order',
	})
	const cancelPOResource = createResource({
		url: 'zevar_core.api.stock.cancel_purchase_order',
	})
	const createMemoResource = createResource({
		url: 'zevar_core.api.stock.create_memo',
	})
	const receiveMemoResource = createResource({
		url: 'zevar_core.api.stock.receive_memo',
	})
	const createAssemblyResource = createResource({
		url: 'zevar_core.api.stock.create_assembly',
	})
	const disassembleResource = createResource({
		url: 'zevar_core.api.stock.disassemble',
	})
	const submitAssemblyResource = createResource({
		url: 'zevar_core.api.stock.submit_assembly',
	})
	const assemblyDetailResource = createResource({
		url: 'zevar_core.api.stock.get_assembly_detail',
	})

	// ─── New generic CRUD resources (Phase 3) ─────────────────────────────────

	const createItemResource = createResource({
		url: 'zevar_core.api.crud.create_item',
	})
	const updateItemResource = createResource({
		url: 'zevar_core.api.crud.update_item',
	})
	const deleteItemResource = createResource({
		url: 'zevar_core.api.crud.delete_item',
	})
	const getItemResource = createResource({
		url: 'zevar_core.api.crud.get_item',
	})

	const createItemGroupResource = createResource({
		url: 'zevar_core.api.crud.create_item_group',
	})
	const updateItemGroupResource = createResource({
		url: 'zevar_core.api.crud.update_item_group',
	})
	const deleteItemGroupResource = createResource({
		url: 'zevar_core.api.crud.delete_item_group',
	})

	const createBrandResource = createResource({
		url: 'zevar_core.api.crud.create_brand',
	})
	const updateBrandResource = createResource({
		url: 'zevar_core.api.crud.update_brand',
	})
	const deleteBrandResource = createResource({
		url: 'zevar_core.api.crud.delete_brand',
	})

	const createWarehouseResource = createResource({
		url: 'zevar_core.api.crud.create_warehouse',
	})
	const updateWarehouseResource = createResource({
		url: 'zevar_core.api.crud.update_warehouse',
	})
	const deleteWarehouseResource = createResource({
		url: 'zevar_core.api.crud.delete_warehouse',
	})

	// Lookup helpers (used by modals)
	const itemGroupsForSelectResource = createResource({
		url: 'zevar_core.api.crud.get_item_groups_for_select',
	})
	const warehousesForSelectResource = createResource({
		url: 'zevar_core.api.crud.get_warehouses_for_select',
	})
	const itemsInGroupResource = createResource({
		url: 'zevar_core.api.crud.get_items_in_group',
	})
	const itemsForBrandResource = createResource({
		url: 'zevar_core.api.crud.get_items_for_brand',
	})

	// Vendor catalog resources
	const catalogVendorsResource = createResource({
		url: 'zevar_core.api.catalog.get_catalog_vendors',
		onSuccess(data) {
			catalogVendors.value = data.vendors || []
			catalogVendorsTotal.value = data.total || 0
		},
	})

	const catalogItemsResource = createResource({
		url: 'zevar_core.api.catalog.get_catalog_items',
	})

	// ─── Actions ──────────────────────────────────────────────────────────────

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
		return createAssemblyResource.submit({
			items_json,
			source_warehouse,
			target_warehouse,
			purpose,
		})
	}
	function disassemble(name) {
		return disassembleResource.submit({ name })
	}
	function submitAssembly(name) {
		return submitAssemblyResource.submit({ name })
	}
	function loadAssemblyDetail(name) {
		return assemblyDetailResource.submit({ name })
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

	// Item CRUD
	function createItem(values, item_group) {
		return createItemResource.submit({
			values_json: JSON.stringify(values),
			item_group,
		})
	}
	function updateItem(name, values) {
		return updateItemResource.submit({ name, values_json: JSON.stringify(values) })
	}
	function deleteItem(name) {
		return deleteItemResource.submit({ name })
	}
	function getItem(name) {
		return getItemResource.submit({ name })
	}

	// Item Group CRUD
	function createItemGroup(values) {
		return createItemGroupResource.submit({ values_json: JSON.stringify(values) })
	}
	function updateItemGroup(name, values) {
		return updateItemGroupResource.submit({ name, values_json: JSON.stringify(values) })
	}
	function deleteItemGroup(name) {
		return deleteItemGroupResource.submit({ name })
	}

	// Brand CRUD
	function createBrand(values) {
		return createBrandResource.submit({ values_json: JSON.stringify(values) })
	}
	function updateBrand(name, values) {
		return updateBrandResource.submit({ name, values_json: JSON.stringify(values) })
	}
	function deleteBrand(name) {
		return deleteBrandResource.submit({ name })
	}

	// Warehouse CRUD
	function createWarehouse(values) {
		return createWarehouseResource.submit({ values_json: JSON.stringify(values) })
	}
	function updateWarehouse(name, values) {
		return updateWarehouseResource.submit({ name, values_json: JSON.stringify(values) })
	}
	function deleteWarehouse(name) {
		return deleteWarehouseResource.submit({ name })
	}

	// Lookup helpers
	function loadItemGroupsForSelect(parent, is_group) {
		return itemGroupsForSelectResource.submit({ parent, is_group })
	}
	function loadWarehousesForSelect(parent) {
		return warehousesForSelectResource.submit({ parent })
	}
	function loadItemsInGroup(item_group) {
		return itemsInGroupResource.submit({ item_group })
	}
	function loadItemsForBrand(brand) {
		return itemsForBrandResource.submit({ brand })
	}

	// Catalog vendors
	function loadCatalogVendors(params = {}) {
		return catalogVendorsResource.submit(params)
	}
	function loadCatalogItems(params = {}) {
		return catalogItemsResource.submit(params)
	}

	return {
		// state
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
		catalogVendors,
		catalogVendorsTotal,

		// read resources
		supplierOrdersResource,
		orderDetailResource,
		memosResource,
		assembliesResource,
		metalsResource,
		gemsResource,
		warehousesResource,
		warehouseDetailResource,
		categoriesResource,
		brandsResource,
		collectionsResource,
		suppliersResource,
		catalogVendorsResource,
		catalogItemsResource,
		itemsInGroupResource,
		itemsForBrandResource,

		// existing write resources
		createPOResource,
		submitPOResource,
		cancelPOResource,
		createMemoResource,
		receiveMemoResource,
		createAssemblyResource,
		disassembleResource,
		submitAssemblyResource,
		assemblyDetailResource,

		// new CRUD resources
		createItemResource,
		updateItemResource,
		deleteItemResource,
		getItemResource,
		createItemGroupResource,
		updateItemGroupResource,
		deleteItemGroupResource,
		createBrandResource,
		updateBrandResource,
		deleteBrandResource,
		createWarehouseResource,
		updateWarehouseResource,
		deleteWarehouseResource,
		itemGroupsForSelectResource,
		warehousesForSelectResource,

		// loaders
		loadSupplierOrders,
		loadOrderDetail,
		loadMemos,
		loadAssemblies,
		loadAssemblyDetail,
		loadMetals,
		loadGems,
		loadWarehouses,
		loadWarehouseDetail,
		loadCategories,
		loadBrands,
		loadCollections,
		loadSuppliers,
		loadItemsInGroup,
		loadItemsForBrand,
		loadCatalogVendors,
		loadCatalogItems,

		// write actions
		createPO,
		submitPO,
		cancelPO,
		createMemo,
		receiveMemo,
		createAssembly,
		disassemble,
		submitAssembly,
		createItem,
		updateItem,
		deleteItem,
		getItem,
		createItemGroup,
		updateItemGroup,
		deleteItemGroup,
		createBrand,
		updateBrand,
		deleteBrand,
		createWarehouse,
		updateWarehouse,
		deleteWarehouse,
		loadItemGroupsForSelect,
		loadWarehousesForSelect,
	}
})
