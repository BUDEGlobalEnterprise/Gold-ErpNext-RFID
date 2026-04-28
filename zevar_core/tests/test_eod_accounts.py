import frappe
from frappe.tests.utils import FrappeTestCase


class TestEODAccounts(FrappeTestCase):
	def test_financier_payment_modes_mapped_correctly(self):
		company = "Zevar Jewelers"
		financiers = {
			"Synchrony": "Asset — A/R Synchrony - ZJ",
			"AFF": "Asset — A/R AFF - ZJ",
			"CIMA": "Asset — A/R CIMA - ZJ",
			"Progressive": "Asset — A/R Progressive - ZJ",
			"Snap": "Asset — A/R Snap - ZJ",
		}

		seen_accounts = set()

		for mode, expected_account in financiers.items():
			# Mode of Payment should exist
			self.assertTrue(
				frappe.db.exists("Mode of Payment", mode), f"Mode of Payment '{mode}' does not exist"
			)

			doc = frappe.get_doc("Mode of Payment", mode)

			# Should be of type 'General'
			self.assertEqual(doc.type, "General", f"Mode of Payment '{mode}' should be type 'General'")

			# Find the account for the company
			company_account = None
			for acc in doc.accounts:
				if acc.company == company:
					company_account = acc.default_account
					break

			self.assertIsNotNone(
				company_account, f"No account mapping found for '{mode}' and company '{company}'"
			)
			self.assertEqual(company_account, expected_account, f"Mapping for '{mode}' is incorrect")

			# Ensure distinct GL accounts
			self.assertNotIn(
				company_account,
				seen_accounts,
				f"Account '{company_account}' is mapped to multiple financiers",
			)
			seen_accounts.add(company_account)

	def test_eod_accounts_created(self):
		expected_accounts = [
			"Income — Repair Services - ZJ",
			"Liability — Layaway Deposits Held - ZJ",
			"Asset — A/R Synchrony - ZJ",
			"Asset — A/R AFF - ZJ",
			"Asset — A/R CIMA - ZJ",
			"Asset — A/R Progressive - ZJ",
			"Asset — A/R Snap - ZJ",
			"Asset — Cash Drawer Float - ZJ",
		]

		for acc in expected_accounts:
			self.assertTrue(frappe.db.exists("Account", acc), f"Account '{acc}' was not created")
