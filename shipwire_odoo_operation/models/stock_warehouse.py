from openerp import fields, models,api

class stock_warehouse(models.Model):

    _inherit = "stock.warehouse"
    
    
    warehouse_shipwire = fields.Boolean("Shipwire")
    shipwire_warehouse_id = fields.Integer("Shipwire Warehouse ID")
    inventory_adjust = fields.Boolean("Adjust Inventory")
    damage_inventory = fields.Boolean("Damage Inventory")
    inventory_auto_start = fields.Boolean("Auto Start")
    inventory_auto_validate = fields.Boolean("Auto Validate")
    active = fields.Boolean("Active",default=True)
    shipwire_damage_location = fields.Many2one('stock.location',string="Damaged Location")