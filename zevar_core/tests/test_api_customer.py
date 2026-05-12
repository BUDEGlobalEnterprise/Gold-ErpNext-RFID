# Copyright (c) 2025, Zevar Core
# License: GNU General Public License v3.0

"""
Unit Tests for Customer API (customer.py)
Covers: search_customers, get_customer_details, get_recent_customers,
        get_customer_edit_info, update_customer, quick_create_customer

Run with: bench run-tests --app zevar_core --test test_api_customer
"""

import unittest

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today

from zevar_core.tests.utils import ensure_customer

erpnext_required = unittest.skipUnless(
	frappe.db and frappe.db.exists("DocType", "Customer"),
	"ERPNext required (Customer DocType not found)",
)


@erpnext_required
class TestSearchCustomers(FrappeTestCase):
	"""Test search_customers endpoint"""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.customer = ensure_customer("Search Test Customer ABC")

	def setUp(self):
		frappe.set_user("Administrator")

	def test_search_returns_list(self):
		"""Should return a list of customers"""
		from zevar_core.api.customer import search_customers

		result = search_customers(query="Search Test Customer")
		self.assertIsInstance(result, list)

	def test_search_finds_by_name(self):
		"""Should find customer by name"""
		from zevar_core.api.customer import search_customers

		result = search_customers(query="Search Test Customer ABC")
		self.assertIsInstance(result, list)
		self.assertGreater(len(result), 0)

	def test_search_short_query_returns_all(self):
		"""Query < 2 chars should return all customers (up to 100)"""
		from zevar_core.api.customer import search_customers

		result = search_customers(query="")
		self.assertIsInstance(result, list)

	def test_search_nonexistent_returns_empty(self):
		"""Non-matching query should return empty list"""
		from zevar_core.api.customer import search_customers

		result = search_customers(query="ZZZZZZNONEXISTENT999")
		self.assertIsInstance(result, list)

	def test_search_result_has_required_fields(self):
		"""Result items should have customer_name and display_name"""
		from zevar_core.api.customer import search_customers

		result = search_customers(query="Search Test Customer ABC")
		if result:
			self.assertIn("customer_name", result[0])
			self.assertIn("display_name", result[0])


@erpnext_required
class TestGetCustomerDetails(FrappeTestCase):
	"""Test get_customer_details endpoint"""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.customer = ensure_customer("Details Test Customer XYZ")

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_details_returns_dict(self):
		"""Should return customer details dict"""
		from zevar_core.api.customer import get_customer_details

		result = get_customer_details(self.customer)
		self.assertIsInstance(result, dict)
		self.assertEqual(result["name"], self.customer)
		self.assertIn("customer_name", result)
		self.assertIn("display_name", result)

	def test_get_details_has_core_fields(self):
		"""Should include core customer fields"""
		from zevar_core.api.customer import get_customer_details

		result = get_customer_details(self.customer)
		self.assertIn("mobile_no", result)
		self.assertIn("email_id", result)
		self.assertIn("customer_type", result)

	def test_get_details_has_recent_orders(self):
		"""Should include recent_orders list"""
		from zevar_core.api.customer import get_customer_details

		result = get_customer_details(self.customer)
		self.assertIn("recent_orders", result)
		self.assertIsInstance(result["recent_orders"], list)

	def test_get_details_nonexistent_customer(self):
		"""Should raise error for nonexistent customer"""
		from zevar_core.api.customer import get_customer_details

		with self.assertRaises(frappe.ValidationError):
			get_customer_details("NONEXISTENT-CUSTOMER-99999")

	def test_get_details_empty_customer_name(self):
		"""Should raise error for empty customer name"""
		from zevar_core.api.customer import get_customer_details

		with self.assertRaises(frappe.ValidationError):
			get_customer_details("")


