# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    Config = env['pos.config'].sudo()
    for config in Config.search([('axiom_draft_receipt_design_id', '!=', False)]):
        xml = config.axiom_draft_receipt_design_id.design_receipt or ''
        cr.execute(
            "UPDATE pos_config SET axiom_draft_design_receipt = %s WHERE id = %s",
            [xml, config.id],
        )
