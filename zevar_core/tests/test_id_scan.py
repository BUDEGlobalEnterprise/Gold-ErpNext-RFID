# Copyright (c) 2026, Zevar Core
# License: GNU General Public License v3.0

"""
Tests for the AAMVA PDF417 driver's license parser (Fix #5).

These tests exercise realistic scanner output rather than carefully-curated
payloads, so the parser stays robust to the messy inputs we'll see in the
field: stripped headers, escaped control characters, ALL-CAPS values,
mixed line endings, and the AAMVA 2000 legacy full-name format.
"""

import frappe
from frappe.tests.utils import FrappeTestCase


def _build_aamva_payload(version: str = "08", iin: str = "636014", elements=None) -> str:
	"""Construct a realistic AAMVA PDF417 payload string for tests.

	`elements` is an iterable of (3-letter code, value) tuples. We build
	the standard header + DL subfile body. Tests only need the body to be
	parseable, not byte-perfect, so we skip the binary subfile-index
	bytes that the real format prepends.
	"""
	elements = list(elements or [])
	body_lines = ["DL"] + [f"{code}{value}" for code, value in elements]
	body = "\n".join(body_lines)
	# Compliance indicator + record/segment separators + ANSI header.
	header = f"@\n\x1e\rANSI {iin}{version}00{len(elements):02d}DL"
	return header + "\n" + body


class TestParseDriversLicenseHappyPath(FrappeTestCase):
	"""A standard 2013 California driver's license should parse cleanly."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.payload = _build_aamva_payload(
			version="08",
			iin="636014",
			elements=[
				("DCS", "DOE"),
				("DAC", "JOHN"),
				("DAD", "QUINCY"),
				("DAG", "123 SPRINGFIELD AVE"),
				("DAI", "SAN FRANCISCO"),
				("DAJ", "CA"),
				("DAK", "94110"),
				("DCG", "USA"),
				("DAQ", "D1234567"),
				("DBB", "01151990"),  # MMDDYYYY → 1990-01-15
				("DBA", "01152030"),  # expiry
				("DBC", "1"),  # Male
			],
		)

	def test_parses_first_and_last_name(self):
		from zevar_core.api.id_scan import parse_drivers_license_payload

		result = parse_drivers_license_payload(self.payload)
		self.assertTrue(result["success"])
		self.assertEqual(result["first_name"], "John")
		self.assertEqual(result["last_name"], "Doe")
		self.assertEqual(result["middle_name"], "Quincy")
		self.assertEqual(result["full_name"], "John Quincy Doe")

	def test_parses_address_components(self):
		from zevar_core.api.id_scan import parse_drivers_license_payload

		result = parse_drivers_license_payload(self.payload)
		# Title-cased on output but state stays uppercase as a 2-letter code.
		self.assertEqual(result["address_line1"], "123 Springfield Ave")
		self.assertEqual(result["city"], "San Francisco")
		self.assertEqual(result["state"], "CA")
		self.assertEqual(result["postal_code"], "94110")
		self.assertEqual(result["country"], "USA")

	def test_parses_dates_to_iso(self):
		from zevar_core.api.id_scan import parse_drivers_license_payload

		result = parse_drivers_license_payload(self.payload)
		self.assertEqual(result["date_of_birth"], "1990-01-15")
		self.assertEqual(result["license_expiry"], "2030-01-15")

	def test_parses_sex_code(self):
		from zevar_core.api.id_scan import parse_drivers_license_payload

		result = parse_drivers_license_payload(self.payload)
		self.assertEqual(result["sex"], "Male")

	def test_parses_license_number(self):
		from zevar_core.api.id_scan import parse_drivers_license_payload

		result = parse_drivers_license_payload(self.payload)
		self.assertEqual(result["license_number"], "D1234567")

	def test_parses_aamva_version(self):
		from zevar_core.api.id_scan import parse_drivers_license_payload

		result = parse_drivers_license_payload(self.payload)
		self.assertEqual(result["aamva_version"], "08")
		self.assertEqual(result["issuer_iin"], "636014")


class TestParseDriversLicenseRobustness(FrappeTestCase):
	"""Real-world scanner output is messy. Make sure we tolerate that."""

	def test_handles_crlf_line_endings(self):
		from zevar_core.api.id_scan import parse_drivers_license_payload

		payload = _build_aamva_payload(elements=[("DCS", "SMITH"), ("DAC", "JANE")]).replace("\n", "\r\n")
		result = parse_drivers_license_payload(payload)
		self.assertTrue(result["success"])
		self.assertEqual(result["last_name"], "Smith")
		self.assertEqual(result["first_name"], "Jane")

	def test_handles_escaped_control_chars(self):
		"""Some scanners send "\\n" literal instead of an actual newline."""
		from zevar_core.api.id_scan import parse_drivers_license_payload

		payload = (
			_build_aamva_payload(elements=[("DCS", "SMITH"), ("DAC", "JANE")])
			.replace("\n", "\\n")
			.replace("\x1e", "\\u001e")
		)
		result = parse_drivers_license_payload(payload)
		self.assertTrue(result["success"])
		self.assertEqual(result["first_name"], "Jane")

	def test_handles_legacy_full_name_field_DAA(self):
		"""AAMVA 2000 cards used DAA with comma-separated full name."""
		from zevar_core.api.id_scan import parse_drivers_license_payload

		payload = _build_aamva_payload(
			version="00",
			elements=[("DAA", "DOE,JOHN,Q"), ("DAQ", "DL000001")],
		)
		result = parse_drivers_license_payload(payload)
		self.assertTrue(result["success"])
		self.assertEqual(result["last_name"], "Doe")
		self.assertEqual(result["first_name"], "John")
		self.assertEqual(result["middle_name"], "Q")

	def test_handles_missing_optional_fields(self):
		"""Cards from minors / new licenses may omit the address."""
		from zevar_core.api.id_scan import parse_drivers_license_payload

		payload = _build_aamva_payload(
			elements=[
				("DCS", "ROE"),
				("DAC", "RICHARD"),
				("DBB", "07041988"),
			]
		)
		result = parse_drivers_license_payload(payload)
		self.assertTrue(result["success"])
		self.assertEqual(result["last_name"], "Roe")
		self.assertNotIn("address_line1", result)
		self.assertNotIn("city", result)
		self.assertEqual(result["date_of_birth"], "1988-07-04")

	def test_handles_yyyymmdd_canadian_format(self):
		"""Canadian licenses encode dates as YYYYMMDD."""
		from zevar_core.api.id_scan import parse_drivers_license_payload

		payload = _build_aamva_payload(
			elements=[
				("DCS", "TREMBLAY"),
				("DAC", "MARIE"),
				("DBB", "19850315"),
				("DCG", "CAN"),
			]
		)
		result = parse_drivers_license_payload(payload)
		self.assertTrue(result["success"])
		self.assertEqual(result["date_of_birth"], "1985-03-15")
		self.assertEqual(result["country"], "CAN")

	def test_drops_garbage_dates_silently(self):
		"""A scanner that emits 00000000 for DBB shouldn't bubble garbage up."""
		from zevar_core.api.id_scan import parse_drivers_license_payload

		payload = _build_aamva_payload(elements=[("DCS", "DOE"), ("DAC", "JOHN"), ("DBB", "00000000")])
		result = parse_drivers_license_payload(payload)
		self.assertTrue(result["success"])
		self.assertNotIn("date_of_birth", result)


