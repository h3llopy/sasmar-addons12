from openerp import fields, models ,api, _
from openerp.http import request
from requests.auth import HTTPBasicAuth
from openerp.exceptions import Warning
import json
import requests
from datetime import datetime
from openerp.exceptions import UserError
import time
import ast

class single_ict_invoice(models.TransientModel):
    _name = 'single.ict.invoice.wizard'
    

    @api.multi
    def create_invoice_bill(self):

        invoice_ids = self.create_invoice()
        bill_ids = self.create_bill()


    @api.multi
    def create_invoice(self):
        active_ids=self._context.get('active_ids',[])
        
        sale_order_ids = []
        
        ict_ids = self.env['inter.company.transfer.ept'].search([('id','in',active_ids),('state','in',['processed']),('customer_invoice_id','=',False)])
        combination = {}
        for ict in ict_ids:
            sale_id = ict.sale_order_id
            if sale_id.invoice_ids:
                continue
            icu = ict.source_company_id.intercompany_user_id.id
            temp = combination.get(icu,[])
            temp.append(ict.sale_order_id.id)
            combination[icu] = temp
            sale_order_ids.append(sale_id.id)
        invoice_ids = []
        for comb_key,comb_val in combination.iteritems():
            sale_advance_payment = self.env['sale.advance.payment.inv'].sudo(comb_key).create({'advance_payment_method':'delivered'})
            invoices = sale_advance_payment.with_context({'active_ids':comb_val,'open_invoices':True}).sudo(comb_key).create_invoices()
            
            invoice_id = invoices.get('res_id',False)
            if invoice_id:
                for ict in ict_ids:
                    if ict.sale_order_id.id in comb_val:
                        ict.write({'customer_invoice_id':invoice_id})
                invoice_id = self.env['account.invoice'].sudo(comb_key).browse(invoice_id)
                invoice_ids.append(invoice_id)
            else:
                domain = invoices.get('domain',[])
            
                invoice_ids  = ast.literal_eval(domain)
            
                invoices = self.env['account.invoice'].sudo(comb_key).browse(invoice_ids[0][2])
                
                for temp_ept in invoices:   
                    invoice_ids.append(temp_ept)
                    
                for ict in ict_ids:
                    for inv in invoices:
                        if ict.destination_company_id.partner_id.id == inv.partner_id.id and ict.sale_order_id.id in comb_val:
                            ict.write({'customer_invoice_id':inv.id})
                            break
            
            config_record = self.env.ref('ICT_ept_v9.intercompany_transaction_config_record')
            if config_record.auto_validate_invoices:
                for invoice in invoice_ids:
                    invoice.signal_workflow('invoice_open')
                
        return invoice_ids
    
    @api.multi
    def create_bill(self):
        active_ids=self._context.get('active_ids',[]) 
        
        purchase_order_ids = []
        invoice_obj = self.env['account.invoice']
        
        ict_ids = self.env['inter.company.transfer.ept'].search([('id','in',active_ids),('state','in',['processed']),('vendor_bill_id','=',False)])
        for ict in ict_ids : 
            purchase_order_ids.append(ict.purchase_order_id)

        combination = []
        temp = []
        for ict in ict_ids:
            temp.append(ict.source_company_id.partner_id)
            temp.append(ict.destination_company_id)
            temp.append(ict.currency_id)
            if temp not in combination:
                combination.append(temp)
            temp=[]

        bill_ids = []
        for com in combination:
            context = {'default_type': 'in_invoice',
                        'type': 'in_invoice', 
                        'journal_type': 'purchase',
                    }
                                
            values = {
                'company_id': com[1].id or False,
                'currency_id':com[2].id,
                'partner_id':com[0].id or False,
                'type': 'in_invoice',
                'journal_type': 'purchase',
                'journal_id': com[1].default_purchase_journal and com[1].default_purchase_journal.id
            }
            

            purchase_user = com[1].intercompany_user_id.id
            
            vals = invoice_obj.sudo(purchase_user).with_context(context).new(values)
            
            temp_ict_ids = []
            for pur in purchase_order_ids:
                if [ pur.partner_id,pur.company_id,pur.currency_id] == com:
                    vals.purchase_id = pur.id
                    vals.sudo(purchase_user).purchase_order_change()
                    
                    for ict in ict_ids:
                        if ict.purchase_order_id == pur:
                            temp_ict_ids.append(ict.id)
                    
                    
            vals.sudo(purchase_user)._onchange_partner_id()
            vals.date_invoice = datetime.today()
            vals.sudo(purchase_user)._onchange_payment_term_date_invoice()
            vals.sudo(purchase_user)._onchange_origin()
            vals.currency_id = com[2]
            vals.journal_id = com[1].default_purchase_journal and com[1].default_purchase_journal.id or vals.journal_id

            for line in vals.invoice_line_ids:
                line.quantity = line.purchase_line_id and line.purchase_line_id.product_qty or 0.0
                line.sudo(purchase_user)._compute_price()
                
            bill_id =  self.env['account.invoice'].sudo(purchase_user).with_context({'type':'in_invoice'}).create(vals._convert_to_write(vals._cache))
            bill_ids.append(bill_id)
            config_record = self.env.ref('ICT_ept_v9.intercompany_transaction_config_record')
            if config_record.auto_validate_invoices:
                bill_id.sudo(purchase_user).signal_workflow('invoice_open')

            if temp_ict_ids:
                temp_ict_ids = self.env['inter.company.transfer.ept'].browse(temp_ict_ids)
                temp_ict_ids.write({'vendor_bill_id':bill_id.id})      
   
        return bill_ids
    
