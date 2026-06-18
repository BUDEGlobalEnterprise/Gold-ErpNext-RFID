import frappe

def execute():
    # Check all POS profiles - maybe the DB query was limited
    all_profiles = frappe.db.sql("""
        SELECT name, warehouse, company
        FROM `tabPOS Profile`
        ORDER BY name
    """, as_dict=True)
    print(f"=== All POS Profiles ({len(all_profiles)}) ===")
    for p in all_profiles:
        print(f"  {p.name} | {p.warehouse} | {p.company}")

    # Check for test-related ones
    test_profiles = [p for p in all_profiles if "test" in (p.name or "").lower()]
    if test_profiles:
        print(f"\n=== Test Profiles ({len(test_profiles)}) ===")
        for p in test_profiles:
            print(f"  {p.name}")
    else:
        print("\nNo test profiles found.")
