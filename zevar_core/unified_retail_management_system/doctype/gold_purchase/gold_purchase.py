# Copyright (c) 2026, Zevar and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class GoldPurchase(Document):
    def validate(self):
        self._calculate_item_values()
        self._calculate_totals()
        self._validate_totals()
        self._validate_cash_threshold()

    def on_submit(self):
        self._create_payment_entry()
        self._create_stock_entry()
        self._log_audit_event()

    def on_cancel(self):
        self._cancel_linked_entries()

    def _calculate_item_values(self):
        from zevar_core.api.pricing import _get_gold_rate
        from zevar_core.constants import PURITY_VALUES

        for item in self.items:
            item.net_weight_g = (item.gross_weight_g or 0) - (item.stone_weight_g or 0)
            if item.net_weight_g <= 0:
                item.calculated_value = 0
                item.rate_per_gram = 0
                continue

            purity_pct = PURITY_VALUES.get(item.purity, 0)
            item.purity_percentage = purity_pct * 100

            metal = item.metal_type
            if metal in ("White Gold", "Rose Gold"):
                metal = "Yellow Gold"

            rate = _get_gold_rate(metal, item.purity)
            item.rate_per_gram = rate
            item.calculated_value = round(item.net_weight_g * rate, 2)

            if not item.agreed_value:
                item.agreed_value = item.calculated_value

    def _calculate_totals(self):
        self.total_gross_weight = sum(i.gross_weight_g or 0 for i in self.items)
        self.total_net_weight = sum(i.net_weight_g or 0 for i in self.items)
        self.total_calculated_value = sum(i.calculated_value or 0 for i in self.items)
        self.total_agreed_value = sum(i.agreed_value or 0 for i in self.items)

    def _validate_totals(self):
        if not self.items:
            frappe.throw(_("At least one scrap item is required"))

        for i, item in enumerate(self.items, 1):
            if (item.gross_weight_g or 0) <= 0:
                frappe.throw(_("Row {0}: Gross weight must be greater than 0").format(i))
            if (item.agreed_value or 0) <= 0:
                frappe.throw(_("Row {0}: Agreed value must be greater than 0").format(i))

        if self.total_agreed_value <= 0:
            frappe.throw(_("Total purchase amount must be greater than 0"))

    def _validate_cash_threshold(self):
        from zevar_core.constants import CASH_REPORTING_THRESHOLD

        if self.payment_method == "Cash" and self.total_agreed_value >= CASH_REPORTING_THRESHOLD:
            if not self.id_type or not self.id_number:
                frappe.throw(
                    _(
                        "ID verification is required for cash purchases of ${0} or more "
                        "(IRS Form 8300 threshold)"
                    ).format(int(CASH_REPORTING_THRESHOLD))
                )

    def _create_payment_entry(self):
        company = frappe.defaults.get_user_default("Company")
        if not company:
            return

        mode_of_payment = self.payment_method
        if mode_of_payment not in ("Cash", "Check", "Wire Transfer", "Zelle"):
            mode_of_payment = "Cash"

        pe = frappe.get_doc(
            {
                "doctype": "Payment Entry",
                "payment_type": "Pay",
                "posting_date": self.purchase_date.strftime("%Y-%m-%d") if self.purchase_date else frappe.utils.today(),
                "mode_of_payment": mode_of_payment,
                "party_type": "Customer",
                "party": self.customer,
                "paid_from": frappe.db.get_value("Company", company, "default_cash_account"),
                "paid_to": self._get_purchase_account(company),
                "paid_amount": self.total_agreed_value,
                "received_amount": self.total_agreed_value,
                "reference_no": self.reference_number or self.name,
                "reference_date": frappe.utils.today(),
                "remark": f"Gold scrap purchase - {self.name}",
            }
        )
        pe.insert(ignore_permissions=True)
        pe.submit()
        self.db_set("payment_entry", pe.name)
        self.db_set("payment_status", "Paid")

    def _get_purchase_account(self, company):
        if self.purchase_account:
            return self.purchase_account
        account = frappe.db.get_value("Company", company, "stock_adjustment_account")
        return account or frappe.db.get_value("Company", company, "default_inventory_account")

    def _create_stock_entry(self):
        company = frappe.defaults.get_user_default("Company")
        if not company:
            return

        store = frappe.get_doc("Store Location", self.store_location)
        target_warehouse = store.default_warehouse
        if not target_warehouse:
            return

        se = frappe.get_doc(
            {
                "doctype": "Stock Entry",
                "stock_entry_type": "Material Receipt",
                "company": company,
                "to_warehouse": target_warehouse,
                "items": [],
            }
        )

        for item in self.items:
            scrap_item = self._get_or_create_scrap_item(item, company)
            se.append(
                "items",
                {
                    "item_code": scrap_item,
                    "qty": item.net_weight_g,
                    "uom": "Gram",
                    "t_warehouse": target_warehouse,
                    "basic_rate": item.rate_per_gram or 0,
                    "valuation_rate": item.rate_per_gram or 0,
                },
            )

        se.insert(ignore_permissions=True)
        se.submit()
        self.db_set("stock_entry", se.name)

    def _get_or_create_scrap_item(self, item, company):
        item_name = f"SCRAP-{item.metal_type.replace(' ', '')}-{item.purity}"
        if frappe.db.exists("Item", item_name):
            return item_name

        from zevar_core.constants import PURITY_VALUES

        purity_pct = PURITY_VALUES.get(item.purity, 0)
        scrap_item = frappe.get_doc(
            {
                "doctype": "Item",
                "item_code": item_name,
                "item_name": f"Scrap {item.metal_type} {item.purity}",
                "item_group": "Raw Materials",
                "stock_uom": "Gram",
                "is_stock_item": 1,
                "valuation_method": "Moving Average",
                "custom_metal_type": item.metal_type,
                "custom_purity": item.purity,
                "custom_net_weight_g": 1,
            }
        )
        scrap_item.insert(ignore_permissions=True)
        return scrap_item.name

    def _log_audit_event(self):
        if frappe.db.exists("DocType", "POS Audit Log"):
            frappe.get_doc(
                {
                    "doctype": "POS Audit Log",
                    "event_type": "gold_purchase",
                    "reference_doctype": "Gold Purchase",
                    "reference_name": self.name,
                    "user": frappe.session.user,
                    "details": f"Gold scrap purchase from {self.customer_name} - ${self.total_agreed_value}",
                }
            ).insert(ignore_permissions=True)

    def _cancel_linked_entries(self):
        for ref_field in ("payment_entry", "stock_entry"):
            ref_name = self.get(ref_field)
            if ref_name and frappe.db.exists(ref_field.replace("_", " ").title().replace(" ", ""), ref_name):
                doc = frappe.get_doc(ref_field.replace("_", " ").title().replace(" ", ""), ref_name)
                if doc.docstatus == 1:
                    doc.cancel()
