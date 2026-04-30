import frappe

def create_reports():
    if not frappe.db.exists("Report", "Financier Receivables Today"):
        doc = frappe.new_doc("Report")
        doc.report_name = "Financier Receivables Today"
        doc.ref_doctype = "GL Entry"
        doc.report_type = "Script Report"
        doc.is_standard = "Yes"
        doc.module = "Unified Retail Management System"
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        print("Created report: Financier Receivables Today")

def create_number_cards():
    cards = ["Synchrony", "AFF", "CIMA", "Progressive", "Snap"]
    for financier in cards:
        name = f"A/R — {financier} (Today)"
        if not frappe.db.exists("Number Card", name):
            doc = frappe.new_doc("Number Card")
            doc.name = name
            doc.label = name
            doc.document_type = "GL Entry"
            doc.function = "Sum"
            doc.aggregate_function_based_on = "debit"
            doc.filters_json = f'[("GL Entry", "account", "=", "Asset — A/R {financier} - ZJ", False), ("GL Entry", "posting_date", "=", "Today", False)]'
            doc.is_standard = 1
            doc.module = "Unified Retail Management System"
            doc.insert(ignore_permissions=True)
            print(f"Created number card: {name}")
    frappe.db.commit()

create_reports()
create_number_cards()
