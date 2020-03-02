# -*- coding: utf-8 -*-
from openerp import models,api,fields
import openerp.addons.decimal_precision as dp

class ProductTemplate(models.Model):
    _inherit = "product.template"

    weight_net = fields.Float('Net Weight', digits_compute=dp.get_precision('Stock Weight'), help="The net weight in Kg.")
        
    # @api.multi
    # def _get_product_accounts(self):
    #     return super(ProductTemplate,self)._get_product_accounts()
    #     """
    #     :Viki stopped this method because of wrong calculation of accounts. 
    #     """
    #     if self._context.get('journal_id'):
    #         journal_search =  self.env["account.journal"].browse(self._context.get('journal_id')).company_id.id
    #     elif self._context.get('default_journal_id'):
    #         journal_search =  self.env["account.journal"].browse(self._context.get('default_journal_id')).company_id.id
    #     elif self._context.get('company_id'):
    #         journal_search = self._context.get('company_id')
    #     else:
    #         journal_search = False
    #     property_obj = self.env['ir.property']
    #     field_obj = self.env['ir.model.fields']
    #     '''Account income property '''
    #     field_id = field_obj.search([('field_description', '=', 'Income Account'), ('name', '=', 'property_account_income_id')])
    #     if field_id:
    #         property_id = property_obj.search([('fields_id', '=', field_id[0].id), ('company_id', '=', journal_search)])
    #     else:
    #         property_id = False
    #     if property_id:
    #         acc_ref = property_id.browse(property_id[0].id).value_reference
    #         acc_income_acc = acc_ref and acc_ref.split(',') and acc_ref.split(',')[1]
            
    #         acc_income_acc = int(acc_income_acc)
    #     else:
    #         acc_income_acc =  False
    #     if not acc_income_acc:
    #         field_id = field_id.search([('field_description', '=', 'Income Account'), ('name', '=', 'property_account_income_categ_id')])
    #         if field_id:
    #             property_id = property_id.search([('fields_id', '=', field_id[0].id), ('company_id', '=', journal_search)])
    #         else:
    #             property_id = False
    #         if property_id:
    #             acc_ref = property_id.browse( property_id[0].id).value_reference
    #             acc_income_acc = acc_ref and acc_ref.split(',') and acc_ref.split(',')[1]
    #             acc_income_acc = int(acc_income_acc)
    #         else:
    #             acc_income_acc = self.categ_id.property_account_income_categ_id and self.categ_id.property_account_income_categ_id.id or False
    #     '''Expence Account   '''
    #     field_id = field_obj.search([('field_description', '=', 'Expense Account'), ('name', '=', 'property_account_expense_id')])
    #     if field_id:
    #         property_id = property_obj.search([('fields_id', '=', field_id[0].id), ('company_id', '=', journal_search)])
    #     else:
    #         property_id = False
    #     if property_id:
            
    #         acc_ref = property_id.browse(property_id[0].id).value_reference
    #         acc_exp_acc = acc_ref and acc_ref.split(',') and acc_ref.split(',')[1]
    #         acc_exp_acc = int(acc_exp_acc)
    #     else:
    #         acc_exp_acc = False
    #     if not acc_exp_acc:
    #         field_id = field_id.search([('field_description', '=', 'Expense Account'), ('name', '=', 'property_account_expense_categ_id')])
    #         if field_id:
    #             property_id = property_id.search([('fields_id', '=', field_id[0].id), ('company_id', '=', journal_search)])
    #         else:
    #             property_id = False
    #         if property_id:
    #             acc_ref = property_id.browse( property_id[0].id).value_reference
    #             acc_exp_acc = acc_ref and acc_ref.split(',') and acc_ref.split(',')[1]
    #             acc_exp_acc = int(acc_exp_acc)
    #         else:
    #             acc_exp_acc = self.categ_id.property_account_expense_categ_id and self.categ_id.property_account_expense_categ_id.id or False
    #     '''Stcok Input Account '''
                
    #     field_id = field_obj.search([('field_description', '=', 'Stock Input Account'), ('name', '=', 'property_stock_account_input')])
    #     if field_id:
    #         property_id = property_obj.search([('fields_id', '=', field_id[0].id), ('company_id', '=', journal_search)])
    #     else:
    #         property_id = False
    #     if property_id:
    #         acc_ref = property_id.browse(property_id[0].id).value_reference
    #         stock_in_acc = acc_ref and acc_ref.split(',') and acc_ref.split(',')[1]
            
    #         stock_in_acc = int(stock_in_acc)
    #     else:
    #         stock_in_acc = False
    #     if not stock_in_acc:
    #         field_id = field_id.search([('field_description', '=', 'Stock Input Account'), ('name', '=', 'property_stock_account_input_categ_id')])
    #         if field_id:
    #             property_id = property_id.search([('fields_id', '=', field_id[0].id), ('company_id', '=', journal_search)])
    #         else:
    #             property_id = False
    #         if property_id:
    #             acc_ref = property_id.browse( property_id[0].id).value_reference
    #             stock_in_acc = acc_ref and acc_ref.split(',') and acc_ref.split(',')[1]
    #             stock_in_acc = int(stock_in_acc)
    #     '''Stcok Output Account '''
    #     field_id = field_obj.search([('field_description', '=', 'Stock Output Account'), ('name', '=', 'property_stock_account_output')])
    #     if field_id:
    #         property_id = property_obj.search([('fields_id', '=', field_id[0].id), ('company_id', '=', journal_search)])
    #     else:
    #         property_id = False
    #     if property_id:
    #         acc_ref = property_id.browse(property_id[0].id).value_reference
    #         stock_out_acc = acc_ref and acc_ref.split(',') and acc_ref.split(',')[1]
            
    #         stock_out_acc = int(stock_out_acc)
    #     else:
    #         stock_out_acc = False
    #     if not stock_out_acc:
    #         field_id = field_id.search([('field_description', '=', 'Stock Input Account'), ('name', '=', 'property_stock_account_output_categ_id')])
    #         if field_id:
    #             property_id = property_id.search([('fields_id', '=', field_id[0].id), ('company_id', '=', journal_search)])
    #         else:
    #             property_id = False
    #         if property_id:
    #             acc_ref = property_id.browse( property_id[0].id).value_reference
    #             stock_out_acc = acc_ref and acc_ref.split(',') and acc_ref.split(',')[1]
    #             stock_out_acc = int(stock_in_acc)
        
    #     '''Stcok JOurnal Account '''
    #     field_id = field_obj.search([('field_description', '=', 'Stock Journal'), ('name', '=', 'property_stock_journal')])
    #     if field_id:
    #         property_id = property_obj.search([('fields_id', '=', field_id[0].id), ('company_id', '=', journal_search)])
    #     else:
    #         property_id = False    
    #     if property_id:
    #         acc_ref = property_id.browse(property_id[0].id).value_reference
    #         stock_journal_acc = acc_ref and acc_ref.split(',') and acc_ref.split(',')[1]
            
    #         stock_journal_acc = int(stock_journal_acc)
    #     else:
    #         stock_journal_acc = False
        
    #     '''Stcok valuation Account '''
    #     field_id = field_obj.search([('field_description', '=', 'Stock Valuation Account'), ('name', '=', 'property_stock_valuation_account_id')])
    #     if field_id:
    #         property_id = property_obj.search([('fields_id', '=', field_id[0].id), ('company_id', '=', journal_search)])
    #     else:
    #         property_id = False
    #     if property_id:
    #         acc_ref = property_id.browse(property_id[0].id).value_reference
    #         stock_valuation_acc = acc_ref and acc_ref.split(',') and acc_ref.split(',')[1]
            
    #         stock_valuation_acc = int(stock_valuation_acc)
    #     else:
    #         stock_valuation_acc = False
    #     account = self.env['account.account']
    #     return {
    #         'income': account.browse(acc_income_acc) ,
    #         'expense': account.browse(acc_exp_acc) ,
    #         'stock_input': account.browse(stock_in_acc), 
    #         'stock_output': account.browse(stock_out_acc)  , 
    #         'stock_valuation': account.browse(stock_valuation_acc) ,
    #         'stock_journal': account.browse(stock_journal_acc),
    #     }

    