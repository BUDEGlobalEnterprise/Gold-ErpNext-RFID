import frappe

def execute():
    sessions = frappe.get_all("POS Opening Entry",
        filters={"docstatus": 1},
        fields=["name", "pos_profile", "status", "opening_cash", "posting_date"],
        order_by="creation desc",
        limit_page_length=20
    )
    print(f"=== POS Opening Entries ({len(sessions)}) ===")
    for s in sessions:
        print(f"  {s.name} | {s.pos_profile} | status={s.status} | cash={s.opening_cash} | {s.posting_date}")

    pos_sessions = frappe.get_all("POS Closing Entry",
        filters={"docstatus": 1},
        fields=["name", "pos_profile", "status"],
        order_by="creation desc",
        limit_page_length=5
    )
    print(f"\n=== POS Closing Entries ({len(pos_sessions)}) ===")
    for s in pos_sessions:
        print(f"  {s.name} | {s.pos_profile} | status={s.status}")

    # Check if there's a POS Session doctype
    if frappe.db.exists("DocType", "POS Session"):
        sessions2 = frappe.get_all("POS Session",
            filters={},
            fields=["name", "pos_profile", "status"],
            order_by="creation desc",
            limit_page_length=10
        )
        print(f"\n=== POS Sessions ({len(sessions2)}) ===")
        for s in sessions2:
            print(f"  {s.name} | {s.pos_profile} | {s.status}")
