# -*- coding: utf-8 -*-
{
    'name': 'HR Extension Ept',
    'version': '1.0',
    'summary' : 'HR Extension Ept',
    'description': """
        Recreation of all the modules from old one.

    """,
    'author': 'Emipro Technologies Pvt. Ltd.',
    'website': 'http://www.emiprotechnologies.com/',
    'maintainer': 'Emipro Technologies Pvt. Ltd.',
#     'depends': ['base_sasmar','custom_contract'],    
    'depends': ['base_sasmar'],    
    'data': [
            'views/contract_view.xml',
            ],    
    'installable': True,
    'auto_install': False,
    'application' : True,
}
