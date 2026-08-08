/** @odoo-module */

import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { useAsyncLockedMethod } from "@point_of_sale/app/utils/hooks";
import { patch } from "@web/core/utils/patch";

patch(ControlButtons.prototype, {
    setup() {
        super.setup(...arguments);
        this.clickPrintDraft = useAsyncLockedMethod(this.clickPrintDraft.bind(this));
    },

    async clickPrintDraft() {
        const order = this.pos.get_order();
        await this.pos.axiomPrintOrder(order);
    },
});
