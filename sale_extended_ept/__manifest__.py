# -*- coding: utf-8 -*-
{
    'name': 'Sales Extension Ept',
    'version': '1.0',
    'summary' : 'Sales Extension',
    'description': """
        Recreation of all the modules from old one.

    """,
    'author': 'Emipro Technologies Pvt. Ltd.',
    'website': 'http://www.emiprotechnologies.com/',
    'maintainer': 'Emipro Technologies Pvt. Ltd.',
#     'depends': ['base_sasmar','sasmar_user_preference','bi_email_reply_fix','bi_sasmar_send_mail','transfer_document'],    
    'depends': ['base_sasmar'],
    'data': [
             'views/res_config_view.xml',
             'data/rule.xml',
             'data/ir_crons_ept.xml',
             'data/mail_template_ept.xml',
             'views/crm_team_view_ept.xml',
             'views/res_company_view_ept.xml',
             'views/crm_lead_view_ept.xml',
             'views/res_partner_view_ept.xml',
#              'views/sale_order_view_ept.xml',
             #'views/base_config_setting.xml',
             #'views/account_voucher_view_ept.xml',
            ],    
    'installable': True,
    'auto_install': False,
    'application' : True,
}
