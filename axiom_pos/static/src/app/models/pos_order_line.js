/** @odoo-module */

import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { patch } from "@web/core/utils/patch";

patch(PosOrderline.prototype, {
    _axiomCanShowPrices() {
        const configId = this.config?.id;
        if (!configId) {
            return false;
        }
        const cashierId = Number(sessionStorage.getItem(`connected_cashier_${configId}`));
        const users = this.models["res.users"];
        let cashier = cashierId ? users.get(cashierId) : null;
        if (!cashier) {
            cashier = users.get(this.session?.user_id?.id);
        }
        if (!cashier) {
            cashier = users.getFirst();
        }
        return Boolean(cashier?.axiom_show_product_price ?? cashier?.raw?.axiom_show_product_price);
    },

    getDisplayData() {
        const data = super.getDisplayData(...arguments);
        if (!this._axiomCanShowPrices()) {
            return {
                ...data,
                price: "",
                unitPrice: "",
                oldUnitPrice: "",
                price_without_discount: "",
            };
        }
        return data;
    },
});
