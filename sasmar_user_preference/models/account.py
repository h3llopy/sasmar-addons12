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
from odoo import api, fields, models, _
from odoo.tools.translate import _
from odoo.tools.safe_eval import safe_eval
import time
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare
from odoo.exceptions import UserError, RedirectWarning, ValidationError
TYPE2JOURNAL = {
    'out_invoice': 'sale',
    'in_invoice': 'purchase',
    'out_refund': 'sale',
    'in_refund': 'purchase',
}

class Accountaccount(models.Model):
    _inherit = "account.account"
    
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        ctx = dict(self._context or {})
        if ctx.get('account'):
            com = ctx.get('account')[0][1]
            company_id = self.env['account.invoice'].browse(com).company_id.id
            args.append(['company_id','=' ,company_id ])
        if name:
            domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&'] + domain
        accounts = self.search(domain + args, limit=limit)
        return accounts.name_get()
    
        
class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"
    
    def _set_taxes(self):
        """ Used in on_change to set taxes and price."""
        if self.invoice_id.type in ('out_invoice', 'out_refund'):
            taxes = self.product_id.taxes_id or self.account_id.tax_ids
        else:
            taxes = self.product_id.supplier_taxes_id or self.account_id.tax_ids

        # Keep only taxes of the company
        company_id = self.company_id or self.invoice_id.company_id
        taxes = taxes.filtered(lambda r: r.company_id == company_id)
        self.invoice_line_tax_ids = fp_taxes = self.invoice_id.fiscal_position_id.map_tax(taxes)

        fix_price = self.env['account.tax']._fix_tax_included_price
        if self.invoice_id.type in ('in_invoice', 'in_refund'):
            if not self.price_unit or float_compare(self.price_unit, self.product_id.standard_price, precision_digits=self.currency_id.rounding) == 0:
                self.price_unit = fix_price(self.product_id.standard_price, taxes, fp_taxes)
        else:
            self.price_unit = fix_price(self.product_id.lst_price, taxes, fp_taxes)
            
    @api.onchange('product_id')
    def _onchange_product_id(self):
        domain = {}
        if not self.invoice_id:
            return
        part = self.invoice_id.partner_id
        fpos = self.invoice_id.fiscal_position_id
        company = self.invoice_id.company_id
        currency = self.invoice_id.currency_id
        type = self.invoice_id.type
        if not part:
            warning = {
                    'title': _('Warning!'),
                    'message': _('You must first select a partner!'),
                }
            return {'warning': warning}

        if not self.product_id:
            if type not in ('in_invoice', 'in_refund'):
                self.price_unit = 0.0
            domain['uom_id'] = []
        else:
            if part.lang:
                product = self.product_id.with_context(lang=part.lang)
            else:
                product = self.product_id

            self.name = product.partner_ref
            
            account = self.get_invoice_line_account(type, product, fpos, company)
            if account:
                self.account_id = account.id
            self._set_taxes()

            if type in ('in_invoice', 'in_refund'):
                if product.description_purchase:
                    self.name += '\n' + product.description_purchase
            else:
                if product.description_sale:
                    self.name += '\n' + product.description_sale

            if not self.uom_id or product.uom_id.category_id.id != self.uom_id.category_id.id:
                self.uom_id = product.uom_id.id
            domain['uom_id'] = [('category_id', '=', product.uom_id.category_id.id)]

            if company and currency:
                if company.currency_id != currency:
                    self.price_unit = self.price_unit * currency.with_context(dict(self._context or {}, date=self.invoice_id.date_invoice)).rate

                if self.uom_id and self.uom_id.id != product.uom_id.id:
                    self.price_unit = self.env['product.uom']._compute_price(
                        product.uom_id.id, self.price_unit, self.uom_id.id)
        return {'domain': domain}


