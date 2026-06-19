import frappe

def create_square_doctype():
    if not frappe.db.exists("DocType", "Square Settings"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "Square Settings",
            "module": "Unified Retail Management System",
            "custom": 0,
            "issingle": 0,
            "istable": 0,
            "fields": [
                {"fieldname": "gateway_name", "fieldtype": "Data", "label": "Gateway Name", "reqd": 1, "unique": 1},
                {"fieldname": "application_id", "fieldtype": "Data", "label": "Application ID", "reqd": 1},
                {"fieldname": "access_token", "fieldtype": "Password", "label": "Access Token", "reqd": 1},
                {"fieldname": "location_id", "fieldtype": "Data", "label": "Location ID", "reqd": 1},
                {"fieldname": "environment", "fieldtype": "Select", "label": "Environment", "options": "Sandbox\nProduction", "default": "Sandbox"},
            ],
            "permissions": [
                {
                    "role": "System Manager",
                    "read": 1, "write": 1, "create": 1, "delete": 1
                }
            ]
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        print("Square Settings DocType created successfully")
    else:
        print("Square Settings DocType already exists")

create_square_doctype()