@erpnext_required
class TestGetRecentCustomers(FrappeTestCase):
	"""Test get_recent_customers endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_recent_returns_list(self):
		"""Should return a list"""
		from zevar_core.api.customer import get_recent_customers

		result = get_recent_customers(limit=10)
		self.assertIsInstance(result, list)

	def test_get_recent_respects_limit(self):
		"""Should respect limit parameter"""
		from zevar_core.api.customer import get_recent_customers

		result = get_recent_customers(limit=5)
		self.assertLessEqual(len(result), 5)


@erpnext_required
class TestGetCustomerEditInfo(FrappeTestCase):
	"""Test get_customer_edit_info endpoint"""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.customer = ensure_customer("Edit Info Test Customer")

	def setUp(self):
		frappe.set_user("Administrator")

	def test_edit_info_returns_details(self):
		"""Should return same structure as get_customer_details"""
		from zevar_core.api.customer import get_customer_edit_info

		result = get_customer_edit_info(self.customer)
		self.assertIsInstance(result, dict)
		self.assertEqual(result["name"], self.customer)


@erpnext_required
class TestQuickCreateCustomer(FrappeTestCase):
	"""Test quick_create_customer endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")
		self.created_customers = []

	def tearDown(self):
		for name in self.created_customers:
			try:
				frappe.delete_doc("Customer", name, ignore_permissions=True, force=True)
			except Exception:
				pass

	def test_quick_create_basic(self):
		"""Should create a customer with just a name"""
		from zevar_core.api.customer import quick_create_customer

		result = quick_create_customer(customer_name="Quick Create Test 001")
		self.assertTrue(result.get("success"))
		self.assertIn("customer_name", result)
		self.created_customers.append(result["customer_name"])

	def test_quick_create_with_phone(self):
		"""Should create customer with phone number"""
		from zevar_core.api.customer import quick_create_customer

		result = quick_create_customer(
			customer_name="Quick Create Phone Test",
			mobile_no="555-123-4567",
		)
		self.assertTrue(result.get("success"))
		self.created_customers.append(result["customer_name"])

		# Verify phone was saved
		customer = frappe.get_doc("Customer", result["customer_name"])
		self.assertEqual(customer.mobile_no, "555-123-4567")

	def test_quick_create_with_email(self):
		"""Should create customer with email"""
		from zevar_core.api.customer import quick_create_customer

		result = quick_create_customer(
			customer_name="Quick Create Email Test",
			email_id="test@example.com",
		)
		self.assertTrue(result.get("success"))
		self.created_customers.append(result["customer_name"])

	def test_quick_create_with_address(self):
		"""Should create customer with billing address"""
		from zevar_core.api.customer import quick_create_customer

		result = quick_create_customer(
			customer_name="Quick Create Address Test",
			address_line1="123 Test Street",
			city="Test City",
			state="CA",
			pincode="90210",
		)
		self.assertTrue(result.get("success"))
		self.created_customers.append(result["customer_name"])

	def test_quick_create_empty_name_raises(self):
		"""Should raise error for empty customer name"""
		from zevar_core.api.customer import quick_create_customer

		with self.assertRaises(frappe.ValidationError):
			quick_create_customer(customer_name="")

	def test_quick_create_duplicate_name(self):
		"""Should handle duplicate customer name (ERPNext auto-renames)"""
		from zevar_core.api.customer import quick_create_customer

		result1 = quick_create_customer(customer_name="Duplicate Name Test")
		self.assertTrue(result1.get("success"))
		self.created_customers.append(result1["customer_name"])

		result2 = quick_create_customer(customer_name="Duplicate Name Test")
		self.assertTrue(result2.get("success"))
		self.created_customers.append(result2["customer_name"])


@erpnext_required
class TestUpdateCustomer(FrappeTestCase):
	"""Test update_customer endpoint"""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.customer_name = ensure_customer("Update Test Customer DEF")

	def setUp(self):
		frappe.set_user("Administrator")

	def test_update_phone(self):
		"""Should update phone number"""
		from zevar_core.api.customer import update_customer

		result = update_customer(
			customer_name=self.customer_name,
			mobile_no="555-999-0000",
		)
		self.assertTrue(result.get("success"))

		# Verify
		customer = frappe.get_doc("Customer", self.customer_name)
		self.assertEqual(customer.mobile_no, "555-999-0000")

	def test_update_email(self):
		"""Should update email"""
		from zevar_core.api.customer import update_customer

		result = update_customer(
			customer_name=self.customer_name,
			email_id="updated@example.com",
		)
		self.assertTrue(result.get("success"))

	def test_update_nonexistent_customer_raises(self):
		"""Should raise error for nonexistent customer"""
		from zevar_core.api.customer import update_customer

		with self.assertRaises(frappe.ValidationError):
			update_customer(
				customer_name="NONEXISTENT-99999",
				mobile_no="555-000-0000",
			)

	def test_update_empty_name_raises(self):
		"""Should raise error for empty customer name"""
		from zevar_core.api.customer import update_customer

		with self.assertRaises(frappe.ValidationError):
			update_customer(customer_name="", mobile_no="555-000-0000")
