"""
Unit Tests for Commission Calculation, Gift Card Lifecycle, and Pricing Engine

Covers:
- R3: Commission calculation (Flat Rate, By Discount Range, By Profit Margin, By Sale Amount)
- R4: Gift Card lifecycle (issue, partial redeem, full redeem, expiry, balance check)
- R15: Pricing engine (MSRP priority, calculated price fallback, standard rate fallback)
"""

import json
import unittest

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, add_months, flt, today

from zevar_core.tests.utils import (
	ensure_customer,
	ensure_item,
	ensure_item_group,
	ensure_warehouse,
)

erpnext_required = unittest.skipUnless(
	frappe.db and frappe.db.exists("DocType", "Sales Invoice"),
	"ERPNext required (Sales Invoice DocType not found)",
)


def _create_test_employee(first_name: str, last_name: str) -> str:
	employee = frappe.get_doc(
		{
			"doctype": "Employee",
			"first_name": first_name,
			"last_name": last_name,
			"gender": "Other",
			"date_of_birth": add_days(today(), -12000),
			"date_of_joining": today(),
		}
	).insert(ignore_permissions=True)
	return employee.name


def _create_commission_rule(
	rule_name: str,
	calculation_type: str,
	flat_rate: float | None = None,
	employee: str | None = None,
	is_default: bool = False,
	ranges: list | None = None,
) -> str:
	doc = frappe.new_doc("Commission Rule")
	doc.rule_name = rule_name
	doc.calculation_type = calculation_type
	doc.is_default = 1 if is_default else 0
	if employee:
		doc.employee = employee
	if flat_rate is not None:
		doc.flat_rate = flat_rate
	if ranges:
		for r in ranges:
			doc.append(
				"commission_ranges",
				{
					"min_value": r["min_value"],
					"max_value": r["max_value"],
					"commission_percent": r["commission_percent"],
				},
			)
	doc.insert(ignore_permissions=True)
	return doc.name


def _create_gift_card(
	customer: str,
	initial_value: float,
	source: str = "Purchase",
	expiry_date: str | None = None,
) -> str:
	doc = frappe.new_doc("Gift Card")
	doc.customer = customer
	doc.initial_value = initial_value
	doc.source = source
	doc.issue_date = today()
	if expiry_date:
		doc.expiry_date = expiry_date
	doc.insert(ignore_permissions=True)
	doc.submit()
	return doc.name


# ==========================================================================
# R3: COMMISSION CALCULATION TESTS
# ==========================================================================


