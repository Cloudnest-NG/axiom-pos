/** @odoo-module */

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

patch(ProductScreen.prototype, {
    getProductPrice(product) {
        if (!this.pos.axiomCashierHasShowProductPrice()) {
            return "";
        }
        return super.getProductPrice(product);
    },

    get selectedOrderlineTotal() {
        if (!this.pos.axiomCashierHasShowProductPrice()) {
            return "";
        }
        return super.selectedOrderlineTotal;
    },

    async onProductInfoClick(product) {
        if (!this.pos.axiomCashierCanViewProductInfo()) {
            this.env.services.notification.add(
                _t("You do not have permission to view product info / on-hand quantity."),
                { type: "warning" }
            );
            return;
        }
        return super.onProductInfoClick(product);
    },
});
