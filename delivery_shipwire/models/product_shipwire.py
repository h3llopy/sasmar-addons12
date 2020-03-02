# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError,UserError
from odoo import tools


class ProductProduct(models.Model):
    _inherit = 'product.product'

    carrier_tracking_ref = fields.Char('Carrier Tracking Reference')
    
    
class stock_change_product_qty(models.TransientModel):
    _inherit = 'stock.change.product.qty'

    
    
    # def change_product_qty(self):
    #     """ Changes the Product Quantity by making a Physical Inventory. """
    #     if context is None:
    #         context = {}

    #     inventory_obj = self.pool.get('stock.inventory')
    #     inventory_line_obj = self.pool.get('stock.inventory.line')

    #     for data in self.browse(cr, uid, ids, context=context):
    #         if data.new_quantity < 0:
    #             raise UserError(_('Quantity cannot be negative.'))
    #         ctx = context.copy()
    #         ctx['location'] = data.location_id.id
    #         ctx['lot_id'] = data.lot_id.id
    #         if data.product_id.id and data.lot_id.id:
    #             filter = 'none'
    #         elif data.product_id.id:
    #             filter = 'product'
    #         else:
    #             filter = 'none'
    #         inventory_id = inventory_obj.create(cr, uid, {
    #             'name': _('INV: %s') % tools.ustr(data.product_id.name),
    #             'filter': filter,
    #             'product_id': data.product_id.id,
    #             'location_id': data.location_id.id,
    #             'company_id':data.location_id.company_id.id,
    #             'lot_id': data.lot_id.id}, context=context)
    #         product = data.product_id.with_context(location=data.location_id.id, lot_id= data.lot_id.id)
    #         th_qty = product.qty_available
    #         line_data = {
    #             'inventory_id': inventory_id,
    #             'product_qty': data.new_quantity,
    #             'location_id': data.location_id.id,
    #             'product_id': data.product_id.id,
    #             'product_uom_id': data.product_id.uom_id.id,
    #             'theoretical_qty': th_qty,
    #             'prod_lot_id': data.lot_id.id,
    #             'company_id':data.location_id.company_id.id,
    #         }
    #         inventory_line_obj.create(cr , uid, line_data, context=context)
    #         inventory_obj.action_done(cr, uid, [inventory_id], context=context)
    #     return {}