@erpnext_required
class TestCommissionFlatRate(FrappeTestCase):
	"""Test Flat Rate commission calculation."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value(
			"Global Defaults", "default_company"
		)
		cls.employee_id = _create_test_employee("CommFlat", "Test")
		cls.rule_name = _create_commission_rule(
			rule_name=f"Test Flat Rate {cls.employee_id}",
			calculation_type="Flat Rate",
			flat_rate=5.0,
			employee=cls.employee_id,
		)
		cls.customer = ensure_customer("Comm Flat Customer")
		cls.warehouse = ensure_warehouse("Comm Flat Warehouse", company=cls.company)
		cls.item = ensure_item("COMM-FLAT-001", "Comm Flat Test Item", rate=1000.0)
		frappe.db.commit()

	def setUp(self):
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.db.rollback()

	def test_flat_rate_commission_on_invoice_submit(self):
		from zevar_core.api.commission import calculate_commissions
		from zevar_core.api.pos import create_pos_invoice

		result = create_pos_invoice(
			items=json.dumps([{"item_code": self.item, "qty": 1, "rate": 1000.0}]),
			payments=json.dumps([{"mode_of_payment": "Cash", "amount": 1000.0}]),
			customer=self.customer,
			warehouse=self.warehouse,
			salespersons=json.dumps([{"employee": self.employee_id, "split": 100}]),
			tax_exempt=True,
		)
		self.assertTrue(result["success"])

		splits = frappe.get_all(
			"Sales Commission Split",
			filters={"sales_invoice": result["invoice_name"], "employee": self.employee_id},
			fields=["commission_rate", "commission_amount", "sale_amount", "split_percent"],
		)
		self.assertEqual(len(splits), 1)
		self.assertEqual(flt(splits[0].commission_rate), 5.0)
		self.assertEqual(flt(splits[0].sale_amount, 2), 1000.0)
		self.assertEqual(flt(splits[0].commission_amount, 2), 50.0)
		self.assertEqual(flt(splits[0].split_percent), 100.0)

	def test_flat_rate_split_between_two_salespersons(self):
		from zevar_core.api.pos import create_pos_invoice

		emp2 = _create_test_employee("CommFlat2", "Test")
		_create_commission_rule(
			rule_name=f"Test Flat Rate {emp2}",
			calculation_type="Flat Rate",
			flat_rate=5.0,
			employee=emp2,
		)
		result = create_pos_invoice(
			items=json.dumps([{"item_code": self.item, "qty": 1, "rate": 1000.0}]),
			payments=json.dumps([{"mode_of_payment": "Cash", "amount": 1000.0}]),
			customer=self.customer,
			warehouse=self.warehouse,
			salespersons=json.dumps(
				[
					{"employee": self.employee_id, "split": 60},
					{"employee": emp2, "split": 40},
				]
			),
			tax_exempt=True,
		)
		self.assertTrue(result["success"])

		splits = frappe.get_all(
			"Sales Commission Split",
			filters={"sales_invoice": result["invoice_name"]},
			fields=["employee", "commission_rate", "commission_amount", "sale_amount"],
			order_by="employee asc",
		)
		self.assertEqual(len(splits), 2)
		for sp in splits:
			self.assertEqual(flt(sp.commission_rate), 5.0)

		sale_amounts = sorted([flt(s.sale_amount, 2) for s in splits])
		self.assertAlmostEqual(sale_amounts[0], 400.0, places=1)
		self.assertAlmostEqual(sale_amounts[1], 600.0, places=1)


@erpnext_required
class TestCommissionByDiscountRange(FrappeTestCase):
	"""Test By Discount Range commission calculation."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value(
			"Global Defaults", "default_company"
		)
		cls.employee_id = _create_test_employee("CommDisc", "Test")
		cls.rule_name = _create_commission_rule(
			rule_name=f"Test Disc Range {cls.employee_id}",
			calculation_type="By Discount Range",
			employee=cls.employee_id,
			ranges=[
				{"min_value": 0, "max_value": 10, "commission_percent": 5.0},
				{"min_value": 10.01, "max_value": 20, "commission_percent": 3.0},
				{"min_value": 20.01, "max_value": 100, "commission_percent": 1.0},
			],
		)
		cls.customer = ensure_customer("Comm Disc Customer")
		cls.warehouse = ensure_warehouse("Comm Disc Warehouse", company=cls.company)
		cls.item = ensure_item("COMM-DISC-001", "Comm Disc Test Item", rate=1000.0)
		frappe.db.commit()

	def setUp(self):
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.db.rollback()

	def test_low_discount_tier(self):
		from zevar_core.api.pos import create_pos_invoice

		result = create_pos_invoice(
			items=json.dumps([{"item_code": self.item, "qty": 1, "rate": 1000.0}]),
			payments=json.dumps([{"mode_of_payment": "Cash", "amount": 1000.0}]),
			customer=self.customer,
			warehouse=self.warehouse,
			salespersons=json.dumps([{"employee": self.employee_id, "split": 100}]),
			discount_amount=50.0,
			tax_exempt=True,
		)
		self.assertTrue(result["success"])

		splits = frappe.get_all(
			"Sales Commission Split",
			filters={"sales_invoice": result["invoice_name"]},
			fields=["commission_rate", "commission_amount"],
		)
		self.assertEqual(len(splits), 1)
		self.assertEqual(flt(splits[0].commission_rate), 5.0)

	def test_high_discount_tier(self):
		from zevar_core.api.pos import create_pos_invoice

		result = create_pos_invoice(
			items=json.dumps([{"item_code": self.item, "qty": 1, "rate": 1000.0}]),
			payments=json.dumps([{"mode_of_payment": "Cash", "amount": 1000.0}]),
			customer=self.customer,
			warehouse=self.warehouse,
			salespersons=json.dumps([{"employee": self.employee_id, "split": 100}]),
			discount_amount=250.0,
			tax_exempt=True,
		)
		self.assertTrue(result["success"])

		splits = frappe.get_all(
			"Sales Commission Split",
			filters={"sales_invoice": result["invoice_name"]},
			fields=["commission_rate"],
		)
		self.assertEqual(len(splits), 1)
		self.assertEqual(flt(splits[0].commission_rate), 1.0)


