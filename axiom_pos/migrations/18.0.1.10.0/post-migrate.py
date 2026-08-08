# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    from odoo.addons.axiom_pos.hooks import _axiom_fill_pos_config_defaults
    _axiom_fill_pos_config_defaults(env)
