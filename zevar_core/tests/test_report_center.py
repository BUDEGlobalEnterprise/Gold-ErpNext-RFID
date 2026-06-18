import unittest
import frappe
def create_test_user(email, roles):
	if not frappe.db.exists("User", email):
		user = frappe.new_doc("User")
		user.email = email
		user.first_name = email.split("@")[0]
		for role in roles:
			user.append("roles", {"role": role})
		user.insert(ignore_permissions=True)
	else:
		user = frappe.get_doc("User", email)
		user.set("roles", [])
		for role in roles:
			user.append("roles", {"role": role})
		user.save(ignore_permissions=True)
	return email

def set_user(user):
	frappe.set_user(user)

from zevar_core.api.report_center import (
	get_executive_overview,
	get_sales_monitor_data,
	get_profit_intelligence_data,
	get_workforce_data,
)


class TestReportCenterRBAC(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.users = {
			"System Manager": create_test_user("sys_manager@zevar.local", ["System Manager"]),
			"Accounts Manager": create_test_user("acc_manager@zevar.local", ["Accounts Manager"]),
			"Store Manager": create_test_user("store_manager@zevar.local", ["Store Manager"]),
			"Sales Manager": create_test_user("sales_manager@zevar.local", ["Sales Manager"]),
			"HR Manager": create_test_user("hr_manager@zevar.local", ["HR Manager"]),
			"Sales User": create_test_user("sales_user@zevar.local", ["Sales User"]),
		}

	@classmethod
	def tearDownClass(cls):
		frappe.set_user("Administrator")
		super().tearDownClass()

	def assert_access(self, fn, role, expected_allowed):
		user = self.users[role]
		set_user(user)
		if expected_allowed:
			try:
				fn()
			except frappe.PermissionError:
				self.fail(f"Role {role} should have access to {fn.__name__}")
			except Exception:
				# Other exceptions (like db errors or missing docs) are fine, 
				# we only care about PermissionError
				pass
		else:
			with self.assertRaises(frappe.PermissionError, msg=f"Role {role} should NOT have access to {fn.__name__}"):
				fn()

	def test_executive_overview_access(self):
		for role in self.users.keys():
			self.assert_access(get_executive_overview, role, True)

	def test_sales_monitor_access(self):
		for role in self.users.keys():
			self.assert_access(get_sales_monitor_data, role, True)

	def test_profit_intelligence_access(self):
		allowed = {"System Manager", "Accounts Manager"}
		for role in self.users.keys():
			self.assert_access(get_profit_intelligence_data, role, role in allowed)

	def test_workforce_data_access(self):
		allowed = {"System Manager", "Store Manager", "Sales Manager", "HR Manager"}
		for role in self.users.keys():
			self.assert_access(get_workforce_data, role, role in allowed)

