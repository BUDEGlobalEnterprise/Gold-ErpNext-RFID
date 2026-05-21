# Copyright (c) 2026, Zevar Core
# License: GNU General Public License v3.0

"""
Multi-store enforcement tests.

Verifies that a cashier in store A cannot read or write inventory belonging
to store B. Manager-class roles bypass and may operate across all stores.

Covers:
- get_user_allowed_warehouses
- assert_pos_warehouse_access
- get_pos_items (catalog read path) refuses cross-store warehouse
"""

import frappe
from frappe.tests.utils import FrappeTestCase

from zevar_core.tests.utils import ensure_pos_profile, ensure_warehouse


def _ensure_pos_user(email: str, role: str = "Sales User") -> str:
	"""Create or return a non-admin user with a single POS-related role."""
	if not frappe.db.exists("User", email):
		user = frappe.new_doc("User")
		user.email = email
		user.first_name = "Zevar"
		user.last_name = "Cashier"
		user.send_welcome_email = 0
		user.enabled = 1
		user.user_type = "System User"
		user.insert(ignore_permissions=True)

	user_doc = frappe.get_doc("User", email)
	{r.role for r in (user_doc.roles or [])}
	# Remove System Manager / Sales Manager / Store Manager / etc that would
	# bypass our check; ensure only the intended single role is present.
	user_doc.roles = []
	user_doc.append("roles", {"role": role})
	user_doc.save(ignore_permissions=True)
	return email


def _assign_user_to_pos_profile(profile_name: str, email: str) -> None:
	"""Add `email` to the profile's applicable_for_users child table if missing."""
	profile = frappe.get_doc("POS Profile", profile_name)
	if any(u.user == email for u in (profile.applicable_for_users or [])):
		return
	profile.append("applicable_for_users", {"user": email})
	# The test fixture profile was inserted with ignore_mandatory because it
	# omits write_off_account / write_off_cost_center; we have to keep that
	# bypass when re-saving or the validator will trip on those fields.
	profile.flags.ignore_mandatory = True
	profile.save(ignore_permissions=True)


class TestUserAllowedWarehouses(FrappeTestCase):
	"""get_user_allowed_warehouses returns the right scope per user."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		frappe.set_user("Administrator")

		cls.allowed_wh = ensure_warehouse("Zevar MS Allowed Warehouse")
		cls.foreign_wh = ensure_warehouse("Zevar MS Foreign Warehouse")
		cls.profile = ensure_pos_profile(
			profile_name="Zevar Multistore Test Profile",
			warehouse_name="Zevar MS Allowed Warehouse",
		)

		cls.cashier = _ensure_pos_user("zevar_ms_cashier@example.com")
		_assign_user_to_pos_profile(cls.profile, cls.cashier)

		cls.unassigned = _ensure_pos_user("zevar_ms_unassigned@example.com")

		frappe.db.commit()

	def setUp(self):
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")

	def test_admin_is_unrestricted(self):
		"""Administrator (and other manager-class roles) returns None."""
		from zevar_core.api.permissions import get_user_allowed_warehouses

		self.assertIsNone(get_user_allowed_warehouses("Administrator"))

	def test_cashier_sees_only_assigned_warehouse(self):
		"""A non-admin user with a POS profile sees that profile's warehouse."""
		from zevar_core.api.permissions import get_user_allowed_warehouses

		allowed = get_user_allowed_warehouses(self.cashier)
		self.assertIsNotNone(allowed)
		self.assertIn(self.allowed_wh, allowed)
		self.assertNotIn(self.foreign_wh, allowed)

	def test_unassigned_user_sees_nothing(self):
		"""A non-admin without any POS profile assignment is locked out."""
		from zevar_core.api.permissions import get_user_allowed_warehouses

		allowed = get_user_allowed_warehouses(self.unassigned)
		self.assertEqual(allowed, [])


class TestAssertPosWarehouseAccess(FrappeTestCase):
	"""assert_pos_warehouse_access throws on cross-store warehouses."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		frappe.set_user("Administrator")

		cls.allowed_wh = ensure_warehouse("Zevar MS Allowed Warehouse")
		cls.foreign_wh = ensure_warehouse("Zevar MS Foreign Warehouse")
		cls.profile = ensure_pos_profile(
			profile_name="Zevar Multistore Test Profile",
			warehouse_name="Zevar MS Allowed Warehouse",
		)
		cls.cashier = _ensure_pos_user("zevar_ms_cashier@example.com")
		_assign_user_to_pos_profile(cls.profile, cls.cashier)
		frappe.db.commit()

	def setUp(self):
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")

	def test_admin_bypasses_check(self):
		"""Manager-class roles never raise."""
		from zevar_core.api.permissions import assert_pos_warehouse_access

		# Should not raise.
		assert_pos_warehouse_access(self.foreign_wh, user="Administrator")

	def test_cashier_allowed_warehouse_passes(self):
		"""A cashier's own warehouse is permitted."""
		from zevar_core.api.permissions import assert_pos_warehouse_access

		assert_pos_warehouse_access(self.allowed_wh, user=self.cashier)

	def test_cashier_foreign_warehouse_throws(self):
		"""A cashier accessing another store's warehouse hits PermissionError."""
		from zevar_core.api.permissions import assert_pos_warehouse_access

		with self.assertRaises(frappe.PermissionError):
			assert_pos_warehouse_access(self.foreign_wh, user=self.cashier)

	def test_empty_warehouse_is_noop(self):
		"""Falsy warehouse short-circuits without throwing."""
		from zevar_core.api.permissions import assert_pos_warehouse_access

		# None and "" must both be safe.
		assert_pos_warehouse_access(None, user=self.cashier)
		assert_pos_warehouse_access("", user=self.cashier)


class TestCatalogMultiStoreEnforcement(FrappeTestCase):
	"""get_pos_items refuses to read another store's inventory."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		frappe.set_user("Administrator")

		cls.allowed_wh = ensure_warehouse("Zevar MS Allowed Warehouse")
		cls.foreign_wh = ensure_warehouse("Zevar MS Foreign Warehouse")
		cls.profile = ensure_pos_profile(
			profile_name="Zevar Multistore Test Profile",
			warehouse_name="Zevar MS Allowed Warehouse",
		)
		cls.cashier = _ensure_pos_user("zevar_ms_cashier@example.com")
		_assign_user_to_pos_profile(cls.profile, cls.cashier)
		frappe.db.commit()

	def setUp(self):
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")

	def test_admin_can_read_any_warehouse(self):
		"""Admin doesn't get blocked by the multi-store check."""
		from zevar_core.api.catalog import get_pos_items

		# Should not raise. Result list is fine to be empty.
		result = get_pos_items(warehouse=self.foreign_wh, page_length=5)
		self.assertIsInstance(result, list)

	def test_cashier_blocked_from_foreign_warehouse(self):
		"""A non-admin cashier hits PermissionError on a foreign warehouse."""
		from zevar_core.api.catalog import get_pos_items

		try:
			frappe.set_user(self.cashier)
			with self.assertRaises(frappe.PermissionError):
				get_pos_items(warehouse=self.foreign_wh, page_length=5)
		finally:
			frappe.set_user("Administrator")

	def test_cashier_can_read_own_warehouse(self):
		"""A non-admin cashier can read their own store's catalog."""
		from zevar_core.api.catalog import get_pos_items

		try:
			frappe.set_user(self.cashier)
			result = get_pos_items(warehouse=self.allowed_wh, page_length=5)
			self.assertIsInstance(result, list)
		finally:
			frappe.set_user("Administrator")
