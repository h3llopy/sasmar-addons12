# -*- coding: utf-8 -*-
{
    'name': 'Project Extension Ept',
    'version': '1.0',
    'summary' : 'Project Extension',
    'description': """
        Recreation of all the modules from old one.

    """,
    'author': 'Emipro Technologies Pvt. Ltd.',
    'website': 'http://www.emiprotechnologies.com/',
    'maintainer': 'Emipro Technologies Pvt. Ltd.',
#     'depends': ['base_sasmar','custom_bi_project_subtask'],    
    'depends': ['base_sasmar'],
    'data': [
            'views/project_task_view_ept.xml',
            ],    
    'installable': True,
    'auto_install': False,
    'application' : True,
}
