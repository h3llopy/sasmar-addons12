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
import math
from odoo import models
import time
from odoo import api, fields, models, _
from odoo.tools.translate import _
import odoo.addons.decimal_precision as dp
from datetime import datetime, timedelta, date

class product_template(models.Model):
    _inherit = "product.template"

    weight_net = fields.Float('Net Weight', digits_compute=dp.get_precision('Stock Weight'), help="The net weight in Kg.")

class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.depends('product_id', 'product_uom_qty', 'product_uom')
    def _cal_move_weight(self):
        res = {}
        for move in self.browse():
            weight = weight_net = 0.00
            if move.product_id.weight > 0.00:
                converted_qty = move.product_qty
                weight = (converted_qty * move.product_id.weight)

                if move.product_id.weight_net > 0.00:
                    weight_net = (converted_qty * move.product_id.weight_net)

            res[move.id] = {
                            'weight': weight,
                            'weight_net': weight_net,
                            }
        return res

    weight_net = fields.Float(compute=_cal_move_weight, type='float', string='Net weight', digits_compute=dp.get_precision('Stock Weight'), multi='_cal_move_weight')

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def create_lots_for_picking(self, cr, uid, ids, context=None):
        lot_obj = self.pool['stock.production.lot']
        opslot_obj = self.pool['stock.production.lot']
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
    
    def _get_picking_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('stock.move').browse(cr, uid, ids, context=context):
            result[line.picking_id.id] = True
        return result.keys()

    weight_net = fields.Float(compute=_cal_weight, type='float', string='Net Weight', digits_compute=dp.get_precision('Stock Weight'), multi='_cal_weight')


class res_company(models.Model):
    _inherit = "res.company"

    bank_ids = fields.One2many('res.partner.bank', 'company_id', 'Bank Accounts', help='Bank accounts related to this company')


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'
    
    
    @api.multi
    def unlink(self):
        for line in self:
            if line.statement_id !=  False:
                line.statement_id = False
                return True
            else:
                return super(AccountMoveLine, self).unlink()

    
  
        

      
class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"
    
    move_line_ids = fields.One2many('account.move.line', 'statement_id', string='Entry lines')
    account_id = fields.Many2one('account.account', related='journal_id.default_debit_account_id', type='many2one', string='Account', readonly=True, help='used in statement reconciliation domain, but shouldn\'t be used elswhere.')


    
	
    @api.one
    @api.depends('line_ids', 'balance_start', 'line_ids.amount', 'balance_end_real','move_line_ids')
    def _end_balance(self):
        res_users_obj = self.env['res.users']
        company_currency_id = self.env.user.company_id.currency_id
        statement_balance_start = self.balance_start
        for line in self.move_line_ids:
            if line.debit > 0:
                if line.account_id.id == \
                        self.journal_id.default_debit_account_id.id:
                    statement_balance_start += line.amount_currency or line.debit
            else:
                if line.account_id.id == \
                        self.journal_id.default_credit_account_id.id:
                    statement_balance_start += line.amount_currency or (-line.credit)
        self.balance_end = statement_balance_start
        if self.state in ('open'):
            for line in self.line_ids:
                statement_balance_start += line.amount
                self.balance_end = statement_balance_start
        
        
class account_tax(models.Model):
 
    _inherit = 'account.tax'
    
    def name_get(self):
        if not self.ids:
            return []
        res = []
        for record in self.read(['description','name']):
            name = record['description'] and record['description'] or record['name']
            res.append((record['id'],name ))
        return res
        
        	
class res_partner_bank(models.Model):
    _inherit = "res.partner.bank"

    company_id = fields.Many2one('res.company', 'Company Bank Account')
    footer = fields.Boolean('Display on Report')
    bank_name = fields.Char('Bank Name', required=True)
    bank_bic = fields.Char('Bank Identifier Code')
    bank_name_t = fields.Char('Bank Name', required=True)
    
    
    @api.onchange('bank_id')
    def onchange_bank_id(self):
        if self.bank_id:
            bank = self.env['res.bank'].browse(self.bank_id.id)
            if bank.name:
                self.bank_name = bank.name
                self.bank_bic = bank.bic


