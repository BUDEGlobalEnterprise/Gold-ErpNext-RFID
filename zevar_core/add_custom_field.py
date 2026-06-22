import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def execute():
    create_custom_field("User", dict(
        fieldname="pos_manager_pin_hash",
        label="POS Manager PIN Hash",
        fieldtype="Data",
        hidden=1,
        read_only=1,
        insert_after="first_name"
    ))
    frappe.db.commit()
    print("Added custom field pos_manager_pin_hash to User")
