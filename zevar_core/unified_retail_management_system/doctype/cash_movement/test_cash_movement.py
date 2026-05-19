import unittest
import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt
from zevar_core.tests.utils import ensure_pos_profile

erpnext_required = unittest.skipUnless(
	frappe.db and frappe.db.exists("DocType", "POS Profile"),
	"ERPNext required (POS Profile DocType not found)",
)

@erpnext_required
class TestCashMovement(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.test_profile = "Test POS Profile"
		cls.test_profile = ensure_pos_profile(
			profile_name=cls.test_profile,
			warehouse_name="Test Cash Movement Warehouse",
		)

	def setUp(self):
		frappe.set_user("Administrator")
		self._cleanup_sessions()
		
		# Dynamically determine the required opening balance based on POS Profile settings
		profile = frappe.get_doc("POS Profile", self.test_profile)
		opening_balance = 100.00
		if profile.get("custom_enforce_fixed_float"):
			opening_balance = flt(profile.get("custom_fixed_opening_float", 300.0))

		# Open a test session
		from zevar_core.api.pos_session import open_pos_session
		result = open_pos_session(
			pos_profile=self.test_profile,
			opening_balance=opening_balance,
		)
		self.session_name = result.get("session_name")

	def tearDown(self):
		self._cleanup_sessions()
		frappe.set_user("Administrator")

	def _cleanup_sessions(self):
		"""Clean up test sessions"""
		sessions = frappe.get_all(
			"POS Opening Entry",
			filters={"user": "Administrator", "status": "Open"},
			fields=["name", "docstatus"],
		)
		for session in sessions:
			try:
				doc = frappe.get_doc("POS Opening Entry", session.name)
				if doc.docstatus == 1:
					doc.cancel()
				frappe.delete_doc("POS Opening Entry", session.name, ignore_permissions=True)
			except Exception:
				pass

	def test_cash_out_creates_movement(self):
		from zevar_core.api.pos_session import record_cash_movement
		result = record_cash_movement(
			session_name=self.session_name,
			movement_type="Cash Out",
			amount=50.0,
			reason="Petty Cash"
		)
		self.assertTrue(result.get("success"))

	def test_cash_out_over_100_requires_manager(self):
		from zevar_core.api.pos_session import record_cash_movement
		# Cash out over 100 without manager pin should raise ValidationError
		with self.assertRaises(frappe.ValidationError):
			record_cash_movement(
				session_name=self.session_name,
				movement_type="Cash Out",
				amount=200.0,
				reason="Bank Drop"
			)
