# -*- coding: utf-8 -*-
from odoo import models,api,fields
import odoo.addons.decimal_precision as dp

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def action_cancel_draft(self):
        self.do_unreserve()
        self.move_lines.write({'state': 'draft'})
        message = "Picking '%s' has been set in draft state." % self.name
        self.message_post(message)
      
    # @api.multi
    # def do_print_picking(self):
    #     return self.env['report'].get_action(self,'stock_extended_ept.report_picking_1')
    
    def create_lots_for_picking(self, cr, uid, ids, context=None):
        lot_obj = self.pool['stock.production.lot']
        opslot_obj = self.pool['stock.pack.operation.lot']
        to_unlink = []
        for picking in self.browse(cr, uid, ids, context=context):
            for ops in picking.pack_operation_ids:
                for opslot in ops.pack_lot_ids:
                    if not opslot.lot_id:
                        lot_id = lot_obj.create(cr, uid, {'name': opslot.lot_name, 'product_id': ops.product_id.id,'expiry_date': opslot.expiry_date}, context=context)
                        opslot_obj.write(cr, uid, [opslot.id], {'lot_id':lot_id}, context=context)
                #Unlink pack operations where qty = 0
                to_unlink += [x.id for x in ops.pack_lot_ids if x.qty == 0.0]
        opslot_obj.unlink(cr, uid, to_unlink, context=context)
    
    @api.depends('product_id', 'move_lines')
    def _cal_weight(self):
        res = {}
        for picking in self.browse():
            total_weight = total_weight_net = 0.00

            for move in picking.move_lines:
                if move.state != 'cancel':
                    total_weight += move.weight
                    total_weight_net += move.weight_net

            res[picking.id] = {
                                'weight': total_weight,
                                'weight_net': total_weight_net,
                              }
        return res
    
    weight_net = fields.Float(compute=_cal_weight,string='Net Weight', digits_compute=dp.get_precision('Stock Weight'))