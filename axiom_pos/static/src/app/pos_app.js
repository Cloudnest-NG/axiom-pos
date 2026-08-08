/** @odoo-module */

import { Chrome } from "@point_of_sale/app/pos_app";
import { patch } from "@web/core/utils/patch";
import { onMounted } from "@odoo/owl";

patch(Chrome.prototype, {
    setup() {
        super.setup(...arguments);
        onMounted(() => {
            this.pos.axiomApplyScreenTheme?.();
        });
    },
});
