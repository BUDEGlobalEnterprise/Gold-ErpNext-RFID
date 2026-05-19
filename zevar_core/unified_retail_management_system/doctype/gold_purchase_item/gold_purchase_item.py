# Copyright (c) 2026, Zevar and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class GoldPurchaseItem(Document):
    def validate(self):
        self.net_weight_g = (self.gross_weight_g or 0) - (self.stone_weight_g or 0)
        if self.net_weight_g <= 0:
            return

        from zevar_core.constants import PURITY_VALUES
        purity_key = self.purity
        self.purity_percentage = (PURITY_VALUES.get(purity_key, 0)) * 100
