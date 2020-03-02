# -*- coding: utf-8 -*-
from odoo import models,api,fields

class StockPackOperation(models.Model):
    _inherit = "stock.pack.operation"
    
    def split_lot(self, cr, uid, ids, context=None):
        context = context or {}
        ctx=context.copy()
        assert len(ids) > 0
        data_obj = self.pool['ir.model.data']
        pack = self.browse(cr, uid, ids[0], context=context)
        picking_type = pack.picking_id.picking_type_id
        serial = (pack.product_id.tracking == 'serial')
        view = data_obj.xmlid_to_res_id(cr, uid, 'stock.view_pack_operation_lot_form')
        """
        :Viki Removed below code which is commented.
        """
#         returned_move = pack.linked_move_operation_ids.mapped('move_id').mapped('origin_returned_move_id')
#         only_create = picking_type.use_create_lots and not picking_type.use_existing_lots and not returned_move
        only_create = picking_type.use_create_lots and not picking_type.use_existing_lots
        show_reserved = any([x for x in pack.pack_lot_ids if x.qty_todo > 0.0])
        search_picking = self.pool.get('stock.picking.type').browse(cr, uid, picking_type.id, context=context)
        if search_picking.name == 'Delivery Orders' or  search_picking.name ==   'Internal Transfers':
            ctx.update({'picking_type': search_picking.name})
        ctx.update({'serial': serial,
                    'only_create': only_create,
                    'create_lots': picking_type.use_create_lots,
                    'state_done': pack.picking_id.state == 'done',
                    'show_reserved': show_reserved})
        return {
             'name': 'Lot Details',
             'type': 'ir.actions.act_window',
             'view_type': 'form',
             'view_mode': 'form',
             'res_model': 'stock.pack.operation',
             'views': [(view, 'form')],
             'view_id': view,
             'target': 'new',
             'res_id': pack.id,
             'context': ctx,
        }
        
     