class TestParseDriversLicenseFailures(FrappeTestCase):
	"""Negative cases — make sure we fail clearly rather than silently."""

	def test_empty_string_returns_unsuccessful(self):
		from zevar_core.api.id_scan import parse_drivers_license_payload

		result = parse_drivers_license_payload("")
		self.assertFalse(result["success"])
		self.assertIn("error", result)

	def test_random_text_returns_unsuccessful(self):
		from zevar_core.api.id_scan import parse_drivers_license_payload

		result = parse_drivers_license_payload("not a real barcode")
		self.assertFalse(result["success"])

	def test_aamva_header_without_name_fails(self):
		from zevar_core.api.id_scan import parse_drivers_license_payload

		# Has the magic header but no name fields.
		payload = "@\n\x1e\rANSI 6360140800\nDL\nDAQABC\n"
		result = parse_drivers_license_payload(payload)
		self.assertFalse(result["success"])
		self.assertIn("name", result["error"].lower())

	def test_endpoint_throws_on_empty_input(self):
		from zevar_core.api.id_scan import parse_drivers_license

		with self.assertRaises(frappe.exceptions.ValidationError):
			parse_drivers_license(barcode="")

	def test_endpoint_throws_on_oversized_input(self):
		from zevar_core.api.id_scan import parse_drivers_license

		with self.assertRaises(frappe.exceptions.ValidationError):
			parse_drivers_license(barcode="x" * 10000)

	def test_endpoint_throws_on_unparseable_input(self):
		from zevar_core.api.id_scan import parse_drivers_license

		with self.assertRaises(frappe.exceptions.ValidationError):
			parse_drivers_license(barcode="completely random text")

	def test_endpoint_returns_parsed_fields_on_success(self):
		from zevar_core.api.id_scan import parse_drivers_license

		payload = _build_aamva_payload(
			elements=[
				("DCS", "DOE"),
				("DAC", "JANE"),
				("DBB", "06151985"),
			]
		)
		result = parse_drivers_license(barcode=payload)
		self.assertTrue(result["success"])
		self.assertEqual(result["first_name"], "Jane")
		self.assertEqual(result["last_name"], "Doe")
		self.assertEqual(result["date_of_birth"], "1985-06-15")
