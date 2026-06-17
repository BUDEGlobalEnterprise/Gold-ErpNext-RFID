import frappe
import unittest

def run_tests():
	from zevar_core.tests.test_pos_apis import TestPOSProfileAPI, TestPOSSessionAPI
	print("Running TestPOSProfileAPI...")
	suite1 = unittest.TestLoader().loadTestsFromTestCase(TestPOSProfileAPI)
	runner1 = unittest.TextTestRunner(verbosity=2)
	runner1.run(suite1)

	print("\nRunning TestPOSSessionAPI...")
	suite2 = unittest.TestLoader().loadTestsFromTestCase(TestPOSSessionAPI)
	runner2 = unittest.TextTestRunner(verbosity=2)
	runner2.run(suite2)
