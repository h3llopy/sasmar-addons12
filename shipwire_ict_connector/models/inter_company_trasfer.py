from odoo import models,fields,api, _

class stockPicking(models.Model):

    _inherit = "inter.company.transfer.ept"

    is_auto_ict = fields.Boolean("Is auto ICT ?",defalt=False,copy=False)
    

    @api.multi
    def get_related_moves(self):
        move_ids = []   
        for line in self.line_ids:
            move_ids = move_ids + line.stock_move_ids
        return move_ids

    @api.multi
    def get_related_pickings(self):
        
        picking_ids = []
        move_ids = self.get_related_moves()
        move_ids = self.env['stock.move'].browse(move_ids)
        for move in move_ids:
            picking_ids.append(move.picking_id)
        return picking_ids

    @api.multi
    def get_related_sale_orders(self):
        sale_order_ids = []
        picking_ids = self.get_related_pickings()
        picking_ids = self.env['stock.picking'].browse(picking_ids)
        for picking in picking_ids:
            sale_order_ids.append(picking.sale_id)
        return sale_order_ids


