# -*- coding: utf-8 -*-
from openerp import models,api,fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import datetime,date

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    confirm_date = fields.Date(string = 'Confirm  Date' , readonly=True)
    doc= fields.Boolean('Transfer Document')
    
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].with_context(company_id=vals.get('company_id') or False).next_by_code('sale.order') or 'New'
        return super(SaleOrder,self).create(vals)
    
    @api.onchange('company_id')
    def onchange_company_id(self):
        if self.company_id:
            search_warehouse = self.env['stock.warehouse'].search([('company_id','=',self.company_id.id)])
            self.warehouse_id = search_warehouse and search_warehouse[0].id or False

    # Comment by dhaval : Managed in force company Module            
    # @api.multi
    # def _prepare_invoice(self ):
    #     return super(SaleOrder,self)._prepare_invoice()
    #     """
    #     :Viki Wrong Way of getting account from property field.
    #     """
    #     property_obj = self.env['ir.property']
    #     field_obj = self.env['ir.model.fields']
    #     self.ensure_one()    
    #     journal_ids = self.env['account.journal'].search(
    #         [('type', '=', 'sale'), ('company_id', '=', self.company_id.id)])
    #     if not journal_ids:
    #         raise UserError(_('There is no Account for %s Company. You may have to set a chart of account from Accounting app, settings menu.') % \
    #                 (self.company_id.name,))
    #     field_ids = field_obj.search([('field_description', '=', 'Account Receivable')])
    #     if field_ids:
    #         for field in field_ids:
    #             property_id = property_obj.search([('fields_id', '=', field.id), ('company_id', '=', self.company_id.id)])
    #             if property_id:
    #                 acc_ref = property_obj.browse(property_id[0].id).value_reference
    #                 account_id = acc_ref and acc_ref.split(',') and acc_ref.split(',')[1]
    #                 account_id = int(account_id)
    #     else:
    #         raise UserError( _('There is no Account for %s Company. You may have to set a chart of account from Accounting app, settings menu.') % \
    #                                     (self.company_id.name,))
    #     invoice_vals = {
    #         'name': self.client_order_ref or '',
    #         'origin': self.name,
    #         'type': 'out_invoice',
    #         'reference': self.client_order_ref or self.name,
    #         'account_id': account_id ,
    #         'partner_id': self.partner_invoice_id.id,
    #         'journal_id': journal_ids[0].id,
    #         'currency_id': self.pricelist_id.currency_id.id,
    #         'comment': self.note,
    #         'payment_term_id': self.payment_term_id.id,
    #         'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
    #         'company_id': self.company_id.id,
    #         'user_id': self.user_id and self.user_id.id,
    #         'team_id': self.team_id.id,
    #     }
    #     return invoice_vals
    
    @api.one
    def copy(self, default=None):
        default = dict(default or {})
        default.update(confirm_date=False,doc=False)
        return super(SaleOrder, self).copy(default=default)
    
    @api.multi
    def delivery_set(self):
        """
        :Viki Overridden Method in Base for price_unit (Me too.) 
        """
        # Remove delivery products from the sale order
        self._delivery_unset()

        for order in self:
            carrier = order.carrier_id
            if carrier:
                if order.state not in ('draft', 'sent'):
                    raise UserError(_('The order state have to be draft to add delivery lines.'))

                if carrier.delivery_type not in ['fixed', 'base_on_rule']:
                    # Shipping providers are used when delivery_type is other than 'fixed' or 'base_on_rule'
                    price_unit = order.carrier_id.get_shipping_price_from_so(order)[0]
                else:
                    # Classic grid-based carriers
                    carrier = order.carrier_id.verify_carrier(order.partner_shipping_id)
                    if not carrier:
                        raise UserError(_('No carrier matching.'))
                    price_unit = carrier.get_price_available(order)
                    if order.company_id.currency_id.id != order.pricelist_id.currency_id.id:
                        price_unit = order.pricelist_id.currency_id.with_context(date=order.date_order).compute(price_unit, order.pricelist_id.currency_id)

                order._create_delivery_line(carrier, price_unit)

            else:
                raise UserError(_('No carrier set for this order.'))

        return True
    
    @api.model    
    def cron_sale(self):
        purchase_order = self.env['purchase.order']
        sale_search = self.search([])
        sale_ids = []
        for sale in sale_search:
            if sale.confirm_date:
                confirm_date = datetime.strptime(sale.confirm_date ,'%Y-%m-%d').date()
                if sale.warehouse_id.company_id.id != sale.company_id.id and confirm_date == date.today() and sale.state == 'sale' and sale.doc == False:
                    sale_ids.append(sale.id)
        if sale_ids:
            for sale in sale_ids:
                brw_sale = self.browse(sale)
                brw_sale.write({'doc':True})
        if sale_ids:
            type_id = False
            
            sale_list =[]
            purchase_list =[]
            list_of_same_ids = []
            list_of_purchase_id =[]
            reg_sale_brw = self.browse(sale_ids)
            for sale in reg_sale_brw:
                order_line = []
                order_line_sale = []
                currency_id = sale.company_id.currency_id.id
                partner_sale = sale.company_id.partner_id and sale.company_id.partner_id.id or False
                company_purchase = sale.company_id and sale.company_id.id or False
                #company_purchase = sale.warehouse_id.company_id and sale.warehouse_id.company_id.id or False
                fpos = sale.fiscal_position_id
                company_id = sale.company_id.id
                company_sale = sale.warehouse_id.company_id and sale.warehouse_id.company_id.id or False
                warehouse_sale_id = sale.warehouse_id.id
                type_obj = self.env['stock.picking.type']
                types = type_obj.search([('code', '=', 'incoming'), ('warehouse_id.company_id', '=', sale.warehouse_id.company_id.id)])
                type_id = types[0].id
                partner_purchase = sale.warehouse_id.company_id.partner_id and sale.warehouse_id.company_id.partner_id.id or False
                #partner_purchase = sale.company_id.partner_id and sale.company_id.partner_id.id or False
                if partner_purchase:
                    ctx = dict(self._context or {})
                    ctx.update({'partner_id': partner_purchase})
                shop_pricelist_id = sale.company_id.partner_id.property_product_pricelist and sale.company_id.partner_id.property_product_pricelist.id or False
                if sale_list and purchase_list: 
                    for sale_id, purchase_id in zip(sale_list ,purchase_list):
                        brw_sale = self.browse(sale_id)
                        if  brw_sale.partner_id.id == sale.company_id.partner_id.id:
                            list_of_same_ids.append(sale_id)
                            list_of_purchase_id.append(purchase_id)
                if list_of_same_ids and list_of_purchase_id:
                    for sale_id, purchase_id in zip(list_of_same_ids ,list_of_purchase_id):
                        for line in sale.order_line:
                            purchase_tax_id = fpos.map_tax(line.product_id.supplier_taxes_id.filtered(lambda r: r.company_id.id == company_id))
                            tax_id = [(6, 0, [purchase_tax_id.id])] if purchase_tax_id else False
                            sale_tax_id = fpos.map_tax(line.product_id.taxes_id).filtered(lambda r: r.company_id == line.order_id.company_id) if fpos else line.product_id.taxes_id
                            tax_sale = [(6, 0, [sale_tax_id.id])] if sale_tax_id else False
                            if line.product_id.seller_ids:
                                res = {}
                                supplier_id = self.env['product.supplierinfo'].search([('name','=',partner_purchase ),('product_tmpl_id','=',line.product_id.product_tmpl_id.id ),('company_id','=',company_id)])
                                if supplier_id:
                                    if supplier_id[0].product_code  and  supplier_id[0].product_name:
                                        name = '['+supplier_id[0].product_code + ']' + supplier_id[0].product_name 
                                    else:
                                        name = line.name
                                    
                                    res= {
                                          'product_id': line.product_id.id ,
                                           'product_uom': supplier_id[0].product_uom.id  , 
                                           'date_planned':(datetime.today() + relativedelta(days=supplier_id[0].delay)).strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                           'name': name ,
                                           'product_qty':line.product_uom_qty,
                                           'price_unit':supplier_id[0].price ,
                                           'taxes_id': tax_id,
                                           'order_id':purchase_id
                                           }
                                    currency_id = supplier_id[0].currency_id.id
                                else:
                                    res = {
                                           'product_id': line.product_id.id ,
                                           'product_uom': line.product_uom.id , 
                                           'date_planned':datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                           'name':line.name ,
                                           'product_qty':line.product_uom_qty,
                                           'price_unit':line.price_unit ,
                                           'taxes_id': tax_id,
                                           'order_id':purchase_id
                                         }
                            else:
                                res = {'product_id': line.product_id.id ,
                                       'product_uom': line.product_uom.id , 
                                       'date_planned':datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                       'name':line.name ,
                                       'product_qty':line.product_uom_qty,
                                       'price_unit':line.price_unit ,
                                       'taxes_id': tax_id,
                                       'order_id': purchase_id
                                           }
                            purchase_order_line_obj = self.env['purchase.order.line']
                            create_purcahse_line = purchase_order_line_obj.create(res)
                            product = line.product_id.with_context(pricelist=shop_pricelist_id)
                            price_unit = self.env['account.tax']._fix_tax_included_price(product.price, product.taxes_id, line.tax_id)
                            res_sale = {'product_id': line.product_id.id ,
                                        'product_uom': line.product_uom.id ,
                                        'name':line.name ,
                                        'product_uom_qty':line.product_uom_qty,
                                        'price_unit': price_unit or line.price_unit ,
                                        'tax_id': tax_sale,
                                        'order_id': sale_id,
                            }
                            sale_order_line_obj = self.env['sale.order.line']
                            
                            create_sale_line = sale_order_line_obj.create(res_sale)
                        brw_purchase = purchase_order.browse(purchase_id)
                        write_purchase = brw_purchase.write({'origin': brw_purchase.origin + ','+sale.name})
                        brw_sale = self.browse(sale_id)
                        write_sale = brw_sale.write({'origin': brw_sale.origin + ','+sale.name})
                    list_of_same_ids =[]
                    list_of_purchase_id =[]     
                else:
                    for line in sale.order_line:
                        purchase_tax_id = fpos.map_tax(line.product_id.supplier_taxes_id.filtered(lambda r: r.company_id.id == company_id))
                        tax_id = [(6, 0, [purchase_tax_id.id])] if purchase_tax_id else False
                        sale_tax_id = fpos.map_tax(line.product_id.taxes_id).filtered(lambda r: r.company_id == line.order_id.company_id) if fpos else line.product_id.taxes_id
                        tax_sale = [(6, 0, [sale_tax_id.id])] if sale_tax_id else False
                        if line.product_id.seller_ids:
                            supplier_id = self.env['product.supplierinfo'].search([('name','=',partner_purchase ),('product_tmpl_id','=',line.product_id.product_tmpl_id.id ),('company_id','=',company_id)])
                            if supplier_id:
                                
                                if supplier_id[0].product_code  and  supplier_id[0].product_name:
                                    name = '['+supplier_id[0].product_code + ']' + supplier_id[0].product_name 
                                else:
                                    name = line.name
                                res= {
                                      'product_id': line.product_id.id ,
                                       'product_uom': supplier_id[0].product_uom.id  , 
                                       'date_planned':(datetime.today() + relativedelta(days=supplier_id[0].delay)).strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                       'name': name ,
                                       'product_qty':line.product_uom_qty,
                                       'price_unit':supplier_id[0].price ,
                                       'taxes_id': tax_id,
                                    }
                                currency_id = supplier_id[0].currency_id.id
                            else:
                                res = {
                                       'product_id': line.product_id.id ,
                                       'product_uom': line.product_uom.id , 
                                       'date_planned':datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                       'name':line.name ,
                                       'product_qty':line.product_uom_qty,
                                       'price_unit':line.price_unit ,
                                       'taxes_id': tax_id,
                                     }
                        else:
                            res = {'product_id': line.product_id.id ,
                                   'product_uom': line.product_uom.id , 
                                   'date_planned':datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                   'name':line.name ,
                                   'product_qty':line.product_uom_qty,
                                   'price_unit':line.price_unit ,
                                   'taxes_id': tax_id,
                                       }
                        order_line.append((0, 0, res))
                        product = line.product_id.with_context(pricelist=shop_pricelist_id)
                        price_unit = self.env['account.tax']._fix_tax_included_price(product.price, product.taxes_id, line.tax_id)
                        res_sale = {'product_id': line.product_id.id ,
                                    'product_uom': line.product_uom.id ,
                                    'name':line.name ,
                                    'product_uom_qty':line.product_uom_qty,
                                    'price_unit': price_unit or line.price_unit ,
                                    'tax_id': tax_sale,
                                    }
                        
                        order_line_sale.append((0, 0, res_sale))
                        
                if order_line_sale and partner_sale :
                    vals = {    'partner_id' : partner_sale,
                                'partner_invoice_id' : partner_sale,
                                'partner_shipping_id' : partner_sale,
                                'order_line': order_line_sale,
                                'company_id':company_sale,
                                'pricelist_id': shop_pricelist_id,
                                'warehouse_id': 5,
                                'origin': sale.name,
                         }
                    sale_order = self.create(vals)
                    sales_team = self.env['crm.team'].search([('name','=','Inter-Company')])
                    if sales_team:
                        sale_order.write({
                                    'team_id':sales_team.id
                                    })
                    sale_list.append(sale_order.id)
                if order_line and partner_purchase:
                    p_vals = { 'partner_id' : partner_purchase,
                              'order_line': order_line,
                              'company_id': company_purchase,
                              'picking_type_id': 21,
                              'origin':  sale.name,
                              'currency_id': currency_id,
                     }
                    purchase = purchase_order.create(p_vals)
            purchase.button_confirm()
            for picking_id in purchase.picking_ids:
                if picking_id.state ==  'draft':
                    picking_id.action_confirm()
                if picking_id.state ==  'waiting':     
                    picking_id.force_assign()
                if picking_id.state ==  'assigned':     
                    pick_imd_data =picking_id.do_new_transfer()
                    if pick_imd_data.get('res_id'):
                        stock_imd_transfer_obj = self.env['stock.immediate.transfer'].browse(pick_imd_data.get('res_id'))    
                        stock_imd_transfer_obj.process()    
                        purchase_list.append(purchase.id)
        return True
