from odoo import fields, models

class stock_shipwire_items(models.Model):
    _name = 'stock.shipwire.items'

    name = fields.Char('Shipwire Item Id')
    product_id = fields.Many2one('product.product', string='SKU')
    quantity = fields.Char('Quantity')
    ordered = fields.Char('ordered')
    backordered = fields.Char('Backordered')
    reserved = fields.Char('Reserved')
    shipped = fields.Char('Shipped')
    shipping = fields.Char('shipping')
    picking_id = fields.Many2one('stock.picking', string='Picking')