@erpnext_required
class TestCommissionByProfitMargin(FrappeTestCase):
	"""Test By Profit Margin commission calculation."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value(
			"Global Defaults", "default_company"
		)
		cls.employee_id = _create_test_employee("CommProfit", "Test")
		cls.rule_name = _create_commission_rule(
			rule_name=f"Test Profit Margin {cls.employee_id}",
			calculation_type="By Profit Margin",
			employee=cls.employee_id,
			ranges=[
				{"min_value": 0, "max_value": 20, "commission_percent": 2.0},
				{"min_value": 20.01, "max_value": 50, "commission_percent": 4.0},
				{"min_value": 50.01, "max_value": 100, "commission_percent": 6.0},
			],
		)
		cls.customer = ensure_customer("Comm Profit Customer")
		cls.warehouse = ensure_warehouse("Comm Profit Warehouse", company=cls.company)
		cls.item = ensure_item("COMM-PROFIT-001", "Comm Profit Test Item", rate=1000.0)
		frappe.db.commit()

	def setUp(self):
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.db.rollback()

	def test_profit_margin_high_tier(self):
		from zevar_core.api.pos import create_pos_invoice

		result = create_pos_invoice(
			items=json.dumps([{"item_code": self.item, "qty": 1, "rate": 1500.0}]),
			payments=json.dumps([{"mode_of_payment": "Cash", "amount": 1500.0}]),
			customer=self.customer,
			warehouse=self.warehouse,
			salespersons=json.dumps([{"employee": self.employee_id, "split": 100}]),
			tax_exempt=True,
		)
		self.assertTrue(result["success"])

		splits = frappe.get_all(
			"Sales Commission Split",
			filters={"sales_invoice": result["invoice_name"]},
			fields=["commission_rate", "commission_amount"],
		)
		self.assertEqual(len(splits), 1)
		self.assertEqual(flt(splits[0].commission_rate), 6.0)


@erpnext_required
class TestCommissionBySaleAmount(FrappeTestCase):
	"""Test By Sale Amount commission calculation."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value(
			"Global Defaults", "default_company"
		)
		cls.employee_id = _create_test_employee("CommSaleAmt", "Test")
		cls.rule_name = _create_commission_rule(
			rule_name=f"Test Sale Amount {cls.employee_id}",
			calculation_type="By Sale Amount",
			employee=cls.employee_id,
			ranges=[
				{"min_value": 0, "max_value": 500, "commission_percent": 2.0},
				{"min_value": 500.01, "max_value": 2000, "commission_percent": 3.5},
				{"min_value": 2000.01, "max_value": 10000, "commission_percent": 5.0},
			],
		)
		cls.customer = ensure_customer("Comm Sale Amt Customer")
		cls.warehouse = ensure_warehouse("Comm Sale Amt Warehouse", company=cls.company)
		cls.item = ensure_item("COMM-SALEAMT-001", "Comm Sale Amt Test Item", rate=1500.0)
		frappe.db.commit()

	def setUp(self):
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.db.rollback()

	def test_mid_sale_amount_tier(self):
		from zevar_core.api.pos import create_pos_invoice

		result = create_pos_invoice(
			items=json.dumps([{"item_code": self.item, "qty": 1, "rate": 1500.0}]),
			payments=json.dumps([{"mode_of_payment": "Cash", "amount": 1500.0}]),
			customer=self.customer,
			warehouse=self.warehouse,
			salespersons=json.dumps([{"employee": self.employee_id, "split": 100}]),
			tax_exempt=True,
		)
		self.assertTrue(result["success"])

		splits = frappe.get_all(
			"Sales Commission Split",
			filters={"sales_invoice": result["invoice_name"]},
			fields=["commission_rate", "commission_amount"],
		)
		self.assertEqual(len(splits), 1)
		self.assertEqual(flt(splits[0].commission_rate), 3.5)
		self.assertEqual(flt(splits[0].commission_amount, 2), flt(1500.0 * 3.5 / 100, 2))

	def test_high_sale_amount_tier(self):
		from zevar_core.api.pos import create_pos_invoice

		result = create_pos_invoice(
			items=json.dumps([{"item_code": self.item, "qty": 3, "rate": 1500.0}]),
			payments=json.dumps([{"mode_of_payment": "Cash", "amount": 4500.0}]),
			customer=self.customer,
			warehouse=self.warehouse,
			salespersons=json.dumps([{"employee": self.employee_id, "split": 100}]),
			tax_exempt=True,
		)
		self.assertTrue(result["success"])

		splits = frappe.get_all(
			"Sales Commission Split",
			filters={"sales_invoice": result["invoice_name"]},
			fields=["commission_rate"],
		)
		self.assertEqual(len(splits), 1)
		self.assertEqual(flt(splits[0].commission_rate), 5.0)


