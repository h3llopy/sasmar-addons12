# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "Shipwire Shipping",
    'description': "Send your shippings through Shiwire and track their status online",
    'author': "BrowseInfo",
    'website': "https://www.brwoseinfo.com",
    'category': 'Technical Settings',
    'version': '1.0',
    'depends': ['delivery', 'mail','custom_stock_shipwire'],
    'data': [
        'security/ir.model.access.csv',
        'data/delivery_shipwire_schedulars_data.xml',
        'data/delivery_shipwire_data.xml',
        'data/shipwire_data.xml',
        'views/delivery_shipwire_view.xml',
        'views/stock_picking_view.xml',
        'views/warehouse_view.xml',
    ],
}
