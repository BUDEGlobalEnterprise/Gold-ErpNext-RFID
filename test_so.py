import frappe
import json
from zevar_core.api.special_order import create_special_order

def run():
    payload = {
        'order_id': 'SPO-TEST', 
        'customer': '', 
        'warehouse': '', 
        'metal_type': 'Gold', 
        'metal_purity': '14K', 
        'metal_weight': 6, 
        'labor_cost': 60, 
        'overhead_cost': 0, 
        'margin_percent': 30, 
        'stones': [{'id': 'stn_rlpqxv3e', 'stoneType': 'Diamond', 'caratWeight': '1', 'cut': 'Excellent', 'color': 'F', 'clarity': 'VVS2', 'shape': 'Princess', 'source': 'atlantic dia company', 'sourcingMethod': 'Memo Request', 'supplierId': 'ATLANTIC DIA COMP', 'unitPrice': '1500'}], 
        'notes': ''
    }
    try:
        # Try without customer
        create_special_order(payload)
    except Exception as e:
        print(f"Exception 1 (No Customer): {type(e).__name__} - {str(e)}")
        
    payload['customer'] = "Test Customer"
    # Ensure customer exists
    if not frappe.db.exists("Customer", "Test Customer"):
        frappe.get_doc({"doctype": "Customer", "customer_name": "Test Customer"}).insert(ignore_permissions=True)
    
    try:
        # Try with customer
        res = create_special_order(payload)
        print(f"Success: {res}")
    except Exception as e:
        print(f"Exception 2 (With Customer): {type(e).__name__} - {str(e)}")
