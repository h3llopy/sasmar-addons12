{
    'name': 'Shipwire API Operations',
    'version': '1.0',
    'summary' : 'Shipwire Operations',
    'description': """
        Contains all resquest and response operation related to shipwire only.

    """,
    'author': 'Emipro Technologies Pvt. Ltd.',
    'website': 'http://www.emiprotechnologies.com/',
    'maintainer': 'Emipro Technologies Pvt. Ltd.',
    'depends': ['base','stock','sale'],    
    'data': [
        'security/ir.model.access.csv',
        'views/shipwire_instance.xml',
        'views/ir_cron.xml',
        'data/data_shipwire_instance.xml'
            ],    
    'installable': True,
    'auto_install': False,
    'application' : True,
}
