# -*- coding: utf-8 -*-
{
    'name': 'Purchase Extension Ept',
    'version': '1.0',
    'summary' : 'Purchase Extension',
    'description': """
        Recreation of all the modules from old one.

    """,
    'author': 'Emipro Technologies Pvt. Ltd.',
    'website': 'http://www.emiprotechnologies.com/',
    'maintainer': 'Emipro Technologies Pvt. Ltd.',
#     'depends': ['base_sasmar','consumable_purchase_report','sasmar_user_preference','send_email_finance'],    
    'depends': ['base_sasmar'],
    'data': [
             'data/mail_template_ept.xml',
             'views/purchase_order_view_ept.xml',
             'reports/consumable_voucher_report.xml',
            ],    
    'installable': True,
    'auto_install': False,
    'application' : True,
}
