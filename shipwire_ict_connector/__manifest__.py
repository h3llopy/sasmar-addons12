{
    'name': 'Shipwire Shipment to ICT record',
    'version': '1.0',
    'summary' : 'Shipwire Shipment to ICT record',
    'description': """
        Create ICT record on status of shipwire order stages based on configuration.
    """,
    'author': 'Emipro Technologies Pvt. Ltd.',
    'website': 'http://www.emiprotechnologies.com/',
    'maintainer': 'Emipro Technologies Pvt. Ltd.',
    'depends': ['ICT_ept_v9','shipwire_odoo_operation'],    
    'data': [
            'data/ir_cron.xml',
            'views/stock_picking.xml',
            'data/shipwire_stages.xml',
            'data/ir_cron_shipwire_returns.xml',
            'views/ict_menus.xml',
            'views/shipwire_instance.xml',
            'views/sale_order.xml',
            'wizards/sale_order_transfer_ict.xml',
            'wizards/single_ict_invoice_wizard.xml',
            'security/ir.model.access.csv'
             ],    
    'installable': True,
    'auto_install': False,
    'application' : True,
}
