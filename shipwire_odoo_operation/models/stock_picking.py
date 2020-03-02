from openerp import fields, models ,api

class sale_order(models.Model):

    _inherit = "stock.picking"
    
    shipwire_id = fields.Integer(string="Shipwire ID",copy=False)