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
from odoo import api, fields, models, _
from odoo.tools.translate import _
import odoo.addons.decimal_precision as dp
from dateutil.relativedelta import relativedelta
from datetime import datetime
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo import SUPERUSER_ID


class Sale(models.Model):
    _inherit = "sale.order"
    
    '''@api.model
    def default_get(self, fields):
        res = super(Sale, self).default_get(fields)
        if self._context.get('active_id'):
            active_id = self._context.get('active_id')
            crm_brw = self.env['crm.lead'].browse(active_id)
            warehouse_search = self.env['stock.warehouse'].search([('company_id','=',crm_brw.company_id.id)])
            if self._context.get('default_opportunity_id'):
                res['compnay_id'] = crm_brw.company_id.id
                res['warehouse_id'] = warehouse_search.id and warehouse_search[0].id or False
        return res'''
    

    @api.onchange('company_id')
    def onchange_company_id(self):
        if self.company_id:
            search_warehouse = self.env['stock.warehouse'].search([('company_id','=',self.company_id.id)])
            self.warehouse_id = search_warehouse and search_warehouse[0].id or False
            
    @api.multi
    def _create_invoice(self, order, so_line, amount):
        inv_obj = self.env['account.invoice']
        ir_property_obj = self.env['ir.property']

        account_id = False
        if self.product_id.id:
            account_id = self.product_id.property_account_income_id.id
        if not account_id:
            prop = ir_property_obj.get('property_account_income_categ_id', 'product.category')
            prop_id = prop and prop.id or False
            account_id = order.fiscal_position_id.map_account(prop_id)
        if not account_id:
            raise UserError(
                _('There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') % \
                    (self.product_id.name,))

        if self.amount <= 0.00:
            raise UserError(_('The value of the down payment amount must be positive.'))
        if self.advance_payment_method == 'percentage':
            amount = order.amount_untaxed * self.amount / 100
            name = _("Down payment of %s%%") % (self.amount,)
        else:
            amount = self.amount
            name = _('Down Payment')
        invoice = inv_obj.create({
            'name': order.client_order_ref or order.name,
            'origin': order.name,
            'type': 'out_invoice',
            'reference': False,
            'account_id': order.partner_id.property_account_receivable_id.id,
            'partner_id': order.partner_invoice_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'origin': order.name,
                'account_id': account_id,
                'price_unit': amount,
                'quantity': 1.0,
                'discount': 0.0,
                'uom_id': self.product_id.uom_id.id,
                'product_id': self.product_id.id,
                'sale_line_ids': [(6, 0, [so_line.id])],
                'invoice_line_tax_ids': [(6, 0, [x.id for x in self.product_id.taxes_id])],
                'account_analytic_id': order.project_id.id or False,
                'company_id': self.company_id.id,
            })],
            'currency_id': order.pricelist_id.currency_id.id,
            'payment_term_id': order.payment_term_id.id,
            'fiscal_position_id': order.fiscal_position_id.id or order.partner_id.property_account_position_id.id,
            'team_id': order.team_id.id,
        })
        invoice.compute_taxes()
        return invoice
    
    
    @api.multi
    def _prepare_invoice(self ):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        property_obj = self.env['ir.property']
        field_obj = self.env['ir.model.fields']
        self.ensure_one()
        journal_ids = self.env['account.journal'].search(
            [('type', '=', 'sale'), ('company_id', '=', self.company_id.id)])
        if not journal_ids:
            raise UserError(_('There is no Account for %s Company. You may have to set a chart of account from Accounting app, settings menu.') % \
                    (self.company_id.name,))
        field_ids = field_obj.search([('field_description', '=', 'Account Receivable')])
        if field_ids:
            for field in field_ids:
                property_id = property_obj.search([('fields_id', '=', field.id), ('company_id', '=', self.company_id.id)])
                if property_id:
                    acc_ref = property_obj.browse(property_id[0].id).value_reference
                    account_id = acc_ref and acc_ref.split(',') and acc_ref.split(',')[1]
                    account_id = int(account_id)
        else:
            raise UserError( _('There is no Account for %s Company. You may have to set a chart of account from Accounting app, settings menu.') % \
                                        (self.company_id.name,))
#        bank_account_id = False
#        if self.partner_id:
#            if self.partner_id.company_id:
#                company_obj = self.env['res.company'].browse(self.partner_id.company_id.id)
#                if company_obj.bank_ids:
#                    bank_account_id = company_obj.bank_ids[0].id
        invoice_vals = {
            'name': self.client_order_ref or '',
            'origin': self.name,
            'type': 'out_invoice',
            'reference': self.client_order_ref or self.name,
            'account_id': account_id ,
            'partner_id': self.partner_invoice_id.id,
            'journal_id': journal_ids[0].id,
            'currency_id': self.pricelist_id.currency_id.id,
            'comment': self.note,
            'payment_term_id': self.payment_term_id.id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            'company_id': self.company_id.id,
            'user_id': self.user_id and self.user_id.id,
            'team_id': self.team_id.id,
           # 'partner_bank_id': bank_account_id or False,
        }
        return invoice_vals
    
