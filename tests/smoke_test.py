#!/usr/bin/env python3
"""
Zevar POS Go-Live Smoke Test
Run this from the frappe-bench directory to verify all critical systems.
"""

import sys, os, json, requests

BENCH_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
BASE_URL = "http://localhost:8001"
SITE = "zevar.localhost"
ADMIN_USER = "Administrator"
ADMIN_PASS = "admin"

session = requests.Session()
failures = []

def log_pass(msg):
    print(f"  ✅ {msg}")

def log_fail(msg):
    print(f"  ❌ {msg}")
    failures.append(msg)

def log_info(msg):
    print(f"  ℹ️  {msg}")

def test_backend_api_health():
    print("\n🔧 BACKEND API HEALTH CHECKS")
    print("=" * 50)

    # 1. Login
    r = session.post(f"{BASE_URL}/api/method/login", json={"usr": ADMIN_USER, "pwd": ADMIN_PASS})
    if r.status_code == 200 and r.json().get("message") == "Logged In":
        log_pass("Frappe login API responds")
    else:
        log_fail(f"Frappe login failed: {r.status_code} {r.text[:200]}")
        return False

    # 2. Tax API
    r = session.get(f"{BASE_URL}/api/method/zevar_core.api.pos.get_pos_settings")
    if r.status_code == 200:
        data = r.json().get("message", {})
        tax_rate = data.get("tax_rate", 0)
        if tax_rate > 0:
            log_pass(f"Tax API returns rate: {tax_rate}%")
        else:
            log_fail(f"Tax API returns 0%: {data}")
    else:
        log_fail(f"Tax API error: {r.status_code}")

    # 3. POS items API
    r = session.get(f"{BASE_URL}/api/method/zevar_core.api.catalog.get_pos_items", params={"page_length": 1})
    if r.status_code == 200:
        items = r.json().get("message", [])
        log_pass(f"POS items API responds ({len(items)} items)")
    else:
        log_fail(f"POS items API error: {r.status_code}")

    # 4. Customer search API
    r = session.get(f"{BASE_URL}/api/method/frappe.client.get_list", params={
        "doctype": "Customer",
        "fields": '["name"]',
        "limit": 1
    })
    if r.status_code == 200:
        log_pass("Customer search API responds")
    else:
        log_fail(f"Customer search API error: {r.status_code}")

    # 5. Quick create customer API
    test_name = f"SmokeTest-{os.urandom(4).hex()}"
    r = session.post(f"{BASE_URL}/api/method/zevar_core.api.customer.quick_create_customer", json={
        "customer_name": test_name,
        "customer_type": "Individual",
        "mobile_no": "555-555-9999"
    })
    if r.status_code == 200:
        data = r.json().get("message", {})
        if data.get("success"):
            log_pass(f"Customer creation API works ({test_name})")
            # Cleanup
            try:
                session.post(f"{BASE_URL}/api/method/frappe.client.delete", json={
                    "doctype": "Customer",
                    "name": test_name
                })
            except:
                pass
        else:
            log_fail(f"Customer creation returned failure: {data}")
    else:
        log_fail(f"Customer creation API error: {r.status_code} {r.text[:200]}")

    # 6. Print format exists
    r = session.get(f"{BASE_URL}/api/method/frappe.client.get_list", params={
        "doctype": "Print Format",
        "filters": '[["name","=","pos_receipt"]]',
        "fields": '["name","doc_type","html"]'
    })
    if r.status_code == 200:
        formats = r.json().get("message", [])
        if formats:
            pf = formats[0]
            html = pf.get("html", "")
            if html and len(html) > 100:
                log_pass(f"Print Format 'pos_receipt' registered ({len(html)} bytes)")
            else:
                log_fail("Print Format 'pos_receipt' exists but HTML is empty")
        else:
            log_fail("Print Format 'pos_receipt' not found in database")
    else:
        log_fail(f"Print format API error: {r.status_code}")

    # 7. Receipt preview renders
    r = session.get(f"{BASE_URL}/printview", params={
        "doctype": "Sales Invoice",
        "name": "ACC-SINV-2026-00001",
        "format": "pos_receipt"
    })
    if r.status_code == 200:
        if "Store Name" in r.text or "Zevar Jewelers" in r.text or "Receipt #" in r.text:
            log_pass("Receipt preview renders successfully")
        elif "Server Error" in r.text:
            log_fail("Receipt preview returns Server Error")
        else:
            log_info(f"Receipt preview returned 200 but content unclear")
    elif r.status_code == 417:
        log_fail("Receipt preview error 417 — Jinja template has undefined variables")
    else:
        log_fail(f"Receipt preview error: {r.status_code}")

    # 8. Calculate invoice totals
    r = session.post(f"{BASE_URL}/api/method/zevar_core.api.pos.calculate_invoice_totals", json={
        "items": json.dumps([{"item_code": "TEST", "qty": 1, "rate": 1000}]),
        "warehouse": "Stores - ZJ"
    })
    if r.status_code == 200:
        data = r.json().get("message", {})
        tax = data.get("tax", 0)
        grand = data.get("grand_total", 0)
        if tax > 0:
            log_pass(f"Invoice totals API: tax=${tax:.2f}, grand=${grand:.2f}")
        else:
            log_fail(f"Invoice totals API returned zero tax: {data}")
    else:
        log_fail(f"Invoice totals API error: {r.status_code}")

    # 9. Store locations exist
    r = session.get(f"{BASE_URL}/api/method/frappe.client.get_list", params={
        "doctype": "Store Location",
        "fields": '["name","county_tax_rate","default_warehouse"]',
        "limit": 5
    })
    if r.status_code == 200:
        stores = r.json().get("message", [])
        active = [s for s in stores if s.get("default_warehouse")]
        if active:
            log_pass(f"Store locations configured ({len(active)} active)")
        else:
            log_fail("No active store locations with warehouse")
    else:
        log_fail(f"Store location API error: {r.status_code}")

    # 10. Payment modes configured
    r = session.get(f"{BASE_URL}/api/method/zevar_core.api.pos.get_pos_settings")
    if r.status_code == 200:
        modes = r.json().get("message", {}).get("payment_modes", [])
        if "Cash" in modes:
            log_pass(f"Payment modes configured ({len(modes)} modes)")
        else:
            log_fail("Cash payment mode missing")
    else:
        log_fail(f"Payment modes API error: {r.status_code}")

    return True


