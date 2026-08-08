/** @odoo-module */

import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { useAsyncLockedMethod } from "@point_of_sale/app/utils/hooks";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

patch(TicketScreen.prototype, {
    setup() {
        super.setup(...arguments);
        this.axiomPrintOrderRow = useAsyncLockedMethod(this.axiomPrintOrderRow.bind(this));
    },

    axiomCanShowOrderPrint(order) {
        return this.pos.axiomCashierCanPrintOrder(order);
    },

    async axiomPrintOrderRow(order) {
        await this.pos.axiomPrintOrder(order);
    },

    async print(order) {
        // Ticket "Print" is always a reprint of an existing order.
        if (!this.pos.axiomCashierCanReprintPaid()) {
            this.env.services.notification.add(
                _t("You do not have permission to reprint paid orders."),
                { type: "warning" }
            );
            return;
        }
        return super.print(order);
    },
});
