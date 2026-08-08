# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_axiom_theme_bg_color = fields.Char(
        related='pos_config_id.axiom_theme_bg_color',
        readonly=False,
    )
    pos_axiom_theme_text_color = fields.Char(
        related='pos_config_id.axiom_theme_text_color',
        readonly=False,
    )
    pos_axiom_price_bg_color = fields.Char(
        related='pos_config_id.axiom_price_bg_color',
        readonly=False,
    )
    pos_axiom_price_text_color = fields.Char(
        related='pos_config_id.axiom_price_text_color',
        readonly=False,
    )
    pos_axiom_price_alignment = fields.Selection(
        related='pos_config_id.axiom_price_alignment',
        readonly=False,
    )
    pos_axiom_price_font_size = fields.Char(
        related='pos_config_id.axiom_price_font_size',
        readonly=False,
    )
    pos_axiom_paid_reprint_access = fields.Selection(
        related='pos_config_id.axiom_paid_reprint_access',
        readonly=False,
    )
    pos_axiom_product_info_access = fields.Selection(
        related='pos_config_id.axiom_product_info_access',
        readonly=False,
    )
    pos_axiom_draft_receipt_design_id = fields.Many2one(
        related='pos_config_id.axiom_draft_receipt_design_id',
        readonly=False,
    )
    pos_axiom_apply_to_all_pos = fields.Boolean(
        related='pos_config_id.axiom_apply_to_all_pos',
        readonly=False,
    )

    def action_axiom_apply_to_all_company_pos(self):
        self.ensure_one()
        if not self.pos_config_id:
            return False
        return self.pos_config_id.action_axiom_apply_to_all_company_pos()
