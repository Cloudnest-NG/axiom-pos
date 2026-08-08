/** @odoo-module */

import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { patch } from "@web/core/utils/patch";
import { Component, xml } from "@odoo/owl";

/**
 * Draft bills: use selected draft XML design (never paid/Labule custom design).
 * Paid receipts: unchanged (Labule / standard via super).
 */
patch(OrderReceipt.prototype, {
    _axiomIsDraftReceipt() {
        const data = this.props?.data || {};
        return Boolean(data.axiom_is_draft_receipt || data.isBill);
    },

    _axiomDraftDesign() {
        return this.props?.data?.axiom_draft_design_receipt || "";
    },

    get isTrue() {
        if (this._axiomIsDraftReceipt()) {
            // Only render custom XML when a draft design is configured.
            return Boolean(this._axiomDraftDesign());
        }
        return super.isTrue;
    },

    get templateComponent() {
        if (this._axiomIsDraftReceipt()) {
            const design = this._axiomDraftDesign();
            if (!design) {
                return null;
            }
            try {
                return class AxiomDraftReceiptTemplate extends Component {
                    static props = { "*": true };
                    static template = xml`${design}`;
                };
            } catch (error) {
                console.error("Axiom draft receipt: invalid XML design", error);
                return null;
            }
        }
        return super.templateComponent;
    },
});
