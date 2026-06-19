import frappe
import json
from zevar_core.api.special_order import create_special_order

def run():
    payload = {
        'order_id': 'SPO-TEST-123', 
        'customer': 'Test Customer', 
        'warehouse': 'Stores - ZC', 
        'metal_type': 'Gold', 
        'metal_purity': '14K', 
        'metal_weight': 6, 
        'labor_cost': 60, 
        'overhead_cost': 0, 
        'margin_percent': 30, 
        'stones': [{'id': 'stn_rlpqxv3e', 'stoneType': 'Diamond', 'caratWeight': '1', 'cut': 'Excellent', 'color': 'F', 'clarity': 'VVS2', 'shape': 'Princess', 'source': 'atlantic dia company', 'sourcingMethod': 'Memo Request', 'supplierId': 'ATLANTIC DIA COMP', 'unitPrice': '1500'}], 
        'notes': ''
    }
    
    if not frappe.db.exists("Customer", "Test Customer"):
        frappe.get_doc({"doctype": "Customer", "customer_name": "Test Customer", "customer_group": "All Customer Groups", "territory": "All Territories"}).insert(ignore_permissions=True)
    
    try:
        res = create_special_order(payload)
        print("SUCCESS:", res)
    except Exception as e:
        import traceback
        traceback.print_exc()
