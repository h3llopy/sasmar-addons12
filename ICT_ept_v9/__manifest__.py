{
    'name': 'InterCompany Transaction',
    'version': '1.0',
    'summary' : 'ICT Implementation',
    'description': """
        Allow Transaction between two warehouses of different company.

    """,
    'author': 'Emipro Technologies Pvt. Ltd.',
    'website': 'http://www.emiprotechnologies.com/',
    'maintainer': 'Emipro Technologies Pvt. Ltd.',
    'depends': ['delivery','sale','purchase','stock','shipwire_odoo_operation'],    
    'data': [
            'data/ir_sequence.xml',
            'data/intercompany_config.xml',
            'views/intecompany_transaction.xml',
            'views/res_company.xml',
            'views/account_invoice.xml',
            'wizard/reverse_ict_wizard.xml',
            'security/ICT_security.xml',
            'security/ir.model.access.csv',
             ],    
    'installable': True,
    'auto_install': False,
    'application' : True,
}
