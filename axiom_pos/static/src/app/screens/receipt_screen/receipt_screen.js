/** @odoo-module */

import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { patch } from "@web/core/utils/patch";

patch(ReceiptScreen.prototype, {
    /**
     * First print after payment is always shown.
     * Reprint button only when cashier has reprint rights.
     */
    get axiomCanPrint() {
        const order = this.currentOrder;
        if (!order) {
            return false;
        }
        if ((order.nb_print || 0) === 0) {
            return true;
        }
        return this.pos.axiomCashierCanReprintPaid();
    },
});
