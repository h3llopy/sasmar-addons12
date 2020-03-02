# -*- coding: utf-8 -*-
{
    'name': 'Product Extension Ept',
    'version': '1.0',
    'summary' : 'Product Extension',
    'description': """
        Recreation of all the modules from old one.

    """,
    'author': 'Emipro Technologies Pvt. Ltd.',
    'website': 'http://www.emiprotechnologies.com/',
    'maintainer': 'Emipro Technologies Pvt. Ltd.',
#     'depends': ['base_sasmar','sasmar_user_preference'],
    'depends': ['base_sasmar','delivery_shipwire'],       
    'data': [
             'views/product_template_view_ept.xml',
             'views/product_product_view_ept.xml',
            ],    
    'installable': True,
    'auto_install': False,
    'application' : True,
}
