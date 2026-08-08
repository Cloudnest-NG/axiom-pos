# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    from odoo.addons.axiom_pos.hooks import _axiom_fill_pos_config_defaults
    _axiom_fill_pos_config_defaults(env)
    # Ensure required selection columns are never NULL.
    cr.execute(
        """
        UPDATE pos_config
           SET axiom_product_info_access = 'admin'
         WHERE axiom_product_info_access IS NULL OR axiom_product_info_access = ''
        """
    )
    cr.execute(
        """
        UPDATE pos_config
           SET axiom_paid_reprint_access = 'admin'
         WHERE axiom_paid_reprint_access IS NULL OR axiom_paid_reprint_access = ''
        """
    )
