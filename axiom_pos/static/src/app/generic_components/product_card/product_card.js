/** @odoo-module */

import { ProductCard } from "@point_of_sale/app/generic_components/product_card/product_card";
import { patch } from "@web/core/utils/patch";

Object.assign(ProductCard.props, {
    price: { type: String, optional: true },
});

function hexToRgba(hex, alpha = 0.6) {
    if (!hex) {
        return `rgba(0, 0, 0, ${alpha})`;
    }
    const value = String(hex).trim();
    if (value.startsWith("rgba") || value.startsWith("rgb")) {
        return value;
    }
    let h = value.replace("#", "");
    if (h.length === 3) {
        h = h
            .split("")
            .map((c) => c + c)
            .join("");
    }
    if (h.length !== 6) {
        return `rgba(0, 0, 0, ${alpha})`;
    }
    const n = parseInt(h, 16);
    if (Number.isNaN(n)) {
        return `rgba(0, 0, 0, ${alpha})`;
    }
    return `rgba(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}, ${alpha})`;
}

patch(ProductCard.prototype, {
    _axiomConfigGet(fieldName, fallback) {
        const pos = this.env.services.pos;
        if (pos && typeof pos.axiomConfigGet === "function") {
            return pos.axiomConfigGet(fieldName, fallback);
        }
        const config = pos?.config || {};
        const raw = config.raw || {};
        return config[fieldName] ?? raw[fieldName] ?? fallback;
    },

    get axiomDisplayPrice() {
        const pos = this.env.services.pos;
        if (!pos) {
            return "";
        }
        if (
            typeof pos.axiomCashierHasShowProductPrice === "function" &&
            !pos.axiomCashierHasShowProductPrice()
        ) {
            return "";
        }
        if (this.props.price) {
            return this.props.price;
        }
        if (!this.props.product || typeof pos.getProductPriceFormatted !== "function") {
            return "";
        }
        return pos.getProductPriceFormatted(this.props.product) || "";
    },

    get axiomPriceStyleString() {
        let size = this._axiomConfigGet("axiom_price_font_size", "20px");
        if (size && !/[a-z%]+$/i.test(String(size).trim())) {
            size = `${String(size).trim()}px`;
        }
        const bgHex = this._axiomConfigGet("axiom_price_bg_color", "#000000");
        const color = this._axiomConfigGet("axiom_price_text_color", "#FFFFFF");
        // 60% transparent background as requested
        const bg = hexToRgba(bgHex, 0.6);
        return `background-color: ${bg}; color: ${color}; font-size: ${size};`;
    },

    get axiomPricePositionClass() {
        const alignment = this._axiomConfigGet("axiom_price_alignment", "top_right");
        return `axiom-product-price axiom-price-${alignment}`;
    },
});
