# -*- coding: utf-8 -*-
from . import models


def _axiom_fill_pos_config_defaults(env):
    """Fill missing Axiom defaults on existing POS configs so styling applies."""
    PosConfig = env['pos.config'].sudo()
    draft_design = env.ref(
        'axiom_pos.pos_receipt_draft_proforma', raise_if_not_found=False
    )
    for config in PosConfig.search([]):
        vals = {}
        if not config.axiom_theme_bg_color:
            vals['axiom_theme_bg_color'] = '#F0EEEE'
        if not config.axiom_theme_text_color:
            vals['axiom_theme_text_color'] = '#374151'
        if not config.axiom_price_bg_color:
            vals['axiom_price_bg_color'] = '#000000'
        if not config.axiom_price_text_color:
            vals['axiom_price_text_color'] = '#FFFFFF'
        if not config.axiom_price_alignment:
            vals['axiom_price_alignment'] = 'top_right'
        if not config.axiom_price_font_size:
            vals['axiom_price_font_size'] = '20px'
        if not config.axiom_product_info_access:
            vals['axiom_product_info_access'] = 'admin'
        if not config.axiom_paid_reprint_access:
            vals['axiom_paid_reprint_access'] = 'admin'
        if draft_design and not config.axiom_draft_receipt_design_id:
            vals['axiom_draft_receipt_design_id'] = draft_design.id
        if vals:
            config.write(vals)


def post_init_hook(env):
    _axiom_fill_pos_config_defaults(env)
