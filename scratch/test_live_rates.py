import frappe
import zevar_core.api.pricing

frappe.init(site='zevar.localhost')
frappe.connect()

user = 'mathias@abc.com'
frappe.set_user(user)
print(f"Testing as user: {user}")

try:
    rates = zevar_core.api.pricing.get_live_metal_rates()
    print("Rates fetched successfully:")
    print(rates)
except Exception as e:
    print(f"Error: {e}")