class single_ict_refund(models.TransientModel):
    _name = 'single.ict.refund.wizard'

    @api.multi
    def create_refund_invoice_bills(self):
        self.create_refund_invoice()
        self.create_refund_bills()

    @api.multi
    def create_refund_invoice(self):

        active_ids=self._context.get('active_ids',[]) 
        account_invoice_obj = self.env['account.invoice']
        account_invoice_line_obj = self.env['account.invoice.line']
        
        reverse_ict_ids = self.env['reverse.inter.company.transfer.ept'].search([('id','in',active_ids),('state','in',['processed']),('refund_customer_invoice_id','=',False)])
        refund_rict_combination = []
        temp = []
       
        created_refunds = []
        for rict in reverse_ict_ids:
            icu = rict.ict_id.source_company_id.intercompany_user_id.id
            ict = rict.ict_id
            if not ict.customer_invoice_id :
                continue
            invoice = ict.customer_invoice_id
            refund_invoice_id = False
            for comb in refund_rict_combination:
                if comb[0] == invoice:
                    refund_invoice_id = comb[1]
            if not refund_invoice_id:
                source_company = rict.ict_id.source_company_id
                refund_journal = source_company.default_sales_refund_journal and source_company.default_sales_refund_journal.id or None
                refund_values_dict = account_invoice_obj.sudo(icu)._prepare_refund(invoice,date_invoice=invoice.date_invoice,description=invoice.name,journal_id=refund_journal)
                refund_values_dict['invoice_line_ids'] = False
                created_refund = self.env['account.invoice'].sudo(icu).create(refund_values_dict)
                temp.append(invoice)
                temp.append(created_refund)
                if temp not in refund_rict_combination:
                    refund_rict_combination.append(temp)
                    
                created_refunds.append(created_refund)
            
            for line in rict.line_ids:
                
                refund_line_vals = {
                    'product_id':line.product_id.id,
                    'quantity':line.quantity,
                    'account_id':invoice.invoice_line_ids[0].account_id.id,
                    'company_id':invoice.company_id.id,
                    'invoice_id':refund_invoice_id and refund_invoice_id.id or created_refund.id,
                    'price_unit':line.price,
                    'name':line.product_id.name
                    }
                inv_line = account_invoice_line_obj.sudo(icu).create(refund_line_vals)
                inv_line.sudo(icu)._onchange_uom_id()
                inv_line.sudo(icu)._onchange_account_id()
                inv_line.sudo(icu)._onchange_product_id()

                rict.sudo(icu).write({'refund_customer_invoice_id':created_refund.id})
                

        config_record = self.env.ref('ICT_ept_v9.intercompany_transaction_config_record')
        if config_record.auto_validate_refunds:
            for refund in created_refunds:
                refund.sudo().signal_workflow('invoice_open')
                
        return True
    
    @api.multi
    def create_refund_bills(self):
        
        active_ids=self._context.get('active_ids',[])
        account_invoice_obj = self.env['account.invoice']
        account_invoice_line_obj = self.env['account.invoice.line']
        
        reverse_ict_ids = self.env['reverse.inter.company.transfer.ept'].search([('id','in',active_ids),('state','in',['processed']),('refund_vendor_bill_id','=',False)])

        refund_rict_combination = []
        temp = []
        
        
        created_refunds = []
        for rict in reverse_ict_ids:
            icu = rict.ict_id.destination_company_id.intercompany_user_id.id
            ict = rict.ict_id
            if not ict.vendor_bill_id :
                continue
            invoice = ict.vendor_bill_id
            refund_invoice_id = False
            for comb in refund_rict_combination:
                if comb[0] == invoice:
                    refund_invoice_id = comb[1]
            if not refund_invoice_id:
                dest_company = rict.ict_id.destination_company_id
                refund_journal = dest_company.default_purchase_refund_journal and dest_company.default_purchase_refund_journal.id or None
                refund_values_dict = account_invoice_obj.sudo(icu)._prepare_refund(invoice,date_invoice=invoice.date_invoice,description=invoice.name,journal_id=refund_journal)
                refund_values_dict['invoice_line_ids'] = False
                created_refund = self.env['account.invoice'].sudo(icu).create(refund_values_dict)
                temp.append(invoice)
                temp.append(created_refund)
                if temp not in refund_rict_combination:
                    refund_rict_combination.append(temp)

            for line in rict.line_ids:
                
                refund_line_vals = {
                    'product_id':line.product_id.id,
                    'quantity':line.quantity,
                    'account_id':invoice.invoice_line_ids[0].account_id.id,
                    'company_id':invoice.company_id.id,
                    'invoice_id':refund_invoice_id and refund_invoice_id.id or created_refund.id,
                    'price_unit':line.price,
                    'name':line.product_id.name
                    }

                inv_line = account_invoice_line_obj.sudo(icu).create(refund_line_vals)
                inv_line.sudo(icu)._onchange_uom_id()
                inv_line.sudo(icu)._onchange_account_id()
                inv_line.sudo(icu)._onchange_product_id()

                rict.sudo(icu).write({'refund_vendor_bill_id':created_refund.id})
            created_refunds.append(created_refund)
            
        config_record = self.env.ref('ICT_ept_v9.intercompany_transaction_config_record')
        if config_record.auto_validate_refunds:
            for refund in created_refunds:
                refund.sudo().signal_workflow('invoice_open')
                
        return True
        