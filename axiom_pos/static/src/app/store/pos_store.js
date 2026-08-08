/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

function axiomParseColor(input, fallback = { r: 0, g: 0, b: 0 }) {
    if (!input) {
        return { ...fallback };
    }
    const value = String(input).trim();
    const rgba = value.match(
        /^rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})(?:\s*,\s*[\d.]+)?\s*\)$/i
    );
    if (rgba) {
        return {
            r: Math.min(255, parseInt(rgba[1], 10)),
            g: Math.min(255, parseInt(rgba[2], 10)),
            b: Math.min(255, parseInt(rgba[3], 10)),
        };
    }
    let h = value.replace("#", "");
    if (h.length === 3) {
        h = h
            .split("")
            .map((c) => c + c)
            .join("");
    }
    if (h.length !== 6) {
        return { ...fallback };
    }
    const n = parseInt(h, 16);
    if (Number.isNaN(n)) {
        return { ...fallback };
    }
    return {
        r: (n >> 16) & 255,
        g: (n >> 8) & 255,
        b: n & 255,
    };
}

function axiomRgbToHex({ r, g, b }) {
    const to = (n) => Math.max(0, Math.min(255, Math.round(n))).toString(16).padStart(2, "0");
    return `#${to(r)}${to(g)}${to(b)}`;
}

function axiomRgbToRgba({ r, g, b }, alpha = 1) {
    return `rgba(${Math.round(r)}, ${Math.round(g)}, ${Math.round(b)}, ${alpha})`;
}

/** Mix color A toward color B by percent (0–100). */
function axiomMix(a, b, percent) {
    const t = Math.max(0, Math.min(100, percent)) / 100;
    return {
        r: a.r + (b.r - a.r) * t,
        g: a.g + (b.g - a.g) * t,
        b: a.b + (b.b - a.b) * t,
    };
}

function axiomLuminance({ r, g, b }) {
    const lin = (c) => {
        const s = c / 255;
        return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
    };
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
}

function axiomContrastText(bg, text, light = { r: 255, g: 255, b: 255 }, dark = { r: 17, g: 24, b: 39 }) {
    const bgLum = axiomLuminance(bg);
    const textLum = axiomLuminance(text);
    const contrast = (Math.max(bgLum, textLum) + 0.05) / (Math.min(bgLum, textLum) + 0.05);
    if (contrast >= 3.2) {
        return text;
    }
    return bgLum > 0.45 ? dark : light;
}

function hexToRgba(hex, alpha = 0.6) {
    return axiomRgbToRgba(axiomParseColor(hex), alpha);
}

/**
 * Layout theme only: body from config, header ~28% thicker (mix toward text).
 */
function axiomBuildLayoutTheme(bgHex, textHex) {
    const bg = axiomParseColor(bgHex, { r: 240, g: 238, b: 238 });
    const text = axiomParseColor(textHex, { r: 55, g: 65, b: 81 });
    const header = axiomMix(bg, text, 28);
    return {
        bg: axiomRgbToHex(bg),
        text: axiomRgbToHex(text),
        header: axiomRgbToHex(header),
        headerText: axiomRgbToHex(axiomContrastText(header, text)),
    };
}

