import frappe
from frappe import _
from frappe.utils import flt

class CashMovement(frappe.model.document.Document):
    def validate(self):
        self._validate_session_is_open()
        self._validate_amount_positive()
        self._validate_manager_authorization()

    def on_submit(self):
        from zevar_core.api.audit_log import log_event_safely
        log_event_safely(event_type="cash_movement", details={
            "movement_name": self.name, "session": self.session,
            "movement_type": self.movement_type, "amount": flt(self.amount),
            "reason": self.reason, "authorized_by": self.authorized_by,
        }, reference_document=self.name, reference_type="Cash Movement")

    def _validate_session_is_open(self):
        if not self.session:
            frappe.throw(_("Session is required"))
        session = frappe.get_doc("POS Opening Entry", self.session)
        if session.status != "Open":
            frappe.throw(_("Cannot add cash movement to a closed session"))

    def _validate_amount_positive(self):
        if flt(self.amount) <= 0:
            frappe.throw(_("Amount must be greater than zero"))

    def _validate_manager_authorization(self):
        if self.movement_type == "Cash Out" and flt(self.amount) > 100:
            if not self.authorized_by:
                frappe.throw(_("Cash out of ${0} requires manager authorization").format(self.amount))
            roles = frappe.get_roles(self.authorized_by)
            if "Sales Manager" not in roles and "System Manager" not in roles and "Store Manager" not in roles:
                frappe.throw(_("Authorizing user must be a manager"))