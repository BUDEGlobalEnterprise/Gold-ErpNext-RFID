import frappe
import json
from frappe.utils import flt, cint

@frappe.whitelist(allow_guest=False)
def get_live_quote(metal_type=None, metal_purity=None, metal_weight=None, stones=None, labor_cost=None, overhead_cost=None, margin_percent=None, **kwargs):
	if isinstance(stones, str):
		try:
			stones = json.loads(stones)
		except Exception:
			stones = []
	if not stones:
		stones = []

	weight_g = flt(metal_weight) or flt(kwargs.get("weight_g"))
	labor_cost = flt(labor_cost)
	overhead_cost = flt(overhead_cost)
	margin_percent = flt(margin_percent)

	# Mocked live quoting logic based on payload
	metal_cost = weight_g * 85.0
	stone_cost = sum([flt(s.get("carat_weight", s.get("carat", 0))) * flt(s.get("unit_price", 0)) for s in stones])
	
	subtotal = metal_cost + stone_cost + labor_cost + overhead_cost
	total = subtotal * (1 + margin_percent / 100.0)

	return {
		"metal_cost": metal_cost,
		"stone_cost": stone_cost,
		"labor_cost": labor_cost,
		"overhead_cost": overhead_cost,
		"subtotal": subtotal,
		"margin": total - subtotal,
		"total": total
	}

@frappe.whitelist(allow_guest=False)
def create_special_order(payload=None, **kwargs):
	"""
	API endpoint for the Special Order Wizard to create a Special Order
	along with its linked Job Bag.
	"""
	if not payload:
		payload = kwargs
	elif isinstance(payload, str):
		try:
			payload = json.loads(payload)
		except Exception:
			payload = kwargs

	customer = payload.get("customer")
	if not customer:
		frappe.throw("Customer is mandatory for a Special Order. Please select a customer.")

	so = frappe.get_doc({
		"doctype": "Zevar Special Order",
		"customer": customer,
		"ring_size": payload.get("ring_size"),
		"metal_type": payload.get("metal_type"),
		"metal_purity": payload.get("metal_purity"),
		"estimated_weight_grams": payload.get("metal_weight"),
		"estimated_total_price": payload.get("grand_total"),
		"workflow_status": "Draft",
	})

	stones = payload.get("stones", [])
	if isinstance(stones, str):
		stones = json.loads(stones)

	for stone in stones:
		sourcing = stone.get("sourcingMethod") or stone.get("sourcing_method") or "In-House"
		item_code = stone.get("item_code") or stone.get("stone_id") or ""
		serial_no = stone.get("serial_no")
		supplier_id = stone.get("supplierId") or stone.get("supplier_id")
		unit_price = stone.get("unit_price") or stone.get("unitPrice") or 0

		# If sourcing requires an item and none is provided, generate a dummy item
		if sourcing == "Memo Request" and not item_code:
			item_code = f"CUST-STONE-{frappe.generate_hash(length=6)}"
			try:
				frappe.get_doc({
					"doctype": "Item",
					"item_code": item_code,
					"item_name": f"Custom {stone.get('shape', '')} {stone.get('caratWeight', '')}ct",
					"item_group": "Products",
					"is_stock_item": 0,
					"stock_uom": "Nos",
				}).insert(ignore_permissions=True)
			except Exception:
				pass

		so.append("stones", {
			"stone_item_code": item_code,
			"shape": stone.get("shape") or "",
			"carat_weight": stone.get("caratWeight") or stone.get("carat") or 0,
			"clarity": stone.get("clarity") or "",
			"color": stone.get("color") or "",
			"sourcing_method": sourcing,
		})

		if sourcing == "In-Stock" and serial_no:
			try:
				from zevar_core.api.inventory_v2 import acquire_inventory_lock
				acquire_inventory_lock(serial_no=serial_no, lock_owner=f"Special Order {so.name}")
			except Exception:
				pass
		elif sourcing == "Memo Request" and supplier_id:
			try:
				from zevar_core.api.memo import create_memo
				create_memo({
					"memo_class": "Vendor Memo",
					"vendor": supplier_id,
					"items": [{
						"item_code": item_code,
						"qty": 1,
						"memo_price": flt(unit_price),
					}],
					"notes": f"Auto-generated for Special Order {so.name}",
				})
			except Exception as e:
				frappe.log_error(title=f"Failed to create memo for SO {so.name}", message=frappe.get_traceback())

	so.insert(ignore_permissions=True)

	jb = frappe.get_doc({
		"doctype": "Zevar Job Bag",
		"special_order": so.name,
	})
	jb.insert(ignore_permissions=True)

	frappe.db.commit()

	return {"status": "success", "order_id": so.name, "job_bag": jb.name}

