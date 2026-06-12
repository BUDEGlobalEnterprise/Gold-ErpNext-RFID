# Copyright (c) 2026, Zevar and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class DisplayCase(Document):
	def validate(self):
		self.set_zone_type_from_warehouse()
		self.update_stats()

	def on_trash(self):
		if self.item_count > 0:
			frappe.throw(
				_("Cannot delete display case {0} because it still has {1} items.").format(
					frappe.bold(self.case_name), frappe.bold(self.item_count)
				)
			)

	def set_zone_type_from_warehouse(self):
		"""Auto-populate zone_type from warehouse name pattern."""
		if not self.warehouse:
			return

		wh_name = self.warehouse.lower()
		if "showcase" in wh_name:
			self.zone_type = "Showcase"
		elif "back stock" in wh_name or "backstock" in wh_name:
			self.zone_type = "Back Stock"
		elif "safe" in wh_name:
			self.zone_type = "Safe"
		elif "reserved" in wh_name:
			self.zone_type = "Reserved"
		elif "quarantine" in wh_name:
			self.zone_type = "Quarantine"
		elif "transit" in wh_name:
			self.zone_type = "Transit"

	def update_stats(self):
		"""Update cached item count and total value for this case."""
		if not self.warehouse:
			self.item_count = 0
			self.total_value = 0.0
			return

		stats = frappe.db.sql(
			"""
			SELECT
				COUNT(DISTINCT item_code) as item_count,
				SUM(actual_qty * valuation_rate) as total_value
			FROM `tabBin`
			WHERE warehouse = %s AND actual_qty > 0
		""",
			(self.warehouse,),
			as_dict=True,
		)

		if stats:
			self.item_count = stats[0].item_count or 0
			self.total_value = stats[0].total_value or 0.0
