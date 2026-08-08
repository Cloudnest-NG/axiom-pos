# -*- coding: utf-8 -*-
from odoo import _, api, fields, models

AXIOM_POS_CONFIG_FIELDS = (
    'axiom_theme_bg_color',
    'axiom_theme_text_color',
    'axiom_price_bg_color',
    'axiom_price_text_color',
    'axiom_price_alignment',
    'axiom_price_font_size',
    'axiom_paid_reprint_access',
    'axiom_product_info_access',
    'axiom_draft_receipt_design_id',
)


class PosConfig(models.Model):
    _inherit = 'pos.config'

    axiom_theme_bg_color = fields.Char(
        string='POS Theme Background',
        default='#F0EEEE',
        help='Background color for the POS screen theme.',
    )
    axiom_theme_text_color = fields.Char(
        string='POS Theme Text',
        default='#374151',
        help='Default text color for the POS screen theme.',
    )
    axiom_price_bg_color = fields.Char(
        string='Product Price Background',
        default='#000000',
        help='Background color of the price badge on product cards (shown at 60% opacity).',
    )
    axiom_price_text_color = fields.Char(
        string='Product Price Text',
        default='#FFFFFF',
        help='Text color of the price badge on product cards.',
    )
    axiom_price_alignment = fields.Selection(
        selection=[
            ('top_left', 'Top Left'),
            ('top_center', 'Top Center'),
            ('top_right', 'Top Right'),
            ('middle_left', 'Middle Left'),
            ('middle', 'Middle'),
            ('middle_right', 'Middle Right'),
            ('bottom_left', 'Bottom Left'),
            ('bottom_center', 'Bottom Center'),
            ('bottom_right', 'Bottom Right'),
        ],
        string='Product Price Alignment',
        default='top_right',
        required=True,
        help='Position of the price badge on product cards.',
    )
    axiom_price_font_size = fields.Char(
        string='Product Price Font Size',
        default='20px',
        help='Font size of the price badge on product cards (e.g. 20px).',
    )
    axiom_paid_reprint_access = fields.Selection(
        selection=[
            ('all', 'Everyone'),
            ('admin', 'POS Administrators'),
            ('none', 'No one'),
        ],
        string='Paid Order Reprinting',
        default='admin',
        required=True,
        help='Who can reprint paid receipts. "No one" disables reprint for all cashiers.',
    )
    axiom_product_info_access = fields.Selection(
        selection=[
            ('all', 'Everyone'),
            ('admin', 'POS Administrators'),
            ('none', 'No one'),
        ],
        string='Product Info / On Hand',
        default='admin',
        required=True,
        help='Who can open the product info card and see on-hand quantity in the POS. '
             '"Everyone" includes basic cashiers / employees.',
    )
    axiom_draft_receipt_design_id = fields.Many2one(
        'pos.receipt',
        string='Draft Receipt Design',
        help='XML receipt design used when printing draft / pro forma bills.',
    )
    axiom_draft_design_receipt = fields.Text(
        related='axiom_draft_receipt_design_id.design_receipt',
        string='Draft Receipt XML',
        store=True,
        readonly=True,
    )
    axiom_apply_to_all_pos = fields.Boolean(
        string='Apply Axiom Settings to All POS',
        default=False,
        help='When enabled and you save, copy all Axiom POS settings from this '
             'config (theme, price badge, draft receipt, locks) to every other '
             'Point of Sale in the same company. The checkbox resets after save.',
    )

    def _axiom_get_config_vals(self):
        self.ensure_one()
        return {name: self[name] for name in AXIOM_POS_CONFIG_FIELDS}

    def action_axiom_apply_to_all_company_pos(self):
        """Copy Axiom POS settings from this config to all other company POS."""
        for config in self:
            others = self.search([
                ('company_id', '=', config.company_id.id),
                ('id', '!=', config.id),
            ])
            if others:
                others.with_context(axiom_skip_apply_to_all=True).write(
                    config._axiom_get_config_vals()
                )
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Axiom POS'),
                'message': _(
                    'Axiom settings were applied to all other Points of Sale '
                    'in this company.'
                ),
                'type': 'success',
                'sticky': False,
            },
        }

    def write(self, vals):
        if self.env.context.get('axiom_skip_apply_to_all'):
            return super().write(vals)
        # Required selections must never be cleared (UI can send False).
        if 'axiom_product_info_access' in vals and not vals.get('axiom_product_info_access'):
            vals['axiom_product_info_access'] = 'admin'
        if 'axiom_paid_reprint_access' in vals and not vals.get('axiom_paid_reprint_access'):
            vals['axiom_paid_reprint_access'] = 'admin'
        apply_all = bool(vals.get('axiom_apply_to_all_pos'))
        res = super().write(vals)
        if apply_all:
            for config in self:
                others = self.search([
                    ('company_id', '=', config.company_id.id),
                    ('id', '!=', config.id),
                ])
                if others:
                    others.with_context(axiom_skip_apply_to_all=True).write(
                        config._axiom_get_config_vals()
                    )
            self.with_context(axiom_skip_apply_to_all=True).write({
                'axiom_apply_to_all_pos': False,
            })
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('axiom_product_info_access'):
                vals['axiom_product_info_access'] = 'admin'
            if not vals.get('axiom_paid_reprint_access'):
                vals['axiom_paid_reprint_access'] = 'admin'
        return super().create(vals_list)

    @api.model
    def _load_pos_data_fields(self, config_id):
        """Ensure Axiom theme / receipt fields are always sent to the POS UI."""
        fields_list = super()._load_pos_data_fields(config_id) or []
        if not fields_list:
            return fields_list
        for name in AXIOM_POS_CONFIG_FIELDS + ('axiom_draft_design_receipt',):
            if name not in fields_list:
                fields_list.append(name)
        return fields_list