#    
class account_payment(models.Model):
    _inherit = "account.payment"

    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        if not self.invoice_ids:
            # Set default partner type for the payment type
            if self.payment_type == 'inbound':
                self.partner_type = 'customer'
            elif self.payment_type == 'outbound':
                self.partner_type = 'supplier'
        # Set payment method domain
        res = self._onchange_journal()
        if not res.get('domain', {}):
            res['domain'] = {}
        res['domain']['journal_id'] = self.payment_type == 'inbound' and [('at_least_one_inbound', '=', True)] or [('at_least_one_outbound', '=', True)]
        res['domain']['journal_id'].append(('type', 'in', ('bank', 'cash')))
        if self.invoice_ids:
            company_id = self.env['account.invoice'].browse(self.invoice_ids[0].id).company_id.id
            res['domain']['journal_id'].append(('company_id', '=', company_id))
        return res
    
    @api.one
    @api.depends('invoice_ids', 'payment_type', 'partner_type', 'partner_id')
    def _compute_destination_account_id(self):
        property_obj = self.env['ir.property']
        field_obj = self.env['ir.model.fields']
        if self.invoice_ids:
            self.destination_account_id = self.invoice_ids[0].account_id.id
        elif self.payment_type == 'transfer':
            if not self.company_id.transfer_account_id.id:
                raise UserError(_('Transfer account not defined on the company.'))
            self.destination_account_id = self.company_id.transfer_account_id.id
        elif self.partner_id:
            
            if self.partner_type == 'customer':
                
                field_id = field_obj.search([('field_description', '=', 'Account Receivable'), ('name', '=', 'property_account_receivable_id')])
                if field_id:
                    property_id = property_obj.search([('fields_id', '=', field_id[0].id), ('company_id', '=', self.company_id.id)])
                if property_id:
                    acc_ref = property_id.browse(property_id[0].id).value_reference
                    acc_income_acc = acc_ref and acc_ref.split(',') and acc_ref.split(',')[1]
                    acc_income_acc = int(acc_income_acc)
                else:
                    acc_income_acc = False
                self.destination_account_id = acc_income_acc
            else:
                field_id = field_obj.search([('field_description', '=', 'Account Payable'), ('name', '=', 'property_account_payable_id')])
                if field_id:
                    property_id = property_obj.search([('fields_id', '=', field_id[0].id), ('company_id', '=', self.company_id.id)])
                if property_id:
                    acc_ref = property_id.browse(property_id[0].id).value_reference
                    acc_income_acc = acc_ref and acc_ref.split(',') and acc_ref.split(',')[1]
                    acc_income_acc = int(acc_income_acc)
                else:
                    acc_income_acc = False
                self.destination_account_id = acc_income_acc
        
