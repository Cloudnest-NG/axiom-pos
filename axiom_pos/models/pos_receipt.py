# -*- coding: utf-8 -*-
from odoo import api, models


class PosReceipt(models.Model):
    _name = 'pos.receipt'
    _inherit = ['pos.receipt', 'pos.load.mixin']

    @api.model
    def _load_pos_data_domain(self, data):
        return []

    @api.model
    def _load_pos_data_fields(self, config_id):
        return ['id', 'name', 'design_receipt']


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _load_pos_data_models(self, config_id):
        models = super()._load_pos_data_models(config_id)
        if 'pos.receipt' not in models:
            models.append('pos.receipt')
        return models
