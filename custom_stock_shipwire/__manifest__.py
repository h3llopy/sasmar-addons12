# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "Stock Configuration Customization For Shipwire Shipping",
    'description': "Shipwire installation Option in Stock COnfiguration Screen",
    'author': "BrowseInfo",
    'website': "https://www.brwoseinfo.com",
    'category': 'Technical Settings',
    'version': '1.0',
    'depends': ['delivery', 'mail', 'stock'],
    'data': [
        'views/stock_config.xml'
    ],
    'auto_install' :True,
}