@erpnext_required
class TestCommissionDefaultRule(FrappeTestCase):
	"""Test default commission rule fallback when no employee-specific rule exists."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value(
			"Global Defaults", "default_company"
		)
		# Clear existing default rules
		frappe.db.sql("UPDATE `tabCommission Rule` SET is_default = 0")
		frappe.db.commit()
		cls.default_rule = _create_commission_rule(
			rule_name=f"Test Default Commission Rule {frappe.generate_hash(length=8)}",
			calculation_type="Flat Rate",
			flat_rate=3.0,
			is_default=True,
		)
		cls.employee_id = _create_test_employee("CommDefault", "Test")
		cls.customer = ensure_customer("Comm Default Customer")
		cls.warehouse = ensure_warehouse("Comm Default Warehouse", company=cls.company)
		cls.item = ensure_item("COMM-DEFAULT-001", "Comm Default Test Item", rate=500.0)
		frappe.db.commit()

	def setUp(self):
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.db.rollback()

	def test_falls_back_to_default_rule(self):
		from zevar_core.api.pos import create_pos_invoice

		result = create_pos_invoice(
			items=json.dumps([{"item_code": self.item, "qty": 1, "rate": 500.0}]),
			payments=json.dumps([{"mode_of_payment": "Cash", "amount": 500.0}]),
			customer=self.customer,
			warehouse=self.warehouse,
			salespersons=json.dumps([{"employee": self.employee_id, "split": 100}]),
			tax_exempt=True,
		)
		self.assertTrue(result["success"])

		splits = frappe.get_all(
			"Sales Commission Split",
			filters={"sales_invoice": result["invoice_name"], "employee": self.employee_id},
			fields=["commission_rate", "commission_amount"],
		)
		self.assertEqual(len(splits), 1)
		self.assertEqual(flt(splits[0].commission_rate), 3.0)
		self.assertEqual(flt(splits[0].commission_amount, 2), 15.0)


# ==========================================================================
# R4: GIFT CARD LIFECYCLE TESTS
# ==========================================================================


@erpnext_required
class TestGiftCardLifecycle(FrappeTestCase):
	"""Test full Gift Card lifecycle: issue, partial redeem, full redeem, balance check."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.customer = ensure_customer("GC Lifecycle Customer")
		frappe.db.commit()

	def setUp(self):
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.db.rollback()

	def test_issue_gift_card(self):
		gc_name = _create_gift_card(self.customer, 500.0)

		gc = frappe.get_doc("Gift Card", gc_name)
		self.assertEqual(flt(gc.balance), 500.0)
		self.assertEqual(flt(gc.initial_value), 500.0)
		self.assertEqual(gc.status, "Active")

	def test_partial_redeem(self):
		from zevar_core.api.gift_card import process_gift_card_payment

		gc_name = _create_gift_card(self.customer, 500.0)

		result = process_gift_card_payment(gc_name, 200.0)
		self.assertTrue(result["success"])
		self.assertEqual(flt(result["remaining_balance"]), 300.0)
		self.assertEqual(result["status"], "Active")

		gc = frappe.get_doc("Gift Card", gc_name)
		self.assertEqual(flt(gc.balance), 300.0)

	def test_full_redeem_marks_used(self):
		from zevar_core.api.gift_card import process_gift_card_payment

		gc_name = _create_gift_card(self.customer, 500.0)

		result = process_gift_card_payment(gc_name, 500.0)
		self.assertTrue(result["success"])
		self.assertEqual(flt(result["remaining_balance"]), 0.0)
		self.assertEqual(result["status"], "Used")

		gc = frappe.get_doc("Gift Card", gc_name)
		self.assertEqual(gc.status, "Used")

	def test_redeem_exceeds_balance_throws(self):
		from zevar_core.api.gift_card import process_gift_card_payment

		gc_name = _create_gift_card(self.customer, 100.0)

		with self.assertRaises(frappe.ValidationError):
			process_gift_card_payment(gc_name, 200.0)

	def test_balance_check_valid_card(self):
		from zevar_core.api.gift_card import get_gift_card_balance

		gc_name = _create_gift_card(self.customer, 250.0)

		result = get_gift_card_balance(gc_name)
		self.assertTrue(result["valid"])
		self.assertEqual(flt(result["balance"]), 250.0)
		self.assertEqual(flt(result["initial_value"]), 250.0)
		self.assertEqual(result["status"], "Active")

	def test_balance_check_invalid_number(self):
		from zevar_core.api.gift_card import get_gift_card_balance

		result = get_gift_card_balance("NONEXISTENT-GC-99999")
		self.assertFalse(result["valid"])

	def test_zero_payment_throws(self):
		from zevar_core.api.gift_card import process_gift_card_payment

		gc_name = _create_gift_card(self.customer, 100.0)

		with self.assertRaises(frappe.ValidationError):
			process_gift_card_payment(gc_name, 0.0)