def test_frontend_build():
    print("\n🎨 FRONTEND BUILD CHECKS")
    print("=" * 50)

    pos_path = os.path.join(BENCH_DIR, "apps", "zevar_core", "frontend", "zevar_ui")

    # 1. Check cart.js tax fix
    cart_js = os.path.join(pos_path, "src", "stores", "cart.js")
    if os.path.exists(cart_js):
        with open(cart_js) as f:
            content = f.read()
        if "zevar_core.api.pos.get_pos_settings" in content:
            log_pass("cart.js has correct tax API path")
        elif "zevar_core.api.get_pos_settings" in content:
            log_fail("cart.js STILL has wrong tax API path!")
        else:
            log_info("cart.js tax API path not found (check manually)")
    else:
        log_fail("cart.js not found")

    # 2. Check data-testid selectors exist
    selector_files = [
        os.path.join(pos_path, "src", "components", "ItemCard.vue"),
        os.path.join(pos_path, "src", "components", "CartSidebar.vue"),
        os.path.join(pos_path, "src", "components", "CheckoutModal.vue"),
        os.path.join(pos_path, "src", "components", "CustomerSelector.vue"),
    ]
    total_selectors = 0
    for fpath in selector_files:
        if os.path.exists(fpath):
            with open(fpath) as f:
                count = f.read().count('data-testid="')
                total_selectors += count
    if total_selectors >= 10:
        log_pass(f"E2E selectors present ({total_selectors} data-testid attrs)")
    else:
        log_fail(f"Only {total_selectors} E2E selectors found (need 10+)")

    # 3. Check receipt print format JSON exists
    pf_json = os.path.join(
        BENCH_DIR, "apps", "zevar_core", "zevar_core",
        "unified_retail_management_system", "print_format",
        "pos_receipt", "pos_receipt.json"
    )
    if os.path.exists(pf_json):
        log_pass("pos_receipt.json print format registration exists")
    else:
        log_fail("pos_receipt.json missing")

    # 4. Check Cypress config exists
    cypress_config = os.path.join(
        BENCH_DIR, "apps", "zevar_core", "tests", "cypress", "cypress.config.js"
    )
    if os.path.exists(cypress_config):
        log_pass("Cypress E2E config exists")
    else:
        log_fail("Cypress E2E config missing")

    return True


def test_database_consistency():
    print("\n🗄️  DATABASE CONSISTENCY CHECKS")
    print("=" * 50)

    # These need Frappe context
    try:
        sys.path.insert(0, os.path.join(BENCH_DIR, "apps", "frappe"))
        import frappe
        frappe.init(site=SITE, sites_path=os.path.join(BENCH_DIR, "sites"))
        frappe.connect()

        # 1. Verify tax rate in DB
        stores = frappe.get_all("Store Location", fields=["name", "county_tax_rate", "default_warehouse"], filters={"is_active": 1}, limit=1)
        if stores:
            rate = stores[0].get("county_tax_rate", 0)
            wh = stores[0].get("default_warehouse", "None")
            if rate > 0:
                log_pass(f"DB: Active store '{stores[0].name}' has tax_rate={rate}%, warehouse={wh}")
            else:
                log_fail(f"DB: Active store has zero tax rate")
        else:
            log_fail("DB: No active store locations")

        # 2. Verify print format in DB
        pf = frappe.db.get_value("Print Format", "pos_receipt", ["name", "doc_type", "html"], as_dict=True)
        if pf:
            html_len = len(pf.html or "")
            if html_len > 100:
                log_pass(f"DB: Print Format 'pos_receipt' registered ({html_len} bytes)")
            else:
                log_fail("DB: Print Format 'pos_receipt' has empty HTML")
        else:
            log_fail("DB: Print Format 'pos_receipt' not in database")

        # 3. Verify POS opening entries exist (indicates system was used)
        pos_count = frappe.db.count("POS Opening Entry", {"status": "Open"})
        log_info(f"DB: {pos_count} open POS sessions")

        # 4. Verify Sales Invoices exist
        inv_count = frappe.db.count("Sales Invoice", {"docstatus": 1})
        log_info(f"DB: {inv_count} submitted Sales Invoices")

        frappe.destroy()
    except Exception as e:
        log_fail(f"DB check failed: {e}")

    return True


def main():
    print("=" * 60)
    print("  ZEVAR POS GO-LIVE SMOKE TEST")
    print(f"  Site: {SITE} | URL: {BASE_URL}")
    print("=" * 60)

    os.chdir(BENCH_DIR)

    test_backend_api_health()
    test_frontend_build()
    test_database_consistency()

    print("\n" + "=" * 60)
    if failures:
        print(f"  RESULT: ❌ {len(failures)} failures found")
        for f in failures:
            print(f"    - {f}")
        print("  DO NOT GO LIVE — fix failures first")
        sys.exit(1)
    else:
        print("  RESULT: ✅ All systems green — ready for go-live")
        sys.exit(0)


if __name__ == "__main__":
    main()