class stock_pack_operation_lot(models.Model):
    _inherit = "stock.production.lot"
    
    expiry_date =  fields.Date('Expiry Date')
    
    
class purchase_order(models.Model):
    _inherit = 'purchase.order'
    
    customer_address_id = fields.Many2one('res.partner', 'Customer Address')
    dest_address_id = fields.Many2one('res.partner', 'Delivery Address')
    bid_date = fields.Date('Bid Received On', readonly = True)
    bid_validity = fields.Date('Bid Valid Until')
    validator = fields.Many2one('res.users', 'Validated By')
    expected_date = fields.Date('Expected Date')

class account_account(models.Model):
    
    _inherit = 'account.account'
    
    old_account_code = fields.Char('old code')    
    

class crm_team(models.Model):
    _inherit = 'crm.team'
    
    parent_id = fields.Many2one('crm.team', 'Parent Team')


class stock_inventory(models.Model):
    _inherit = 'stock.inventory'
    
    inventory_date = fields.Datetime('Inventory Date')
    
    
class res_partner(models.Model):
    _inherit = "res.partner"
    
    sequence = fields.Char('Number', compute = 'sequnce_fucn',readonly = 'True')
       
    @api.one
    def sequnce_fucn(self):
        if len(str(self.id)) > 0:
            sequence = {1: '00000', 2: '0000', 3: '000', 4: '00',5:'0'}
            seq = sequence.get(len(str(self.id)), '') + str(self.id)
            self.sequence =  seq
            
class StockLot(models.Model):
    _inherit = "stock.production.lot"
    
    expiry_date =  fields.Date('Expiry Date')
    

class project_task(models.Model):
    _inherit = "project.task"
    
    description = fields.Text('Description')

class sale_order(models.Model):
    _inherit = 'sale.order'
        
    x_manually_done = fields.Boolean(string = 'Manually Done')
    confirm_date = fields.Date(string = 'Confirm  Date' , readonly=True)
    doc= fields.Boolean('Transfer Document')
    
    
            
class sale_order_line(models.Model):
    _inherit = 'sale.order.line'
    
    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)], change_default=True, ondelete='restrict', required=False)

    
    
class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'
    
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)], change_default=True , required = False)
    
    
class hr_expense(models.Model):
    _inherit  = 'hr.expense'
    
    product_id = fields.Many2one('product.product', string='Product', readonly=True, states={'draft': [('readonly', False)]}, domain=[('can_be_expensed', '=', True)], required=False)        
    ref = fields.Char('Description')
    
# class stock_pack_operation(models.Model):
#     _inherit = "stock.pack.operation"
    
#     def split_lot(self, cr, uid, ids, context=None):
#         context = context or {}
#         ctx=context.copy()
#         assert len(ids) > 0
#         data_obj = self.pool['ir.model.data']
#         pack = self.browse(cr, uid, ids[0], context=context)
#         picking_type = pack.picking_id.picking_type_id
#         serial = (pack.product_id.tracking == 'serial')
#         view = data_obj.xmlid_to_res_id(cr, uid, 'stock.view_pack_operation_lot_form')
#         only_create = picking_type.use_create_lots and not picking_type.use_existing_lots
#         show_reserved = any([x for x in pack.pack_lot_ids if x.qty_todo > 0.0])
#         search_picking = self.pool.get('stock.picking.type').browse(cr, uid, picking_type.id, context=context)
#         if search_picking.name == 'Delivery Orders' or  search_picking.name ==   'Internal Transfers':
#             ctx.update({'picking_type': search_picking.name})
#         ctx.update({'serial': serial,
#                     'only_create': only_create,
#                     'create_lots': picking_type.use_create_lots,
#                     'state_done': pack.picking_id.state == 'done',
#                     'show_reserved': show_reserved})
#         return {
#              'name': _('Lot Details'),
#              'type': 'ir.actions.act_window',
#              'view_type': 'form',
#              'view_mode': 'form',
#              'res_model': 'stock.pack.operation',
#              'views': [(view, 'form')],
#              'view_id': view,
#              'target': 'new',
#              'res_id': pack.id,
#              'context': ctx,
#         }

