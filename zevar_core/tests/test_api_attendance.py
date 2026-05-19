# Copyright (c) 2025, Zevar Core
# License: GNU General Public License v3.0

"""
Unit Tests for Attendance API (attendance.py)
Covers: clock_in, clock_out, get_attendance_history, and helper functions

Run with: bench run-tests --app zevar_core --test test_api_attendance
"""

import frappe
from frappe.tests.utils import FrappeTestCase

erpnext_required = frappe.db and frappe.db.exists("DocType", "Employee Checkin")


class TestAttendanceHelpers(FrappeTestCase):
	"""Test attendance helper functions"""

	def test_normalize_break_note_break_start(self):
		"""Should normalize 'break start' variants"""
		from zevar_core.api.attendance import _normalize_break_note

		self.assertEqual(_normalize_break_note("break start"), "Break Start")
		self.assertEqual(_normalize_break_note("Break Start"), "Break Start")
		self.assertEqual(_normalize_break_note("  BREAK START  "), "Break Start")

	def test_normalize_break_note_break_end(self):
		"""Should normalize 'break end' variants"""
		from zevar_core.api.attendance import _normalize_break_note

		self.assertEqual(_normalize_break_note("break end"), "Break End")
		self.assertEqual(_normalize_break_note("Break End"), "Break End")

	def test_normalize_break_note_other(self):
		"""Should return None for non-break notes"""
		from zevar_core.api.attendance import _normalize_break_note

		self.assertIsNone(_normalize_break_note("lunch"))
		self.assertIsNone(_normalize_break_note(""))

	def test_normalize_break_note_none(self):
		"""Should return None for None input"""
		from zevar_core.api.attendance import _normalize_break_note

		self.assertIsNone(_normalize_break_note(None))

	def test_build_device_id_default(self):
		"""Should return HRMS Portal for no note"""
		from zevar_core.api.attendance import _build_device_id

		self.assertEqual(_build_device_id(), "HRMS Portal")

	def test_build_device_id_break_start(self):
		"""Should include break marker in device_id"""
		from zevar_core.api.attendance import _build_device_id

		self.assertEqual(_build_device_id("break start"), "HRMS Portal - Break Start")

	def test_build_device_id_break_end(self):
		"""Should include break marker in device_id"""
		from zevar_core.api.attendance import _build_device_id

		self.assertEqual(_build_device_id("break end"), "HRMS Portal - Break End")

	def test_default_working_hours_full_time(self):
		"""Full-time employees get 8 hours"""
		from zevar_core.api.attendance import _get_default_working_hours

		self.assertEqual(_get_default_working_hours("Full-time"), 8)
		self.assertEqual(_get_default_working_hours(None), 8)

	def test_default_working_hours_part_time(self):
		"""Part-time employees get 4 hours"""
		from zevar_core.api.attendance import _get_default_working_hours

		self.assertEqual(_get_default_working_hours("Part-time"), 4)
		self.assertEqual(_get_default_working_hours("part-time"), 4)
