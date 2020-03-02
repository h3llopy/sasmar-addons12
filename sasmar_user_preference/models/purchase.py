# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Browseinfo (http://browseinfo.in)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import api, fields, models, _,  SUPERUSER_ID
from odoo.tools.translate import _
from datetime import datetime
from dateutil.relativedelta import relativedelta


JOURNAL_TYPE_MAP = {
    ('outgoing', 'customer'): ['sale'],
    ('outgoing', 'supplier'): ['purchase_refund'],
    ('outgoing', 'transit'): ['sale', 'purchase_refund'],
    ('incoming', 'supplier'): ['purchase'],
    ('incoming', 'customer'): ['sale_refund'],
    ('incoming', 'transit'): ['purchase', 'sale_refund'],}
    

class purchase_order(models.Model):
    _inherit = 'purchase.order'
    
    @api.onchange('company_id')
    def onchange_company_id(self):
        if not self.company_id:
            return {}
        warehouse_obj = self.env['stock.warehouse']
        picking_type_obj = self.env['stock.picking.type']
        warehouse_id = warehouse_obj.search([('company_id', '=', self.company_id.id)])
        if not warehouse_id:
            return {}
        picking_type_id = picking_type_obj.search([('warehouse_id', '=', warehouse_id[0].id or False),('code','=','incoming')])
        if not picking_type_id: 
            return {}
        else: 
            picking_type_id = picking_type_id[0].id
        self.picking_type_id = picking_type_id
    
    @api.model
    def _prepare_picking(self):
        if not self.group_id:
            self.group_id = self.group_id.create({
                'name': self.name,
                'partner_id': self.partner_id.id
            })
        return {
            'picking_type_id': self.picking_type_id.id,
            'partner_id': self.partner_id.id,
            'date': self.date_order,
            'origin': self.name,
            'location_dest_id': self._get_destination_location(),
            'location_id': self.partner_id.property_stock_supplier.id,
            'company_id': self.company_id.id
        }
        
    @api.multi
    def _create_picking(self):
        for order in self:
            ctx = dict(self._context, lang=self.partner_id.lang)
            ctx['company_id'] = self.company_id.id
            if any([ptype in ['product', 'consu'] for ptype in order.order_line.mapped('product_id.type')]):
                res = order._prepare_picking()
                picking = self.env['stock.picking'].create(res)
                moves = order.order_line.filtered(lambda r: r.product_id.type in ['product', 'consu'])._create_stock_moves(picking)
                move_ids = moves._action_confirm()
                
                moves = self.env['stock.move'].browse(move_ids)

                move_ids._action_assign()
        return True     
    
    @api.multi
    def action_view_picking(self):
        '''
        This function returns an action that display existing picking orders of given purchase order ids.
        When only one found, show the picking immediately.
        '''
        action = self.env.ref('stock.action_picking_tree')
        result = action.read()[0]

        #override the context to get rid of the default filtering on picking type
        result['context'] = {}
        pick_ids = sum([order.picking_ids.ids for order in self], [])
        #choose the view_mode accordingly
        if len(pick_ids) > 1:
            result['domain'] = "[('id','in',[" + ','.join(map(str, pick_ids)) + "])]"
        elif len(pick_ids) == 1:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pick_ids and pick_ids[0] or False
        ctx = dict(self._context, lang=self.partner_id.lang)
        ctx['company_id'] = self.company_id.id
        return result
    
    @api.multi
    def action_view_invoice(self):
        '''This function returns an action that display existing vendor bills of given purchase order ids.
        When only one found, show the vendor bill immediately.'''
        action = self.env.ref('account.action_invoice_tree2')
        result = action.read()[0]

        #override the context to get rid of the default filtering
        result['context'] = {'type': 'in_invoice', 'default_purchase_id': self.id, 'default_company_id': self.company_id.id}

        journal_ids = self.env['account.journal'].search(
            [('type', '=', 'purchase'), ('company_id', '=', self.company_id.id)])
            # Use the same account journal than a previous invoice
        result['context']['default_journal_id'] = journal_ids[0].id
        #choose the view_mode accordingly
        if len(self.invoice_ids) != 1:
            result['domain'] = "[('id', 'in', " + str(self.invoice_ids.ids) + ")]"
        elif len(self.invoice_ids) == 1:
            res = self.env.ref('account.invoice_supplier_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = self.invoice_ids.id
        return result
    
class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if not self.product_id:
            return result

        # Reset date, price and quantity since _onchange_quantity will provide default values
        self.date_planned = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.price_unit = self.product_qty = 0.0
        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        result['domain'] = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}

        product_lang = self.product_id.with_context({
            'lang': self.partner_id.lang,
            'partner_id': self.partner_id.id,
        })
        self.name = product_lang.display_name
        if product_lang.description_purchase:
            self.name += '\n' + product_lang.description_purchase

        fpos = self.order_id.fiscal_position_id
        if self.env.uid == SUPERUSER_ID:
            company_id = self.order_id.company_id.id or self.company_id.id
            self.taxes_id = fpos.map_tax(self.product_id.supplier_taxes_id.filtered(lambda r: r.company_id.id == company_id))
        else:
            self.taxes_id = fpos.map_tax(self.product_id.supplier_taxes_id)

        self._suggest_quantity()
        self._onchange_quantity()

        return result
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
