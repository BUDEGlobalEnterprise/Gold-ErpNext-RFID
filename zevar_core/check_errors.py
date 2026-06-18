import frappe

def execute():
    errors = frappe.db.sql("""
        SELECT name, creation, method, error
        FROM `tabError Log`
        WHERE creation > '2026-06-18'
        AND method LIKE '%pos%' OR method LIKE '%POS%' OR method LIKE '%create_pos%'
        ORDER BY creation DESC
        LIMIT 5
    """, as_dict=True)
    
    print(f"=== Recent POS Error Logs ({len(errors)}) ===")
    for e in errors:
        print(f"\n--- {e.name} ({e.creation}) ---")
        print(f"Method: {e.method}")
        print(f"Error: {e.error[:2000]}")