class sale_order_line(models.Model):
    _inherit = 'sale.order.line'
    
    @api.multi
    def _compute_tax_id(self):
        for line in self:
            fpos = line.order_id.fiscal_position_id or line.order_id.partner_id.property_account_position_id
            if fpos:
                # The superuser is used by website_sale in order to create a sale order. We need to make
                # sure we only select the taxes related to the company of the partner. This should only
                # apply if the partner is linked to a company.
                if self.env.uid == SUPERUSER_ID and line.order_id.company_id:
                    taxes = fpos.map_tax(line.product_id.taxes_id).filtered(lambda r: r.company_id == line.order_id.company_id)
                else:
                    taxes = fpos.map_tax(line.product_id.taxes_id).filtered(lambda r: r.company_id == line.order_id.company_id)
                line.tax_id = taxes
            else:
                line.tax_id = line.product_id.taxes_id.filtered(lambda r: r.company_id == line.order_id.company_id) if line.product_id.taxes_id else False
                
    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}

        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not (self.product_uom and (self.product_id.uom_id.category_id.id == self.product_uom.category_id.id)):
            vals['product_uom'] = self.product_id.uom_id

        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )

        name = product.name_get()[0][1]
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['name'] = name
        self._compute_tax_id()

        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price(product.price, product.taxes_id, self.tax_id)
        self.update(vals)
        return {'domain': domain}
    
    
    @api.multi
    def _prepare_invoice_line(self, qty ):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        """
        self.ensure_one()
        res = {}
        property_obj = self.env['ir.property']
        field_obj = self.env['ir.model.fields']
        if self.invoice_status != 'invoiced':
 #           if not account_id:
            if self.product_id:
                field_id = field_obj.search( [('field_description', '=', 'Income Account'), ('name', '=', 'property_account_income_categ_id')])
                if field_id and self._context:
                    property_id = property_obj.search([('fields_id', '=', field_id[0].id), ('company_id', '=', self.order_id.company_id.id)])
                else:
                    property_id = False
                if property_id:
                    acc_ref = property_obj.browse( property_id[0].id).value_reference
                    account_id = acc_ref and acc_ref.split(',') and acc_ref.split(',')[1]
                    account_id = int(account_id)
                else:
                    account_id = False
                    
                if not account_id:
                    field_id = field_obj.search([('field_description', '=', 'Income Account'), ('name', '=', 'property_account_income_categ_id')])
                    if field_id and self._context:
                        property_id = property_obj.search( [('fields_id', '=', field_id[0].id), ('company_id', '=', self.order_id.company_id.id)])
                    else:
                        property_id = False
                    if property_id:
                        acc_ref = property_obj.browse(property_id[0]).value_reference
                        account_id = acc_ref and acc_ref.split(',') and acc_ref.split(',')[1]
                        account_id = int(account_id)
                    else:
                        account_id = False
                if not account_id:
                    raise UserError(_('Error!'),
                            _('Please define income account for this product: "%s" (id:%d).') % \
                            (self.product_id.name, self.product_id.id,))
            else:
                prop = self.pool.get('ir.property').get(
                        'property_account_income_categ_id', 'product.category')
                account_id = prop and prop.id or False
#            uosqty = self._get_line_qty(self)
#            pu = 0.0
#            if uosqty:
#                pu = round(self.price_unit * self.product_uom_qty / uosqty,
#                        self.pool.get('decimal.precision').precision_get('Product Price'))
#            fpos = self.order_id.fiscal_position or False
#            account_id = self.pool.get('account.fiscal.position').map_account(fpos, account_id)
            if not account_id:
                raise UserError(_('Error!'),
                            _('There is no Fiscal Position defined or Income category account defined for default properties of Product categories.'))
        res = {
            'name': self.name,
            'sequence': self.sequence,
            'origin': self.order_id.name,
            'account_id': account_id or False,
            'price_unit': self.price_unit,
            'quantity': qty,
            'discount': self.discount,
            'uom_id': self.product_uom.id,
            'product_id': self.product_id.id or False,
            'invoice_line_tax_ids': [(6, 0, self.tax_id.ids)],
            'account_analytic_id': self.order_id.analytic_account_id.id,
        }
        return res
    
    
    @api.multi
    def invoice_line_create(self, invoice_id, qty):
        """
        Create an invoice line. The quantity to invoice can be positive (invoice) or negative
        (refund).

        :param invoice_id: integer
        :param qty: float quantity to invoice
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for line in self:
            ctx = dict(self._context, lang=self.order_id.partner_id.lang)
            ctx['sale_id'] = line.order_id 
            if not float_is_zero(qty, precision_digits=precision):
                vals = line._prepare_invoice_line(qty=qty)
                vals.update({'invoice_id': invoice_id, 'sale_line_ids': [(6, 0, [line.id])]})
                self.env['account.invoice.line'].create(vals)       
    
