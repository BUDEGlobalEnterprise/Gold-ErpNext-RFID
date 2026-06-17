import frappe

def create_pos_profile():
    """Create default POS Profile if none exists."""
    if frappe.db.exists("POS Profile", "Default POS"):
        print("POS Profile 'Default POS' already exists")
        return

    customer = frappe.db.get_value("Customer", {"customer_name": "Walk In Customer"}, "name")
    if not customer:
        customer = frappe.db.get_value("Customer", {}, "name")

    doc = frappe.new_doc("POS Profile")
    doc.name1 = "Default POS"  # naming_series might be used, but let's try
    doc.company = "Zevar Fine Jewelers"
    doc.warehouse = "Stores - ZFJ"
    doc.currency = "USD"
    doc.selling_price_list = "Standard Selling"
    doc.customer = customer
    doc.write_off_account = "Round Off - ZFJ"
    doc.write_off_cost_center = "Main - ZFJ"
    doc.expense_account = "Cost of Goods Sold - ZFJ"
    doc.cost_center = "Main - ZFJ"
    doc.allow_user_to_edit_rate = 0
    doc.allow_user_to_edit_discount = 1
    doc.allow_delete = 1
    doc.allow_return = 1

    doc.append("payments", {"mode_of_payment": "Cash", "default": 1})
    if frappe.db.exists("Mode of Payment", "Bank Draft"):
        doc.append("payments", {"mode_of_payment": "Bank Draft", "default": 0})

    doc.insert(ignore_permissions=True, set_name="Default POS")
    print(f"Created POS Profile: {doc.name}")
    frappe.db.commit()