class account_invoice(models.Model):
    _inherit = 'account.invoice'
    
    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        account_id = False
        payment_term_id = False
        fiscal_position = False
        bank_id = False
        p = self.partner_id
        company_id = self.company_id.id
        if self._context.get('type') == 'in_invoice':
            journal_id = self.env['account.journal'].search([('type','=', 'purchase'),('company_id','=', company_id)])
        elif self._context.get('type') == 'out_invoice':
            journal_id = self.env['account.journal'].search([('type','=', 'sale'),('company_id','=', company_id)])
        else:
            journal_id = self._default_journal()
        type = self.type
        if p:
            partner_id = p.id
            rec_account = p.property_account_receivable_id
            pay_account = p.property_account_payable_id
            if company_id:
                if p.property_account_receivable_id.company_id and \
                        p.property_account_receivable_id.company_id.id != company_id and \
                        p.property_account_payable_id.company_id and \
                        p.property_account_payable_id.company_id.id != company_id:
                    prop = self.env['ir.property']
                    rec_dom = [('name', '=', 'property_account_receivable_id'), ('company_id', '=', company_id)]
                    pay_dom = [('name', '=', 'property_account_payable_id'), ('company_id', '=', company_id)]
                    res_dom = [('res_id', '=', 'res.partner,%s' % partner_id)]
                    rec_prop = prop.search(rec_dom + res_dom) or prop.search(rec_dom)
                    pay_prop = prop.search(pay_dom + res_dom) or prop.search(pay_dom)
                    rec_account = rec_prop.get_by_record(rec_prop)
                    pay_account = pay_prop.get_by_record(pay_prop)
                    if not rec_account and not pay_account:
                        action = self.env.ref('account.action_account_config')
                        msg = _('Cannot find a chart of accounts for this company, You should configure it. \nPlease go to Account Configuration.')
                        raise RedirectWarning(msg, action.id, _('Go to the configuration panel'))

            if type in ('out_invoice', 'out_refund'):
                account_id = rec_account.id
                payment_term_id = p.property_payment_term_id.id
            else:
                account_id = pay_account.id
                payment_term_id = p.property_supplier_payment_term_id.id
            fiscal_position = p.property_account_position_id.id
            bank_id = p.bank_ids and p.bank_ids.ids[0] or False
        self.account_id = account_id
        self.payment_term_id = payment_term_id
        self.fiscal_position_id = fiscal_position
        self.journal_id = journal_id[0].id
        ctx = dict(self._context or {})
        ctx['company_id'] = self.company_id.id
        
        property_obj = self.env['ir.property']
        field_obj = self.env['ir.model.fields']
        '''Account income property '''
        field_id = field_obj.search([('field_description', '=', 'Income Account'), ('name', '=', 'property_account_income_id')])
        if field_id:
            property_id = property_obj.search([('fields_id', '=', field_id[0].id), ('company_id', '=', self.company_id.id)])
        else:
            property_id = False
        if property_id:
            acc_ref = property_id.browse(property_id[0].id).value_reference
            acc_income_acc = acc_ref and acc_ref.split(',') and acc_ref.split(',')[1]
            
            acc_income_acc = int(acc_income_acc)
        else:
            acc_income_acc = False
        if not acc_income_acc:
            field_id = field_id.search([('field_description', '=', 'Income Account'), ('name', '=', 'property_account_income_categ_id')])
            if field_id:
                property_id = property_id.search([('fields_id', '=', field_id[0].id), ('company_id', '=', self.company_id.id)])
            else:
                property_id = False
            if property_id:
                acc_ref = property_id.browse( property_id[0].id).value_reference
                acc_income_acc = acc_ref and acc_ref.split(',') and acc_ref.split(',')[1]
                acc_income_acc = int(acc_income_acc)
                
        '''Expence Account   '''
        field_id = field_obj.search([('field_description', '=', 'Expense Account'), ('name', '=', 'property_account_expense_id')])
        if field_id:
            property_id = property_obj.search([('fields_id', '=', field_id[0].id), ('company_id', '=', self.company_id.id)])
        else:
            property_id = False
        if property_id:
            acc_ref = property_id.browse(property_id[0].id).value_reference
            acc_exp_acc = acc_ref and acc_ref.split(',') and acc_ref.split(',')[1]
            
            acc_exp_acc = int(acc_exp_acc)
        else:
            acc_exp_acc = False
        if not acc_exp_acc:
            field_id = field_id.search([('field_description', '=', 'Expense Account'), ('name', '=', 'property_account_expense_categ_id')])
            if field_id:
                property_id = property_id.search([('fields_id', '=', field_id[0].id), ('company_id', '=', self.company_id.id)])
            else:
                property_id = False
            if property_id:
                acc_ref = property_id.browse( property_id[0].id).value_reference
                acc_exp_acc = acc_ref and acc_ref.split(',') and acc_ref.split(',')[1]
                acc_exp_acc = int(acc_exp_acc)
        if (self.invoice_line_ids and  ctx.get('type') == 'out_invoice') or (self.invoice_line_ids and  ctx.get('default_type') == 'out_invoice'):
            for i in self.invoice_line_ids:
                if i:
                    i.account_id = acc_income_acc
        if (self.invoice_line_ids and  ctx.get('type') == 'in_invoice') or (self.invoice_line_ids and  ctx.get('default_type') == 'in_invoice'):
            for i in self.invoice_line_ids:
                if i:
                    i.account_id = acc_exp_acc
        if type in ('in_invoice', 'in_refund'):
            self.partner_bank_id = bank_id

            
