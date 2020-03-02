from openerp import fields,models,api,_

class website_region(models.Model):
    _inherit = "website.region"
    
    shipwire_warehouse = fields.Many2one('stock.warehouse',string="Shipwire Warehouse")