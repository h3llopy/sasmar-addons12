# -*- coding: utf-8 -*-
{
    'name': 'Stock Extension Ept',
    'version': '1.0',
    'summary' : 'Stock Extension',
    'description': """
        Recreation of all the modules from old one.

    """,
    'author': 'Emipro Technologies Pvt. Ltd.',
    'website': 'http://www.emiprotechnologies.com/',
    'maintainer': 'Emipro Technologies Pvt. Ltd.',
#     'depends': ['base_sasmar','custom_picking_report','custom_sasmar_supplier','sasmar_user_preference','stock_picking_cancel_extended'],   
    'depends': ['base_sasmar'],
    'data': [
            'security/picking_security.xml',
            'views/stock_production_lot_view_ept.xml',
            #'report/report_stockpicking.xml',
            'views/warehouse_view.xml',
            'views/stock_picking_view_ept.xml',
            'views/stock_history.xml',
            'views/stock_pack_operation_lot.xml',
            ],    
    'installable': True,
    'auto_install': False,
    'application' : True,
}