class stock_move(models.Model):
    _inherit = 'stock.move'
    
    sale_line_id = fields.Many2one('sale.order.line', 'Sale Order Line')


    def attribute_price(self,cr, uid, move, context=None):
        """
            Attribute price to move, important in inter-company moves or receipts with only one partner
        """
        if not move.price_unit:
            price = move.sale_line_id and move.sale_line_id.price_unit or 0.0
            self.write(cr, uid,[move.id], {'price_unit': price})    
            

# class ProcurementOrder(models.Model):
#     _inherit = "procurement.order"
    
#     def _run_move_create(self,cr, uid ,procurement, context=None):
#         ''' Returns a dictionary of values that will be used to create a stock move from a procurement.
#         This function assumes that the given procurement has a rule (action == 'move') set on it.

#         :param procurement: browse record
#         :rtype: dictionary
#         '''
        
#         if procurement.product_id.is_pack==True:
#             return {}
#         newdate = (datetime.strptime(procurement.date_planned, '%Y-%m-%d %H:%M:%S') - relativedelta(days=procurement.rule_id.delay or 0)).strftime('%Y-%m-%d %H:%M:%S')
#         group_id = False
#         if procurement.rule_id.group_propagation_option == 'propagate':
#             group_id = procurement.group_id and procurement.group_id.id or False
#         elif procurement.rule_id.group_propagation_option == 'fixed':
#             group_id = procurement.rule_id.group_id and procurement.rule_id.group_id.id or False
#         #it is possible that we've already got some move done, so check for the done qty and create
#         #a new move with the correct qty
#         already_done_qty = 0
#         for move in procurement.move_ids:
#             already_done_qty += move.product_uom_qty if move.state == 'done' else 0
#         qty_left = max(procurement.product_qty - already_done_qty, 0)
#         vals = {
#             'name': procurement.name,
#             #'company_id': procurement.rule_id.company_id.id or procurement.rule_id.location_src_id.company_id.id or procurement.rule_id.location_id.company_id.id or procurement.company_id.id,
#             'company_id': procurement.company_id.id or procurement.rule_id.company_id.id or procurement.rule_id.location_src_id.company_id.id or procurement.rule_id.location_id.company_id.id,
#             'product_id': procurement.product_id.id,
#             'product_uom': procurement.product_uom.id,
#             'product_uom_qty': qty_left,
#             'partner_id': procurement.rule_id.partner_address_id.id or (procurement.group_id and procurement.group_id.partner_id.id) or False,
#             'location_id': procurement.rule_id.location_src_id.id,
#             'location_dest_id': procurement.location_id.id,
#             'move_dest_id': procurement.move_dest_id and procurement.move_dest_id.id or False,
#             'procurement_id': procurement.id,
#             'rule_id': procurement.rule_id.id,
#             'procure_method': procurement.rule_id.procure_method,
#             'origin': procurement.origin,
#             'picking_type_id': procurement.rule_id.picking_type_id.id,
#             'group_id': group_id,
#             'route_ids': [(4, x.id) for x in procurement.route_ids],
#             'warehouse_id': procurement.rule_id.propagate_warehouse_id.id or procurement.rule_id.warehouse_id.id,
#             'date': newdate,
#             'date_expected': newdate,
#             'propagate': procurement.rule_id.propagate,
#             'priority': procurement.priority,
#             'sale_line_id': procurement.sale_line_id and procurement.sale_line_id.id,
#         }
#         return vals
        
#     def _run(self, cr, uid, procurement, context=None):
        
#         if procurement.rule_id and procurement.rule_id.action == 'move':
#             if not procurement.rule_id.location_src_id:
#                 self.message_post(cr, uid, [procurement.id], body=_('No source location defined!'), context=context)
#                 return False
#             move_obj = self.pool.get('stock.move')
            
#             move_dict = self._run_move_create(cr, uid, procurement, context=context)
            
#             #create the move as SUPERUSER because the current user may not have the rights to do it (mto product launched by a sale for example)
#             if not move_dict:
#                 return True
#             move_obj.create(cr, SUPERUSER_ID, move_dict, context=context)
#             return True
#         return super(procurement_order, self)._run(cr, uid, procurement, context=context)
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
