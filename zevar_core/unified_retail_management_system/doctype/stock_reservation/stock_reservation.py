import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class StockReservation(Document):
	def validate(self):
		if self.serial_no:
			sn = frappe.get_cached_value(
				"Serial No", self.serial_no, ["warehouse", "item_code", "item_name"], as_dict=True
			)
			if not sn or not sn.warehouse:
				frappe.throw(_("Serial No {0} is not in any warehouse").format(self.serial_no))

			existing = frappe.db.exists(
				"Stock Reservation",
				{
					"serial_no": self.serial_no,
					"status": "Active",
					"name": ["!=", self.name],
					"docstatus": 1,
				},
			)
			if existing:
				frappe.throw(
					_("Serial No {0} already has an active reservation: {1}").format(self.serial_no, existing)
				)

			self.item_code = sn.item_code
			self.item_name = sn.item_name

	def on_submit(self):
		from zevar_core.services.inventory_events import transfer_serial

		sn_doc = frappe.get_doc("Serial No", self.serial_no)
		self.warehouse_from = sn_doc.warehouse

		company = frappe.defaults.get_user_default("company") or "Zevar Jewelers"
		abbr = frappe.get_cached_value("Company", company, "abbr") or "Z"

		parent_wh = frappe.db.get_value("Warehouse", sn_doc.warehouse, "parent_warehouse")
		store_root = parent_wh or sn_doc.warehouse

		parts = store_root.split(" - ")
		store_code = parts[0].strip() if parts else "NY-01"

		reserved_wh = f"Reserved {store_code} - {abbr}"
		if not frappe.db.exists("Warehouse", reserved_wh):
			reserved_wh = store_root
		self.warehouse_to = reserved_wh

		se = transfer_serial(
			serial_no=self.serial_no,
			item_code=self.item_code,
			from_warehouse=self.warehouse_from,
			to_warehouse=reserved_wh,
			reference_doctype="Stock Reservation",
			reference_name=self.name,
		)
		self.stock_entry_ref = se.name

		frappe.db.set_value(
			"Serial No",
			self.serial_no,
			{
				"custom_reserved_for_customer": self.customer,
				"custom_reserved_until": self.hold_until,
			},
		)

		self._log_event(
			"piece_reserved", f"Reserved {self.serial_no} for {self.customer} until {self.hold_until}"
		)

	def on_cancel(self):
		if self.status == "Active" and self.stock_entry_ref:
			from zevar_core.services.inventory_events import transfer_serial

			transfer_serial(
				serial_no=self.serial_no,
				item_code=self.item_code,
				from_warehouse=self.warehouse_to,
				to_warehouse=self.warehouse_from,
				reference_doctype="Stock Reservation",
				reference_name=self.name,
			)
			frappe.db.set_value(
				"Serial No",
				self.serial_no,
				{
					"custom_reserved_for_customer": None,
					"custom_reserved_until": None,
				},
			)
			self._log_event("reservation_expired", f"Reservation {self.name} cancelled, stock returned")

		self.status = "Cancelled"
		self.db_set("status", "Cancelled")

	def _log_event(self, event_type, details):
		log = frappe.new_doc("POS Audit Log")
		log.user = frappe.session.user
		log.event_type = event_type
		log.category = "Inventory"
		log.reference_type = "Stock Reservation"
		log.reference_document = self.name
		log.details = details
		log.insert(ignore_permissions=True)
