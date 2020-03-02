# -*- coding: utf-8 -*-
from odoo import models,api,fields
import odoo.addons.decimal_precision as dp

class StockMove(models.Model):
    _inherit = 'stock.move'

    weight_net = fields.Float(compute='_cal_move_weight', string='Net weight', digits_compute=dp.get_precision('Stock Weight'))
    
    @api.depends('product_id', 'product_uom_qty', 'product_uom')
    def _cal_move_weight(self):
        for move in self.filtered(lambda moves: moves.product_id.weight > 0.00):
            move.weight = (move.product_qty * move.product_id.weight)
            if move.product_id.weight_net > 0.00:
                move.weight_net = (move.product_qty * move.product_id.weight_net)

    # Viki Ept Note:
    # Taking valuation price from sale.order.line instead of the product's standard price
    def attribute_price(self,cr, uid, move, context=None):
        """
            Attribute price to move, important in inter-company moves or receipts with only one partner
        """
        if not move.price_unit:
            price = move.procurement_id.sale_line_id and move.procurement_id.sale_line_id.price_unit or 0.0
            self.write(cr, uid,[move.id], {'price_unit': price})
            
    @api.multi
    def action_cancel(self):
        """
        By Viki:
        TODO :Need to check the code of base Sasmar modules.
        Quant qty change.
        Cancel Stock move.
        Deleting account move and account move line from invoice.  
        """
        res = super(StockMove,self).action_cancel()
        return res