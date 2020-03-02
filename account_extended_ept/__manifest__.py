# -*- coding: utf-8 -*-
{
    'name': 'Account Extension Ept',
    'version': '1.0',
    'summary' : 'Account Extension',
    'description': """
        Recreation of all the modules from old one.

    """,
    'author': 'Emipro Technologies Pvt. Ltd.',
    'website': 'http://www.emiprotechnologies.com/',
    'maintainer': 'Emipro Technologies Pvt. Ltd.',
#     'depends': ['base_sasmar','custom_journal','invoice_open','sasmar_user_preference'],    
    'depends': ['base_sasmar'],
    'data': [
             'views/account_bank_statement_view_ept.xml',
             'views/res_partner_bank_view_ept.xml',
             'views/account_journal_view.xml',
             'views/account_voucher_view.xml',
             'views/res_company.xml'
            ],    
    'installable': True,
    'auto_install': False,
    'application' : True,
}
