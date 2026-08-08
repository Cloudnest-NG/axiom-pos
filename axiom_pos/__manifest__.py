# -*- coding: utf-8 -*-
################################################################################
#
#    Axiom Cloudnest Ltd
#
#    Copyright (C) 2026-TODAY Axiom Cloudnest Ltd.
#    Author: Axiom Cloudnest Ltd
#
################################################################################
{
    'name': 'Axiom POS Access Rights',
    'version': '18.0.1.16.0',
    'category': 'Sales/Point of Sale',
    'summary': 'POS access rights, theme layout, draft receipts, reprint rules & print shortcuts for Odoo 18',
    'description': """
Axiom POS Access Rights
=======================

Granular Point of Sale permissions and layout options by Axiom Cloudnest Ltd:

* Show / hide product prices on cards and order lines
* Draft / pro forma printing for POS HR advanced employees
* Paid reprint access: Everyone, POS Administrators, or No one
* Product info / on hand: Everyone, Administrators, or No one
* POS screen theme (body + thicker header from two colors)
* Product card price badge styling (color, alignment, size)
* Draft receipt XML design selection
* Print icons in POS header and ticket list
* Apply Axiom settings to all POS configs in the company

Website: https://www.cloudnest.com.ng
Support: support@cloudnest.com.ng
    """,
    'author': 'Axiom Cloudnest Ltd',
    'company': 'Axiom Cloudnest Ltd',
    'maintainer': 'Axiom Cloudnest Ltd',
    'website': 'https://www.cloudnest.com.ng',
    'support': 'support@cloudnest.com.ng',
    'license': 'LGPL-3',
    # pos_hr: cashier is hr.employee; rights must be loaded on employees.
    # odoo-pos-custom-branding: provides pos.receipt XML designs for draft select.
    'depends': ['point_of_sale', 'pos_hr', 'odoo-pos-custom-branding'],
    'data': [
        'security/axiom_pos_security.xml',
        'data/pos_receipt_draft_data.xml',
        'views/res_config_settings_views.xml',
    ],
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/cloudnest_logo.png',
    ],
    'post_init_hook': 'post_init_hook',
    'assets': {
        'point_of_sale._assets_pos': [
            'axiom_pos/static/src/app/store/pos_store.js',
            'axiom_pos/static/src/app/pos_app.js',
            'axiom_pos/static/src/app/models/pos_order_line.js',
            'axiom_pos/static/src/app/generic_components/product_card/product_card.js',
            'axiom_pos/static/src/app/navbar/navbar.js',
            'axiom_pos/static/src/app/screens/product_screen/product_screen.js',
            'axiom_pos/static/src/app/screens/product_screen/control_buttons/control_buttons.js',
            'axiom_pos/static/src/app/screens/ticket_screen/ticket_screen.js',
            'axiom_pos/static/src/app/screens/receipt_screen/receipt_screen.js',
            'axiom_pos/static/src/app/screens/receipt_screen/receipt/order_receipt.js',
            'axiom_pos/static/src/app/generic_components/product_card/product_card.xml',
            'axiom_pos/static/src/app/navbar/navbar.xml',
            'axiom_pos/static/src/app/screens/product_screen/product_screen.xml',
            'axiom_pos/static/src/app/screens/product_screen/product_info_popup/product_info_popup.xml',
            'axiom_pos/static/src/app/components/product_info_banner/product_info_banner.xml',
            'axiom_pos/static/src/app/screens/product_screen/control_buttons/control_buttons.xml',
            'axiom_pos/static/src/app/screens/ticket_screen/ticket_screen.xml',
            'axiom_pos/static/src/app/screens/receipt_screen/receipt_screen.xml',
            'axiom_pos/static/src/app/screens/receipt_screen/receipt/order_receipt.xml',
            'axiom_pos/static/src/app/axiom_pos_theme.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
