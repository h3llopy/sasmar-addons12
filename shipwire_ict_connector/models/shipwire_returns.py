from odoo import fields, models

class stock_shipwire_returns(models.Model):
    _name = 'stock.shipwire.returns'

    name = fields.Char('Shipwire Return Id')
    transactionid = fields.Char('Shipwire Return transactionId')
    status = fields.Char('Return Status')
    picking_id = fields.Many2one('stock.picking', string='Picking')
