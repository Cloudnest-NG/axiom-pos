# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    axiom_show_product_price = fields.Boolean(
        compute='_compute_axiom_pos_rights',
        string='POS Show Product Prices',
    )
    axiom_enable_draft_printing = fields.Boolean(
        compute='_compute_axiom_pos_rights',
        string='POS Enable Draft Printing',
    )
    axiom_can_reprint_paid = fields.Boolean(
        compute='_compute_axiom_pos_rights',
        string='POS Can Reprint Paid Orders',
    )
    axiom_can_view_product_info = fields.Boolean(
        compute='_compute_axiom_pos_rights',
        string='POS Can View Product Info / On Hand',
    )

    @api.depends('user_id.groups_id')
    def _compute_axiom_pos_rights(self):
        show_price_group = self.env.ref(
            'axiom_pos.group_show_product_price', raise_if_not_found=False
        )
        draft_print_group = self.env.ref(
            'axiom_pos.group_enable_draft_printing', raise_if_not_found=False
        )
        reprint_paid_group = self.env.ref(
            'axiom_pos.group_reprint_paid_orders', raise_if_not_found=False
        )
        product_info_group = self.env.ref(
            'axiom_pos.group_view_product_info', raise_if_not_found=False
        )
        for employee in self:
            groups = employee.user_id.groups_id if employee.user_id else self.env['res.groups']
            employee.axiom_show_product_price = bool(
                show_price_group and show_price_group in groups
            )
            employee.axiom_enable_draft_printing = bool(
                draft_print_group and draft_print_group in groups
            )
            employee.axiom_can_reprint_paid = bool(
                reprint_paid_group and reprint_paid_group in groups
            )
            employee.axiom_can_view_product_info = bool(
                product_info_group and product_info_group in groups
            )

    @api.model
    def _load_pos_data_fields(self, config_id):
        fields_list = super()._load_pos_data_fields(config_id) or []
        for name in (
            'axiom_show_product_price',
            'axiom_enable_draft_printing',
            'axiom_can_reprint_paid',
            'axiom_can_view_product_info',
        ):
            if name not in fields_list:
                fields_list.append(name)
        return fields_list