patch(PosStore.prototype, {
    async processServerData() {
        await super.processServerData(...arguments);
        this.axiomApplyScreenTheme();
    },

    async afterProcessServerData() {
        const result = await super.afterProcessServerData(...arguments);
        this.axiomApplyScreenTheme();
        return result;
    },

    /**
     * Read a pos.config value with raw fallback (Odoo 18 reactive models).
     */
    axiomConfigGet(fieldName, fallback = false) {
        const config = this.config || {};
        const raw = config.raw || {};
        const value = config[fieldName] ?? raw[fieldName];
        if (value === undefined || value === null || value === false || value === "") {
            return fallback;
        }
        return value;
    },

    axiomApplyScreenTheme() {
        const root = document.querySelector(".pos") || document.body;
        if (!document.querySelector(".pos")) {
            setTimeout(() => this.axiomApplyScreenTheme(), 50);
        }
        const bg = this.axiomConfigGet("axiom_theme_bg_color", "#F0EEEE");
        const text = this.axiomConfigGet("axiom_theme_text_color", "#374151");
        const layout = axiomBuildLayoutTheme(bg, text);
        const priceBg = this.axiomConfigGet("axiom_price_bg_color", "#000000");
        const priceText = this.axiomConfigGet("axiom_price_text_color", "#FFFFFF");
        let priceSize = this.axiomConfigGet("axiom_price_font_size", "20px");
        if (priceSize && !/[a-z%]+$/i.test(String(priceSize).trim())) {
            priceSize = `${String(priceSize).trim()}px`;
        }
        const alignment = this.axiomConfigGet("axiom_price_alignment", "top_right");

        root.classList.add("axiom-pos-theme");
        root.style.setProperty("--axiom-pos-bg", layout.bg);
        root.style.setProperty("--axiom-pos-text", layout.text);
        root.style.setProperty("--axiom-pos-header", layout.header);
        root.style.setProperty("--axiom-pos-header-text", layout.headerText);
        root.style.setProperty("--axiom-price-bg", hexToRgba(priceBg, 0.6));
        root.style.setProperty("--axiom-price-text", priceText);
        root.style.setProperty("--axiom-price-size", priceSize);
        root.dataset.axiomPriceAlign = alignment;
    },

    /**
     * POS HR advanced / admin employee, or non-HR cashier with manager role.
     * Basic employees must never inherit the session opener's admin rights.
     */
    axiomCashierIsPosAdmin() {
        if (this.config?.module_pos_hr || this.axiomConfigGet("module_pos_hr")) {
            if (typeof this.employeeIsAdmin === "boolean") {
                return this.employeeIsAdmin;
            }
            const cashier = this.get_cashier?.();
            const role = cashier?._role || cashier?.raw?._role;
            return role === "manager";
        }
        const cashier = this.get_cashier?.() || this.user;
        const role = cashier?._role || cashier?.raw?._role || cashier?.role || cashier?.raw?.role;
        return role === "manager";
    },

    /**
     * Resolve a right flag from the active cashier only.
     * Never fall back to the session opener (this.user) when POS HR is on —
     * that was granting admin print rights to basic cashiers.
     */
    _axiomGetRight(fieldName) {
        const readFlag = (record) => {
            if (!record) {
                return undefined;
            }
            if (record[fieldName] !== undefined && record[fieldName] !== null) {
                return Boolean(record[fieldName]);
            }
            if (record.raw && record.raw[fieldName] !== undefined && record.raw[fieldName] !== null) {
                return Boolean(record.raw[fieldName]);
            }
            return undefined;
        };

        const cashier = this.get_cashier?.();
        const usePosHr = Boolean(this.config?.module_pos_hr || this.axiomConfigGet("module_pos_hr"));

        if (cashier) {
            let value = readFlag(cashier);
            if (value !== undefined) {
                return value;
            }

            let userRecord = cashier.user_id;
            if (userRecord && typeof userRecord === "number") {
                userRecord = this.models?.["res.users"]?.get?.(userRecord);
            }
            value = readFlag(userRecord);
            if (value !== undefined) {
                return value;
            }

            const cashierUserId =
                typeof this.get_cashier_user_id === "function" ? this.get_cashier_user_id() : null;
            if (cashierUserId) {
                const byId =
                    typeof cashierUserId === "object"
                        ? cashierUserId
                        : this.models?.["res.users"]?.get?.(cashierUserId);
                value = readFlag(byId);
                if (value !== undefined) {
                    return value;
                }
            }

            // With POS HR, the cashier is an employee — do not inherit session user rights.
            if (usePosHr || cashier.model?.modelName === "hr.employee") {
                return false;
            }
        }

        return Boolean(readFlag(this.user));
    },

    axiomCashierHasShowProductPrice() {
        const usePosHr = Boolean(this.config?.module_pos_hr || this.axiomConfigGet("module_pos_hr"));
        if (usePosHr) {
            const cashier = this.get_cashier?.();
            if (!cashier) {
                return true;
            }
            // Employees without a linked Odoo user: show prices by default.
            if (!(cashier.user_id || cashier.raw?.user_id)) {
                return true;
            }
        }
        return this._axiomGetRight("axiom_show_product_price");
    },

    axiomCashierHasDraftPrinting() {
        // Draft / pro forma: POS HR advanced (admin) employees only.
        if (this.config?.module_pos_hr || this.axiomConfigGet("module_pos_hr")) {
            return this.axiomCashierIsPosAdmin();
        }
        return this._axiomGetRight("axiom_enable_draft_printing");
    },

    axiomCashierCanViewProductInfo() {
        const mode = this.axiomConfigGet("axiom_product_info_access", "admin");
        if (mode === "none") {
            return false;
        }
        if (mode === "all") {
            return true;
        }
        // admin (default): POS HR advanced / admin employees, or group right
        if (this.config?.module_pos_hr || this.axiomConfigGet("module_pos_hr")) {
            return this.axiomCashierIsPosAdmin();
        }
        if (this._axiomGetRight("axiom_can_view_product_info")) {
            return true;
        }
        return this.axiomCashierIsPosAdmin();
    },

    /**
     * Paid *reprint* permission only (nb_print > 0 / ticket reprint).
     * First print of a newly paid order is never gated by this.
     */
    axiomCashierCanReprintPaid() {
        const mode = this.axiomConfigGet("axiom_paid_reprint_access", "admin");
        // Legacy boolean configs (pre-1.9): true -> admin, false -> all
        if (mode === true || mode === "True") {
            return this._axiomPaidReprintAdminOnly();
        }
        if (mode === false || mode === "False") {
            return true;
        }
        if (mode === "none") {
            return false;
        }
        if (mode === "all") {
            return true;
        }
        // admin (default)
        return this._axiomPaidReprintAdminOnly();
    },

    /** @deprecated use axiomCashierCanReprintPaid — kept for older call sites */
    axiomCashierCanPrint() {
        return this.axiomCashierCanReprintPaid();
    },

    _axiomPaidReprintAdminOnly() {
        if (this.config?.module_pos_hr || this.axiomConfigGet("module_pos_hr")) {
            return this.axiomCashierIsPosAdmin();
        }
        return (
            this._axiomGetRight("axiom_can_reprint_paid") || this._axiomGetRight("axiom_can_print")
        );
    },

    axiomIsReprint(order) {
        return Boolean(order && (order.nb_print || 0) > 0);
    },

    /** Resolve draft XML from config (stored related) or linked pos.receipt. */
    axiomGetDraftDesignXml() {
        const direct = this.axiomConfigGet("axiom_draft_design_receipt", "");
        if (direct) {
            return direct;
        }
        let design = this.config?.axiom_draft_receipt_design_id;
        if (!design && this.config?.raw?.axiom_draft_receipt_design_id) {
            design = this.config.raw.axiom_draft_receipt_design_id;
        }
        if (typeof design === "number") {
            design = this.models?.["pos.receipt"]?.get?.(design);
        }
        if (Array.isArray(design)) {
            design = this.models?.["pos.receipt"]?.get?.(design[0]);
        }
        return design?.design_receipt || design?.raw?.design_receipt || "";
    },

    /**
     * Header / ticket print visibility.
     * Draft → draft right. Paid first print → always. Paid reprint → reprint right.
     */
    axiomCashierCanPrintOrder(order = this.get_order()) {
        if (!order?.lines?.length) {
            return false;
        }
        if (!order.finalized) {
            return this.axiomCashierHasDraftPrinting();
        }
        if (!this.axiomIsReprint(order)) {
            return true; // first paid print always allowed
        }
        return this.axiomCashierCanReprintPaid();
    },

    /**
     * Build print data for draft bills using the selected pos.receipt XML design.
     * Do not attach draft flags to paid orderExportForPrinting().
     */
    axiomBuildDraftReceiptData(order) {
        // Use this.orderExportForPrinting — super.X is only valid when overriding X.
        const data = this.orderExportForPrinting(order);
        data.isBill = true;
        data.axiom_is_draft_receipt = true;
        data.axiom_draft_design_receipt = this.axiomGetDraftDesignXml();
        data.show_change = false;
        data.paymentlines = [];
        return data;
    },

    /**
     * Draft print uses the same printer API as paid receipts:
     * this.printer.print(OrderReceipt, props, { webPrintFallback: true }).
     */
    async axiomPrintDraftReceipt(order, { basic = false } = {}) {
        if (!order?.lines?.length) {
            return false;
        }
        if (!this.axiomCashierHasDraftPrinting()) {
            this.env.services.notification.add(
                _t("You do not have permission to print draft bills."),
                { type: "warning" }
            );
            return false;
        }
        const data = this.axiomBuildDraftReceiptData(order);
        try {
            return await this.printer.print(
                OrderReceipt,
                {
                    data,
                    formatCurrency: this.env.utils.formatCurrency,
                    basic_receipt: basic,
                },
                { webPrintFallback: true }
            );
        } catch (error) {
            this.env.services.notification.add(
                error?.body || error?.message || _t("Printing failed."),
                { type: "danger" }
            );
            return false;
        }
    },

    async axiomPrintOrder(order) {
        if (!order?.lines?.length) {
            return false;
        }
        // Unpaid → draft template. Paid → paid template (reprint gated).
        if (!order.finalized) {
            return this.axiomPrintDraftReceipt(order);
        }
        if (this.axiomIsReprint(order) && !this.axiomCashierCanReprintPaid()) {
            this.env.services.notification.add(
                _t("You do not have permission to reprint paid orders."),
                { type: "warning" }
            );
            return false;
        }
        return this.printReceipt({ order });
    },

    async printReceipt({
        basic = false,
        order = this.get_order(),
        printBillActionTriggered = false,
    } = {}) {
        // Explicit bill / draft action
        if (printBillActionTriggered) {
            return this.axiomPrintDraftReceipt(order, { basic });
        }
        // Only gate *reprints* of paid orders — never the first print after payment.
        if (order?.finalized && this.axiomIsReprint(order) && !this.axiomCashierCanReprintPaid()) {
            this.env.services.notification.add(
                _t("You do not have permission to reprint paid orders."),
                { type: "warning" }
            );
            return false;
        }
        return super.printReceipt(...arguments);
    },
});

