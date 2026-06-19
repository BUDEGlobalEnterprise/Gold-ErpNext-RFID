import frappe

def set_dummy_keys():
	# Square
	try:
		sq = frappe.get_doc("Square Settings")
		sq.sandbox_application_id = "sandbox-sq0idb-DUMMY_KEY_REPLACE_ME"
		sq.sandbox_access_token = "EAAA-DUMMY_TOKEN_REPLACE_ME"
		sq.save(ignore_permissions=True)
	except frappe.DoesNotExistError:
		# Maybe doesn't exist, create it if it's a single Doctype
		try:
			sq = frappe.new_doc("Square Settings")
			sq.sandbox_application_id = "sandbox-sq0idb-DUMMY_KEY_REPLACE_ME"
			sq.sandbox_access_token = "EAAA-DUMMY_TOKEN_REPLACE_ME"
			sq.insert(ignore_permissions=True)
		except Exception as e:
			print(f"Square error: {e}")
		
	# Stripe
	try:
		st = frappe.get_doc("Stripe Settings")
		st.publishable_key = "pk_test_DUMMY_KEY_REPLACE_ME"
		st.secret_key = "sk_test_DUMMY_KEY_REPLACE_ME"
		st.save(ignore_permissions=True)
	except frappe.DoesNotExistError:
		try:
			st = frappe.new_doc("Stripe Settings")
			st.publishable_key = "pk_test_DUMMY_KEY_REPLACE_ME"
			st.secret_key = "sk_test_DUMMY_KEY_REPLACE_ME"
			st.insert(ignore_permissions=True)
		except Exception as e:
			print(f"Stripe error: {e}")
		
	frappe.db.commit()
