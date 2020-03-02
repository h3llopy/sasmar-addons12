from odoo import fields, models

class stock_shipwire_holds(models.Model):
    _name = 'stock.shipwire.holds'

    name = fields.Char('Shipwire Hold Id')
    description = fields.Char('Description')
    cleareddate = fields.Datetime('Hold Clearance Date')
    applieddate = fields.Datetime('Hold Applied Date')
    picking_id = fields.Many2one('stock.picking', string='Picking')
    hold_id  = fields.Char('Hold ID')
