import re

with open("/workspace/development/frappe-bench/apps/zevar_core/zevar_core/api/pos.py", "r") as f:
    content = f.read()

mock_endpoint = """
@frappe.whitelist(methods=["POST"])
def simulate_payment_success(payment_request_name: str):
	\"\"\"
	DEV ONLY: Simulates a webhook from Stripe/Square by marking a Payment Request as Paid.
	This will trigger the on_payment_request_update hook and send the socket event.
	\"\"\"
	frappe.only_for(["System Manager", "Administrator"])
	
	try:
		pr = frappe.get_doc("Payment Request", payment_request_name)
		if pr.status != "Paid":
			# Simulate what the gateway's webhook does
			frappe.db.set_value("Payment Request", pr.name, "status", "Paid")
			
			# We must also create a dummy Payment Entry to satisfy accounting
			pe = frappe.new_doc("Payment Entry")
			pe.payment_type = "Receive"
			pe.party_type = "Customer"
			pe.party = pr.reference_name # Need to get customer from the Sales Invoice
			
			invoice = frappe.get_doc("Sales Invoice", pr.reference_name)
			pe.party = invoice.customer
			pe.paid_amount = pr.grand_total
			pe.received_amount = pr.grand_total
			pe.mode_of_payment = "Wire Transfer" # Mock
			
			pe.append("references", {
				"reference_doctype": "Sales Invoice",
				"reference_name": invoice.name,
				"allocated_amount": pr.grand_total
			})
			pe.insert(ignore_permissions=True)
			pe.submit()
			
			# Manually trigger the hook since we used db.set_value
			from zevar_core.api.pos import on_payment_request_update
			pr.status = "Paid"
			on_payment_request_update(pr, "on_update")
			
		return {"success": True, "message": "Payment simulated successfully"}
	except Exception as e:
		frappe.log_error("Simulated Payment Failed", frappe.get_traceback())
		frappe.throw(f"Failed to simulate payment: {str(e)}")
"""

if "def simulate_payment_success" not in content:
    content += "\n" + mock_endpoint

with open("/workspace/development/frappe-bench/apps/zevar_core/zevar_core/api/pos.py", "w") as f:
    f.write(content)
