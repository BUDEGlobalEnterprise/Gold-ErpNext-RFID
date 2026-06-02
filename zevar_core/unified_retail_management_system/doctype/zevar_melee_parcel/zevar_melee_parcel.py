import frappe
from frappe.model.document import Document
from frappe.utils import flt


class ZevarMeleeParcel(Document):
	def validate(self):
		if self.stone_count and self.stone_count > 0:
			self.avg_per_stone = flt(self.total_carats / self.stone_count, 4)
