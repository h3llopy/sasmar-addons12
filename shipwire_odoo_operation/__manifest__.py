{
    'name': 'Shipwire Odoo Operations',
    'version': '1.0',
    'summary' : 'Shipwire Odoo Operations',
    'description': """
    

    """,
    'author': 'Emipro Technologies Pvt. Ltd.',
    'website': 'http://www.emiprotechnologies.com/',
    'maintainer': 'Emipro Technologies Pvt. Ltd.',
    'depends': ['base','product','sale','stock','account','shipwire_api_operation','website_sale','product'],    
    'data': [
            'views/stock_warehouse.xml',
            'views/odoo_shipwire_operation.xml',
            'views/sale_order.xml',
            #'views/website_region.xml',
            'views/process_log.xml',
            'views/product.xml',
            'security/shipwire_group.xml',
            'security/ir.model.access.csv',
            'wizard/shipwire_product_export_wizard.xml',
            'views/ir_sequence.xml',
            
            ],    
    'installable': True,
    'auto_install': False,
    'application' : True,
}