@erpnext_required
class TestGiftCardExpiry(FrappeTestCase):
	"""Test Gift Card expiry handling."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.customer = ensure_customer("GC Expiry Customer")
		frappe.db.commit()

	def setUp(self):
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.db.rollback()

	def test_valid_future_expiry(self):
		from zevar_core.api.gift_card import get_gift_card_balance

		gc_name = _create_gift_card(self.customer, 100.0, expiry_date=add_months(today(), 6))

		result = get_gift_card_balance(gc_name)
		self.assertTrue(result["valid"])
		self.assertEqual(result["status"], "Active")

	def test_payment_on_expired_card_throws(self):
		from zevar_core.api.gift_card import process_gift_card_payment

		gc_name = _create_gift_card(self.customer, 100.0, expiry_date=add_days(today(), -1))

		with self.assertRaises(frappe.ValidationError):
			process_gift_card_payment(gc_name, 50.0)

	def test_balance_check_expired_card(self):
		from zevar_core.api.gift_card import get_gift_card_balance

		gc_name = _create_gift_card(self.customer, 100.0, expiry_date=add_days(today(), -1))

		result = get_gift_card_balance(gc_name)
		self.assertFalse(result["valid"])


# ==========================================================================
# R15: PRICING ENGINE TESTS
# ==========================================================================


@erpnext_required
class TestPricingEngineMSRP(FrappeTestCase):
	"""Test MSRP price priority (highest priority)."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		ensure_item_group("Pricing Test Items")
		cls.item_code = "PRICING-MSRP-001"
		if not frappe.db.exists("Item", cls.item_code):
			item = frappe.new_doc("Item")
			item.item_code = cls.item_code
			item.item_name = "Pricing MSRP Test Item"
			item.item_group = "Pricing Test Items"
			item.stock_uom = "Nos"
			item.is_stock_item = 1
			item.is_sales_item = 1
			item.standard_rate = 500.0
			item.custom_msrp = 750.0
			item.insert(ignore_permissions=True)
		frappe.db.commit()

	def setUp(self):
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.db.rollback()

	def test_msrp_takes_priority(self):
		from zevar_core.api.pricing import get_item_price

		result = get_item_price(self.item_code)
		self.assertEqual(result["price_source"], "MSRP")
		self.assertEqual(flt(result["final_price"]), 750.0)

	def test_msrp_response_structure(self):
		from zevar_core.api.pricing import get_item_price

		result = get_item_price(self.item_code)
		self.assertIn("item_code", result)
		self.assertIn("item_name", result)
		self.assertIn("final_price", result)
		self.assertIn("price_source", result)
		self.assertEqual(result["item_code"], self.item_code)


