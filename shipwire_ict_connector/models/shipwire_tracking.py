from odoo import models,fields,api
   
class shipwire_stages(models.Model):
    
    _name="shipwire.tracking"
    
    name = fields.Char("Tracking Number")
    url = fields.Char("Url")
    picking_id = fields.Many2one('stock.picking',"Picking ID",required=True,copy=False)
    shipwire_id = fields.Integer("Shipwire ID")

    