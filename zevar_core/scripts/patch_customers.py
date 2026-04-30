import frappe
import csv
from datetime import datetime

def run():
    csv_file = "/workspace/development/Zevar_URMS/customer.csv"
    updated = 0
    vip_assigned = 0

    with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        for row in reader:
            first = next((v for k, v in row.items() if k and k.startswith("FIRST")), "").strip()
            last = next((v for k, v in row.items() if k and k.startswith("LAST")), "").strip()
            customer_name = f"{first} {last}".strip()

            if not customer_name:
                continue

            dateadd = next((v for k, v in row.items() if k and k.startswith("DATEADD")), "").strip()
            spend = next((v for k, v in row.items() if k and k.startswith("SPEND")), "0").strip()

            if not spend: spend = 0
            try:
                spend_val = float(spend)
            except ValueError:
                spend_val = 0

            creation_str = None
            if dateadd:
                try:
                    dt = datetime.strptime(dateadd, "%d/%m/%Y")
                    creation_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    try:
                        dt = datetime.strptime(dateadd, "%m/%d/%Y")
                        creation_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                    except Exception:
                        pass

            cust = frappe.db.get_value("Customer", {"customer_name": customer_name}, "name")
            if cust:
                updates = {}
                if creation_str:
                    updates["creation"] = creation_str
                # Assign VIP if spend is > 1000
                if spend_val > 1000:
                    updates["customer_group"] = "VIP"
                    vip_assigned += 1

                if updates:
                    set_clause = ", ".join(f"`{k}`=%s" for k in updates.keys())
                    values = list(updates.values()) + [cust]
                    frappe.db.sql(f"UPDATE `tabCustomer` SET {set_clause} WHERE name=%s", values)
                    updated += 1

    frappe.db.commit()
    print(f"Updated {updated} customers. Assigned VIP to {vip_assigned} customers.")
