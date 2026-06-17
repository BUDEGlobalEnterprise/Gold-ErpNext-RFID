import frappe

def run():
    if frappe.db.exists("POS Profile", "Default POS"):
        print("Already exists")
        return
    customer = frappe.db.get_value("Customer", {}, "name")
    doc = frappe.new_doc("POS Profile")
    doc.company = "Zevar Fine Jewelers"
    doc.warehouse = "Stores - ZFJ"
    doc.currency = "USD"
    doc.selling_price_list = "Standard Selling"
    doc.customer = customer
    doc.write_off_account = "Round Off - ZFJ"
    doc.write_off_cost_center = "Main - ZFJ"
    doc.expense_account = "Cost of Goods Sold - ZFJ"
    doc.cost_center = "Main - ZFJ"
    doc.allow_user_to_edit_discount = 1
    doc.allow_delete = 1
    doc.allow_return = 1
    doc.append("payments", {"mode_of_payment": "Cash", "default": 1})
    doc.append("payments", {"mode_of_payment": "Bank Draft", "default": 0})
    doc.insert(ignore_permissions=True, set_name="Default POS")
    frappe.db.commit()
    print(f"Created: {doc.name}")
