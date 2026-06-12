# Copyright (c) 2025, Zevar Core
# License: GNU General Public License v3.0

"""
Unit Tests for Tasks API (tasks.py)
Covers: get_employee_tasks, get_task_stats, and related endpoints

Run with: bench run-tests --app zevar_core --test test_api_tasks
"""

import unittest

import frappe
from frappe.tests.utils import FrappeTestCase


class TestGetEmployeeTasks(FrappeTestCase):
	"""Test get_employee_tasks endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_tasks_returns_dict(self):
		"""Should return tasks dict (or gameplan_installed=False)"""
		from zevar_core.api.tasks import get_employee_tasks

		result = get_employee_tasks()
		self.assertIsInstance(result, dict)
		self.assertIn("tasks", result)

	def test_get_tasks_respects_limit(self):
		"""Should respect limit parameter"""
		from zevar_core.api.tasks import get_employee_tasks

		result = get_employee_tasks(limit=5)
		if result.get("gameplan_installed"):
			self.assertLessEqual(len(result["tasks"]), 5)

	def test_get_tasks_with_status_filter(self):
		"""Should filter by status"""
		from zevar_core.api.tasks import get_employee_tasks

		result = get_employee_tasks(status="Done")
		if result.get("gameplan_installed"):
			for task in result["tasks"]:
				self.assertEqual(task["status"], "Done")


class TestGetTaskStats(FrappeTestCase):
	"""Test get_task_stats endpoint"""

	def setUp(self):
		frappe.set_user("Administrator")

	def test_get_stats_returns_dict(self):
		"""Should return stats dict"""
		from zevar_core.api.tasks import get_task_stats

		result = get_task_stats()
		self.assertIsInstance(result, dict)