@erpnext_required
class TestPricingEngineStandardRate(FrappeTestCase):
	"""Test Standard Rate fallback (lowest priority)."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		ensure_item_group("Pricing Test Items")
		cls.item_code = "PRICING-STD-001"
		if not frappe.db.exists("Item", cls.item_code):
			item = frappe.new_doc("Item")
			item.item_code = cls.item_code
			item.item_name = "Pricing Std Rate Test Item"
			item.item_group = "Pricing Test Items"
			item.stock_uom = "Nos"
			item.is_stock_item = 1
			item.is_sales_item = 1
			item.standard_rate = 300.0
			item.insert(ignore_permissions=True)
		frappe.db.commit()

	def setUp(self):
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.db.rollback()

	def test_standard_rate_fallback(self):
		from zevar_core.api.pricing import get_item_price

		result = get_item_price(self.item_code)
		self.assertEqual(result["price_source"], "Standard Rate")
		self.assertEqual(flt(result["final_price"]), 300.0)

	def test_zero_rate_when_no_pricing(self):
		from zevar_core.api.pricing import get_item_price

		item_code = "PRICING-ZERO-001"
		if not frappe.db.exists("Item", item_code):
			item = frappe.new_doc("Item")
			item.item_code = item_code
			item.item_name = "Pricing Zero Test Item"
			item.item_group = "Pricing Test Items"
			item.stock_uom = "Nos"
			item.is_stock_item = 1
			item.is_sales_item = 1
			item.standard_rate = 0
			item.insert(ignore_permissions=True)
			frappe.db.commit()

		result = get_item_price(item_code)
		self.assertEqual(flt(result["final_price"]), 0.0)


@erpnext_required
class TestPricingEngineCalculated(FrappeTestCase):
	"""Test Calculated price (gold + gemstone) when no MSRP exists."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value(
			"Global Defaults", "default_company"
		)
		frappe.db.commit()

	def setUp(self):
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.db.rollback()

	def test_gold_rate_returns_zero_for_missing_metal(self):
		from zevar_core.api.pricing import _get_gold_rate

		rate = _get_gold_rate("", "22Kt")
		self.assertEqual(rate, 0.0)

	def test_gold_rate_returns_zero_for_missing_purity(self):
		from zevar_core.api.pricing import _get_gold_rate

		rate = _get_gold_rate("Yellow Gold", "")
		self.assertEqual(rate, 0.0)

	def test_rose_gold_uses_yellow_gold_rate(self):
		from zevar_core.api.pricing import _get_gold_rate

		rate = _get_gold_rate("Rose Gold", "18Kt")
		yellow_rate = _get_gold_rate("Yellow Gold", "18Kt")
		self.assertEqual(rate, yellow_rate)

	def test_white_gold_uses_yellow_gold_rate(self):
		from zevar_core.api.pricing import _get_gold_rate

		rate = _get_gold_rate("White Gold", "14Kt")
		yellow_rate = _get_gold_rate("Yellow Gold", "14Kt")
		self.assertEqual(rate, yellow_rate)

	def test_calculated_price_with_no_metal_data(self):
		from zevar_core.api.pricing import get_item_price

		item_code = "PRICING-NOMETAL-001"
		if not frappe.db.exists("Item", item_code):
			item = frappe.new_doc("Item")
			item.item_code = item_code
			item.item_name = "Pricing No Metal Item"
			item.item_group = "All Item Groups"
			item.stock_uom = "Nos"
			item.is_stock_item = 1
			item.is_sales_item = 1
			item.standard_rate = 150.0
			item.insert(ignore_permissions=True)
			frappe.db.commit()

		result = get_item_price(item_code)
		self.assertEqual(result["price_source"], "Standard Rate")
		self.assertEqual(flt(result["final_price"]), 150.0)


@erpnext_required
class TestPricingEngineHelperFunctions(FrappeTestCase):
	"""Test pricing helper functions directly."""

	def setUp(self):
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.db.rollback()

	def test_build_price_response_structure(self):
		from zevar_core.api.pricing import _build_price_response

		class FakeItem:
			name = "TEST-001"
			item_name = "Test Item"
			custom_metal_type = "Yellow Gold"
			custom_purity = "18Kt"
			custom_gross_weight_g = 10.0
			custom_stone_weight_g = 1.0
			custom_net_weight_g = 9.0
			image = None

		result = _build_price_response(FakeItem(), 500.0, "MSRP")
		self.assertEqual(result["item_code"], "TEST-001")
		self.assertEqual(result["final_price"], 500.0)
		self.assertEqual(result["price_source"], "MSRP")
		self.assertEqual(result["metal"], "Yellow Gold")
		self.assertEqual(result["purity"], "18Kt")

	def test_calculate_gold_value_zero_without_data(self):
		from zevar_core.api.pricing import _calculate_gold_value

		class FakeItem:
			custom_net_weight_g = None
			custom_metal_type = None
			custom_purity = None

		result = _calculate_gold_value(FakeItem())
		self.assertEqual(result, 0.0)

	def test_calculate_gemstone_value_zero_without_data(self):
		from zevar_core.api.pricing import _calculate_gemstone_value

		class FakeItem:
			pass

		result = _calculate_gemstone_value(FakeItem())
		self.assertEqual(result, 0.0)
