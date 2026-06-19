import re

with open("/workspace/development/frappe-bench/apps/zevar_core/zevar_core/api/pos.py", "r") as f:
    content = f.read()

# 1. Update signature of create_pos_invoice
content = content.replace(
    "irs_8300_details: str | None = None,",
    "irs_8300_details: str | None = None,\n\tonline_checkout_gateway: str | None = None,"
)

# 2. Pass to _create_pos_invoice_internal
content = content.replace(
    "irs_8300_details,",
    "irs_8300_details,\n\t\t\tonline_checkout_gateway,"
)

# 3. Update signature of _create_pos_invoice_internal
content = content.replace(
    "irs_8300_details: str | None = None,\n) -> dict:",
    "irs_8300_details: str | None = None,\n\tonline_checkout_gateway: str | None = None,\n) -> dict:"
)

# 4. Bypass payments_list validation
content = content.replace(
    'if not payments_list:\n\t\tcheckout_bouncer(_("At least one payment mode is required."), "invoice_failed")',
    'if not payments_list and not online_checkout_gateway:\n\t\tcheckout_bouncer(_("At least one payment mode is required."), "invoice_failed")'
)

# 5. Add online checkout logic at the end
old_return = """		return {
			"success": True,
			"invoice_name": si.name,
			"status": si.status,
			"grand_total": si.grand_total,
			"outstanding_amount": si.outstanding_amount,
			"form_8300_triggered": form_8300_triggered,
			"message": f"Successfully created invoice {si.name}",
		}"""

new_return = """		checkout_url = None
		payment_request_name = None
		if online_checkout_gateway:
			try:
				from zevar_core.api.pos import initiate_online_checkout
				online_res = initiate_online_checkout("Sales Invoice", si.name, online_checkout_gateway)
				checkout_url = online_res.get("checkout_url")
				payment_request_name = online_res.get("payment_request_name")
			except Exception as e:
				frappe.log_error("Online Checkout Failed", frappe.get_traceback())
				frappe.throw(f"Failed to generate online checkout link: {e}")

		return {
			"success": True,
			"invoice_name": si.name,
			"status": si.status,
			"grand_total": si.grand_total,
			"outstanding_amount": si.outstanding_amount,
			"form_8300_triggered": form_8300_triggered,
			"checkout_url": checkout_url,
			"payment_request_name": payment_request_name,
			"message": f"Successfully created invoice {si.name}",
		}"""

content = content.replace(old_return, new_return)

with open("/workspace/development/frappe-bench/apps/zevar_core/zevar_core/api/pos.py", "w") as f:
    f.write(content)

