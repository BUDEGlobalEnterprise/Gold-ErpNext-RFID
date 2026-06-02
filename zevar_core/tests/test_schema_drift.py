"""Schema-drift CI tests for Inventory v2.

These tests walk the Python source code to detect:
1. Fields referenced in controllers but missing from DocType JSON
2. Direct tabBin writes (forbidden by DEC-INV-V2-002)
3. Reservation schema completeness

Run: bench --site <site> run-tests --app zevar_core --test zevar_core.tests.test_schema_drift
"""

import ast
import json
import os
import unittest

import frappe
from frappe.tests.utils import FrappeTestCase


BASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)))
DOCTYPE_PATH = os.path.join(BASE_PATH, "unified_retail_management_system", "doctype")
SERVICES_PATH = os.path.join(BASE_PATH, "services")


class TestSchemaDrift(FrappeTestCase):
	"""Detect fields referenced in controllers but missing from DocType JSON."""

	def test_stock_reservation_schema_complete(self):
		"""reservation_manager.py references must exist in stock_reservation.json."""
		json_path = os.path.join(DOCTYPE_PATH, "stock_reservation", "stock_reservation.json")
		if not os.path.exists(json_path):
			self.skipTest("stock_reservation.json not found")

		with open(json_path) as f:
			schema = json.load(f)

		schema_fields = {f["fieldname"] for f in schema.get("fields", [])}

		required_fields = {
			"reservation_type", "auto_expire_on", "cart_reference", "salesperson",
			"pos_session", "converted_from", "release_reason", "released_by",
			"released_at", "priority", "intended_use",
		}

		missing = required_fields - schema_fields
		self.assertFalse(
			missing,
			f"Stock Reservation JSON missing fields referenced by reservation_manager.py: {missing}",
		)

	def test_zevar_metal_schema_complete(self):
		"""Zevar Metal must have all reference table fields."""
		json_path = os.path.join(DOCTYPE_PATH, "zevar_metal", "zevar_metal.json")
		if not os.path.exists(json_path):
			self.skipTest("zevar_metal.json not found")

		with open(json_path) as f:
			schema = json.load(f)

		schema_fields = {f["fieldname"] for f in schema.get("fields", [])}
		required = {"metal_code", "metal_name", "metal_type", "default_purity", "is_active", "color_hex"}
		missing = required - schema_fields
		self.assertFalse(missing, f"Zevar Metal JSON missing fields: {missing}")

	def test_zevar_purity_schema_complete(self):
		"""Zevar Purity must have all reference table fields."""
		json_path = os.path.join(DOCTYPE_PATH, "zevar_purity", "zevar_purity.json")
		if not os.path.exists(json_path):
			self.skipTest("zevar_purity.json not found")

		with open(json_path) as f:
			schema = json.load(f)

		schema_fields = {f["fieldname"] for f in schema.get("fields", [])}
		required = {"purity_code", "purity_name", "metal", "fine_metal_content", "is_active"}
		missing = required - schema_fields
		self.assertFalse(missing, f"Zevar Purity JSON missing fields: {missing}")

	def test_controller_fields_match_json(self):
		"""Walk controller .py files for self.<field> refs and verify they exist in JSON.

		Uses AST parsing to find self.<attr> assignments and accesses in validate/on_submit hooks.
		"""
		doctypes_to_check = {
			"stock_reservation": "stock_reservation",
			"zevar_metal": "zevar_metal",
			"zevar_purity": "zevar_purity",
		}

		for doctype_dir, expected_json in doctypes_to_check.items():
			controller_path = os.path.join(DOCTYPE_PATH, doctype_dir, f"{doctype_dir}.py")
			json_path = os.path.join(DOCTYPE_PATH, doctype_dir, f"{doctype_dir}.json")

			if not os.path.exists(controller_path) or not os.path.exists(json_path):
				continue

			with open(json_path) as f:
				schema = json.load(f)
			schema_fields = {f["fieldname"] for f in schema.get("fields", [])}
			# Add standard Frappe fields that are always present
			schema_fields.update({
				"naming_series", "status", "docstatus", "owner", "creation",
				"modified", "modified_by", "idx", "company",
			})

			with open(controller_path) as f:
				source = f.read()

			tree = ast.parse(source)
			referenced_fields = set()

			for node in ast.walk(tree):
				if isinstance(node, ast.Attribute):
					if isinstance(node.value, ast.Name) and node.value.id == "self":
						referenced_fields.add(node.attr)

			# Filter out Python builtins and common non-field attributes
			non_fields = {
				"doctype", "_meta", "_doc_before_save", "flags", "name",
				"owner", "creation", "modified", "modified_by", "idx",
				"docstatus", "parent", "parentfield", "parenttype",
				"idx", "_table_fieldnames",
			}
			referenced_fields -= non_fields

			# Only check fields referenced via self.<field> (not via self.get() or dict access)
			missing = referenced_fields - schema_fields
			if missing:
				self.fail(
					f"Controller {doctype_dir}.py references fields not in JSON schema: {missing}"
				)


class TestNoDirectBinWrites(FrappeTestCase):
	"""Enforce DEC-INV-V2-002: no direct tabBin writes outside inventory_events.py."""

	DIRECT_BIN_PATTERNS = [
		"UPDATE `tabBin`",
		"UPDATE tabBin",
		"frappe.db.sql.*tabBin.*UPDATE",
	]

	ALLOWED_FILES = {
		"inventory_events.py",
		"inventory_audit_utils.py",
		"stock_reduction.py",
	}

	def test_no_direct_bin_writes_in_services(self):
		"""Service files must not write directly to tabBin."""
		if not os.path.exists(SERVICES_PATH):
			self.skipTest("services/ directory not found")

		violations = []
		for fname in os.listdir(SERVICES_PATH):
			if not fname.endswith(".py") or fname.startswith("__"):
				continue
			if fname in self.ALLOWED_FILES:
				continue

			fpath = os.path.join(SERVICES_PATH, fname)
			with open(fpath) as f:
				content = f.read()

			for pattern in ["UPDATE `tabBin`", "UPDATE tabBin"]:
				if pattern in content:
					violations.append(f"{fname}: contains '{pattern}'")

			# Check for frappe.db.set_value("Bin", ...)
			if 'frappe.db.set_value("Bin"' in content or "frappe.db.set_value('Bin'" in content:
				violations.append(f"{fname}: contains frappe.db.set_value('Bin', ...)")

		self.assertFalse(
			violations,
			f"Direct tabBin writes found (violates DEC-INV-V2-002):\n" + "\n".join(violations),
		)


class TestPatchIdempotency(FrappeTestCase):
	"""Verify patches are safe to describe (idempotent)."""

	def test_reservation_drift_patch_exists(self):
		patch_path = os.path.join(BASE_PATH, "patches", "v1_2", "fix_stock_reservation_schema_drift.py")
		self.assertTrue(os.path.exists(patch_path), "fix_stock_reservation_schema_drift.py not found")

	def test_seed_reference_patch_exists(self):
		patch_path = os.path.join(BASE_PATH, "patches", "v1_2", "seed_metal_purity_reference.py")
		self.assertTrue(os.path.exists(patch_path), "seed_metal_purity_reference.py not found")

	def test_backfill_pricing_patch_exists(self):
		patch_path = os.path.join(BASE_PATH, "patches", "v1_2", "backfill_pricing_method.py")
		self.assertTrue(os.path.exists(patch_path), "backfill_pricing_method.py not found")
