import frappe

def execute():
    company = "Zevar Fine Jewelers"
    write_off_account = "Write Off - ZFJ"
    cost_center = "Zevar Fine Jewelers - ZFJ"
    float_account = "Cash - ZFJ"

    stores = [
        ("Brooklyn Store POS", "Brooklyn Store - ZFJ"),
        ("SoHo Store POS", "SoHo Store - ZFJ"),
        ("Midtown Store POS", "Midtown Store - ZFJ"),
        ("Queens Store POS", "Queens Store - ZFJ"),
        ("Manhattan Store POS", "Manhattan Store - ZFJ"),
    ]

    for profile_name, warehouse in stores:
        if frappe.db.exists("POS Profile", profile_name):
            print(f"SKIP: {profile_name} already exists")
            continue

        doc = frappe.new_doc("POS Profile")
        doc.name = profile_name
        doc.company = company
        doc.warehouse = warehouse
        doc.currency = "USD"
        doc.write_off_account = write_off_account
        doc.write_off_cost_center = cost_center
        doc.write_off_limit = 0
        doc.update_stock = 1
        doc.custom_fixed_opening_float = 0
        doc.custom_enforce_fixed_float = 0
        doc.custom_float_gl_account = float_account
        doc.custom_variance_alert_threshold = 5.00

        doc.append("payments", {"mode_of_payment": "Cash", "default": 1})

        doc.insert(ignore_permissions=True)
        print(f"CREATED: {profile_name} -> {warehouse}")

    frappe.db.commit()
    print("Done!")