class account_voucher(models.Model):
    
    _inherit = 'account.voucher'
    
    _defaults = {
                 'company_id': lambda self, cr, uid, context: context.get('company_id') 
                 }
    
class AccountRefund(models.TransientModel):
    _inherit = "account.invoice.refund"
    
    @api.multi
    def compute_refund(self, mode='refund'):
        inv_obj = self.env['account.invoice']
        inv_tax_obj = self.env['account.invoice.tax']
        inv_line_obj = self.env['account.invoice.line']
        context = dict(self._context or {})
        
        xml_id = False
        for form in self:
            created_inv = []
            date = False
            description = False
            for inv in inv_obj.browse(context.get('active_ids')):
                context.update({'company_id': inv.company_id.id})
                if inv.state in ['draft', 'proforma2', 'cancel']:
                    raise UserError(_('Cannot refund draft/proforma/cancelled invoice.'))
                if inv.reconciled and mode in ('cancel', 'modify'):
                    raise UserError(_('Cannot refund invoice which is already reconciled, invoice should be unreconciled first. You can only refund this invoice.'))

                date = form.date or False
                description = form.description or inv.name
                refund = inv.refund(form.date_invoice, date, description, inv.journal_id.id)
                refund.compute_taxes()

                created_inv.append(refund.id)
                if mode in ('cancel', 'modify'):
                    movelines = inv.move_id.line_ids
                    to_reconcile_ids = {}
                    to_reconcile_lines = self.env['account.move.line']
                    for line in movelines:
                        if line.account_id.id == inv.account_id.id:
                            to_reconcile_lines += line
                            to_reconcile_ids.setdefault(line.account_id.id, []).append(line.id)
                        if line.reconciled:
                            line.remove_move_reconcile()
                    refund.signal_workflow('invoice_open')
                    for tmpline in refund.move_id.line_ids:
                        if tmpline.account_id.id == inv.account_id.id:
                            to_reconcile_lines += tmpline
                            to_reconcile_lines.reconcile()
                    if mode == 'modify':
                        invoice = inv.read(
                                    ['name', 'type', 'number', 'reference',
                                    'comment', 'date_due', 'partner_id',
                                    'partner_insite', 'partner_contact',
                                    'partner_ref', 'payment_term_id', 'account_id',
                                    'currency_id', 'invoice_line_ids', 'tax_line_ids',
                                    'journal_id', 'date'])
                        invoice = invoice[0]
                        del invoice['id']
                        invoice_lines = inv_line_obj.browse(invoice['invoice_line_ids'])
                        invoice_lines = inv_obj._refund_cleanup_lines(invoice_lines)
                        tax_lines = inv_tax_obj.browse(invoice['tax_line_ids'])
                        tax_lines = inv_obj._refund_cleanup_lines(tax_lines)
                        invoice.update({
                            'type': inv.type,
                            'company_id': inv.company_id.id,
                            'date_invoice': date,
                            'state': 'draft',
                            'number': False,
                            'invoice_line_ids': invoice_lines,
                            'tax_line_ids': tax_lines,
                            'date': date,
                            'name': description,
                            
                        })
                        for field in ('partner_id', 'account_id', 'currency_id',
                                         'payment_term_id', 'journal_id'):
                                invoice[field] = invoice[field] and invoice[field][0]
                        inv_refund = inv_obj.create(invoice)
                        if inv_refund.payment_term_id.id:
                            inv_refund._onchange_payment_term_date_invoice()
                        created_inv.append(inv_refund.id)
                xml_id = (inv.type in ['out_refund', 'out_invoice']) and 'action_invoice_tree1' or \
                         (inv.type in ['in_refund', 'in_invoice']) and 'action_invoice_tree2'
                # Put the reason in the chatter
                subject = _("Invoice refund")
                body = description
                refund.message_post(body=body, subject=subject)
        if xml_id:
            result = self.env.ref('account.%s' % (xml_id)).read()[0]
            invoice_domain = eval(result['domain'])
            invoice_domain.append(('id', 'in', created_inv))
            result['domain'] = invoice_domain
            return result
        return True
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
