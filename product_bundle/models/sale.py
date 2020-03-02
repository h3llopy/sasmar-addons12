# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2014-Today BrowseInfo (<http://www.browseinfo.in>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
from odoo import api,  models, _
from odoo import fields
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo import SUPERUSER_ID



class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    @api.onchange('product_id', 'product_uom_qty')
    def _onchange_product_id_check_availability(self):
        res = super(SaleOrderLine, self)._onchange_product_id_check_availability()
        if self.product_id.is_pack:
            if self.product_id.type == 'product':
                warning_mess = {}
                for pack_product in self.product_id.pack_ids:
                    qty = self.product_uom_qty
                    if qty * pack_product.qty_uom > pack_product.product_id.virtual_available:
                        warning_mess = {
                                'title': _('Not enough inventory!'),
                                'message' : ('You plan to sell %s but you have only  %s quantities of the product %s available, and the total quantity to sell is  %s !!' % (qty, pack_product.product_id.virtual_available, pack_product.product_id.name, qty * pack_product.qty_uom))
                                }
                        return {'warning': warning_mess}
        else:
            return res

    
    @api.multi
    def _action_procurement_create(self):
        orders = list(set(x.order_id for x in self))
        res = super(SaleOrderLine, self)._action_procurement_create()
        new_procs = self.env['procurement.order'] #Empty recordset
        for line in self:
            vals = line._prepare_order_line_procurement(group_id=line.order_id.procurement_group_id.id)
            if line.product_id.is_pack:
                pack_product = vals
                for pack_id in line.product_id.pack_ids:
                    pack_product['product_id'] = pack_id.product_id.id
                    pack_product['product_qty'] = line.product_uom_qty * pack_id.qty_uom
                    pack_product['product_uom'] = pack_id.product_id.uom_id.id
                    pack_product['message_follower_ids'] = False
                    new_proc = self.env["procurement.order"].create(pack_product)
                    new_procs += new_proc
        for order in orders:
            reassign = order.picking_ids.filtered(lambda x: x.state=='confirmed' or ((x.state=='partially_available') and not x.printed))
        if reassign:
            reassign.do_unreserve()
            reassign.action_assign()
        new_procs.run()
        return new_procs

    
class stock_quant(models.Model):
    _inherit = 'stock.quant'
    
    def quants_reserve(self, cr, uid, quants, move, link=False, context=None):
        '''This function reserves quants for the given move (and optionally given link). If the total of quantity reserved is enough, the move's state
        is also set to 'assigned'

        :param quants: list of tuple(quant browse record or None, qty to reserve). If None is given as first tuple element, the item will be ignored. Negative quants should not be received as argument
        :param move: browse record
        :param link: browse record (stock.move.operation.link)'''
        
        toreserve = []
        reserved_availability = move.reserved_availability
        #split quants if needed
        for quant, qty in quants:
            if qty <= 0.0 or (quant and quant.qty <= 0.0):
                raise UserError(_('You can not reserve a negative quantity or a negative quant.'))
            if not quant:
                continue
            self._quant_split(cr, uid, quant, qty, context=context)
            toreserve.append(quant.id)
            reserved_availability += quant.qty
        #reserve quants
        if toreserve:
            self.write(cr, SUPERUSER_ID, toreserve, {'reservation_id': move.id}, context=context)
        #check if move'state needs to be set as 'assigned'
        rounding = move.product_id.uom_id.rounding
        if move.product_id.product_tmpl_id.is_pack:
            quantity = []
            for pack_obj in move.product_id.product_tmpl_id.pack_ids:
                product_obj = self.pool.get('product.product')
                product_search =product_obj.search(cr, uid,[('id' ,'=', pack_obj.product_id.id)])
                if product_search:
                    product_qty = product_obj.browse(cr, uid,product_search[0] ).qty_available
                    if product_qty <= 0.0:
                        quantity.append(product_qty)
            if quantity:
                self.pool.get('stock.move').write(cr, uid, [move.id], {'state': 'confirmed'}, context=context)
            else:
                self.pool.get('stock.move').write(cr, uid, [move.id], {'state': 'assigned'}, context=context)
        elif float_compare(reserved_availability, move.product_qty, precision_rounding=rounding) == 0 and move.state in ('confirmed', 'waiting')  :
            self.pool.get('stock.move').write(cr, uid, [move.id], {'state': 'assigned'}, context=context)
        elif float_compare(reserved_availability, 0, precision_rounding=rounding) > 0 and not move.partially_available:
            self.pool.get('stock.move').write(cr, uid, [move.id], {'partially_available': True}, context=context)
    