@frappe.whitelist(allow_guest=False)
def get_job_bag_list(status=None):
	"""Return a list of Job Bag cards for the Shop Floor Kanban."""
	filters = {"docstatus": ["!=", 2]}
	if status and status != "all":
		filters["status"] = status

	jobs = frappe.get_all(
		"Zevar Job Bag",
		filters=filters,
		fields=["name", "special_order", "status", "custom_order_number",
				"custom_priority", "custom_assigned_to", "custom_due_date",
				"custom_item_description", "customer_name", "customer"],
		order_by="modified desc",
	)

	# Enrich with Special Order data
	for job in jobs:
		if not job.get("customer") or not job.get("customer_name"):
			so = frappe.db.get_value(
				"Zevar Special Order",
				job.special_order,
				["customer", "customer_name", "custom_item_description"],
				as_dict=True,
			)
			if so:
				job.update({
					"customer": so.customer,
					"customer_name": so.customer_name,
					"custom_item_description": so.custom_item_description,
				})
		if not job.get("custom_priority"):
			job["custom_priority"] = ""
		if not job.get("custom_due_date"):
			job["custom_due_date"] = ""
		if not job.get("custom_item_description"):
			job["custom_item_description"] = "Special Order"

	return jobs

@frappe.whitelist(allow_guest=False, methods=["POST"])
def update_job_status(job_name, new_status):
	"""Update the workflow status of a Job Bag (used by Kanban drag-and-drop)."""
	job = frappe.get_doc("Zevar Job Bag", job_name)
	job.status = new_status
	job.save(ignore_permissions=True)
	frappe.db.commit()
	return {"status": "success", "name": job.name, "new_status": new_status}

@frappe.whitelist(allow_guest=False)
def get_memo_suppliers():
	"""Return a list of suppliers for the Memo Request stone sourcing."""
	suppliers = frappe.get_all(
		"Supplier",
		filters={"disabled": 0},
		fields=["name", "supplier_name"],
		order_by="supplier_name asc",
	)
	return [{"value": s.name, "label": s.supplier_name} for s in suppliers]

def on_special_order_validate(doc, method=None):
	"""
	Fetches default ring size via Jewel360 logic.
	Generates estimated_total_price via PIRO BOM logic.
	Triggered on 'validate' of Zevar Special Order.
	"""
	if doc.customer and not doc.ring_size:
		# Mocking the Jewel360 logic.
		customer_doc = frappe.get_doc("Customer", doc.customer)
		if hasattr(customer_doc, "custom_ring_size") and customer_doc.custom_ring_size:
			doc.ring_size = customer_doc.custom_ring_size
		else:
			doc.ring_size = "7"
			
	# Mocking the PIRO BOM logic
	if not doc.estimated_total_price:
		# We can call the get_live_quote logic
		quote = get_live_quote(
			metal_type=doc.metal_type,
			purity=doc.metal_purity,
			weight_g=doc.estimated_weight_grams,
			stones=[s.as_dict() for s in doc.stones] if doc.stones else []
		)
		doc.estimated_total_price = quote["total"]

def generate_job_bag_barcode(doc, method=None):
	"""
	Auto-generates a Code128 string on save.
	Triggered on 'before_save' of Zevar Job Bag.
	"""
	if not doc.barcode:
		# Generate a Code128 string
		# E.g., combining 'JB' and the order it's linked to, or just a timestamp/hash
		import time
		doc.barcode = f"128-JB-{int(time.time())}"

@frappe.whitelist(allow_guest=True)
def track_special_order(order_id):
	"""
	Guest-accessible tracking API. Returns minimal status info.
	Requires exact Order ID.
	"""
	if not order_id:
		return {"error": "Order ID is required."}
		
	# Zevar Special Order ID format is typically SPO-XXXX
	try:
		so = frappe.get_doc("Zevar Special Order", order_id)
		# Don't expose pricing or full details to guests
		return {
			"status": "success",
			"order_id": so.name,
			"customer_name": f"{so.customer_name[0]}***" if so.customer_name else "Unknown",
			"metal_type": so.metal_type,
			"workflow_status": so.workflow_status or "Draft",
			"creation": so.creation,
			"modified": so.modified
		}
	except frappe.DoesNotExistError:
		return {"error": "Order not found. Please check your Order ID."}
	except Exception as e:
		return {"error": str(e)}
