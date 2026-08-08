/** @odoo-module */

import { Component, xml } from "@odoo/owl";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { OrderWidget } from "@point_of_sale/app/generic_components/order_widget/order_widget";
import { ReceiptHeader } from "@point_of_sale/app/screens/receipt_screen/receipt/receipt_header/receipt_header";
import { omit } from "@web/core/utils/objects";
import { useService } from "@web/core/utils/hooks";
import { formatDateTime } from "@web/core/l10n/dates";

/**
 * Draft / pro forma receipt.
 * Renders the selected pos.receipt XML design when configured; otherwise
 * falls back to the built-in draft layout.
 */
export class DraftOrderReceipt extends Component {
    static template = "axiom_pos.DraftOrderReceipt";
    static components = {
        Orderline,
        OrderWidget,
        ReceiptHeader,
    };
    static props = {
        data: Object,
        formatCurrency: Function,
        basic_receipt: { type: Boolean, optional: true },
    };
    static defaultProps = {
        basic_receipt: false,
    };

    setup() {
        this.pos = useService("pos");
        this._draftTemplateCache = { design: null, Component: null };
    }

    omit(...args) {
        return omit(...args);
    }

    doesAnyOrderlineHaveTaxLabel() {
        return (this.props.data.orderlines || []).some((line) => line.taxGroupLabels);
    }

    get designReceipt() {
        return (
            this.props.data.axiom_draft_design_receipt ||
            this.pos?.axiomConfigGet?.("axiom_draft_design_receipt", "") ||
            ""
        );
    }

    get isCustomDraft() {
        return Boolean(this.designReceipt && this.templateComponent);
    }

    get templateComponent() {
        const design = this.designReceipt;
        if (!design) {
            return null;
        }
        if (this._draftTemplateCache.design === design && this._draftTemplateCache.Component) {
            return this._draftTemplateCache.Component;
        }
        try {
            class AxiomDraftReceiptTemplate extends Component {
                // OWL requires a static props description for dynamic components.
                static props = { "*": true };
                static template = xml`${design}`;
            }
            this._draftTemplateCache = { design, Component: AxiomDraftReceiptTemplate };
            return AxiomDraftReceiptTemplate;
        } catch (error) {
            console.error("Axiom draft receipt: invalid XML design", error);
            this._draftTemplateCache = { design: null, Component: null };
            return null;
        }
    }

    get templateProps() {
        const config = this.pos?.config || {};
        const company = this.pos?.company || {};
        const data = this.props?.data || {};
        const formatCurrency = this.props?.formatCurrency || (() => "");
        const order = this.pos?.get_order?.() || null;

        let partner = order?.get_partner?.() || order?.partner_id || null;
        if (typeof partner === "number" && this.pos?.models?.["res.partner"]) {
            partner = this.pos.models["res.partner"].get(partner) || null;
        }
        const partnerName = (
            order?.get_partner_name?.() ||
            partner?.name ||
            partner?.display_name ||
            ""
        ).trim();
        const partnerPhone = partner?.mobile || partner?.phone || "";

        return {
            data,
            order,
            partner,
            showCustomer: Boolean(partnerName),
            partnerName,
            partnerPhone,
            printedAt: formatDateTime(luxon.DateTime.now()),
            orderStatus: order?.finalized ? "Settled" : "Draft",
            createdBy: order?.getCashierName?.() || data.cashier || "",
            branchLabel: company.city || company.street2 || company.street || "",
            companyName: company.name || "",
            companyPhone: company.phone || "",
            logo: config.pos_brand_logo || config.logo || null,
            formatCurrency,
            isBill: true,
        };
    }
}
