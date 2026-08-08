/** @odoo-module */

import { Navbar } from "@point_of_sale/app/navbar/navbar";
import { useAsyncLockedMethod } from "@point_of_sale/app/utils/hooks";
import { patch } from "@web/core/utils/patch";

patch(Navbar.prototype, {
    setup() {
        super.setup(...arguments);
        this.axiomClickPrint = useAsyncLockedMethod(this.axiomClickPrint.bind(this));
    },

    /** Hide print entirely when cashier cannot print the current order. */
    get axiomCanShowHeaderPrint() {
        const order = this.pos.get_order();
        return Boolean(order?.lines?.length && this.pos.axiomCashierCanPrintOrder(order));
    },

    async axiomClickPrint() {
        const order = this.pos.get_order();
        if (!this.axiomCanShowHeaderPrint) {
            return;
        }
        await this.pos.axiomPrintOrder(order);
    },
});
