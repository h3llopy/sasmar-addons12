from odoo import models,fields,api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
class intercompany_trasfer(models.Model):
    
    _name="inter.company.transfer.ept"
    _inherit = ['mail.thread']
    _order = 'create_date desc, id desc'
    
    
    def _get_default_team(self):
        return self.env['crm.team']._get_default_team_id()
    
    name = fields.Char('Name')
    
    source_warehouse_id = fields.Many2one('stock.warehouse',string='From Warehouse',required=True)
    source_company_id = fields.Many2one(related='source_warehouse_id.company_id',string="Source Company")
    
    crm_team_id = fields.Many2one('crm.team',string="Sales Team",default=_get_default_team)
    
    destination_warehouse_id = fields.Many2one('stock.warehouse',string='To Warehouse',required=True)
    destination_company_id = fields.Many2one(related='destination_warehouse_id.company_id',string="Destination Company")
    
    
    currency_id = fields.Many2one('res.currency',related="price_list_id.currency_id",string="Currency",required=True)
    price_list_id = fields.Many2one('product.pricelist',string="Price List")

    line_ids = fields.One2many('inter.company.transfer.line','transfer_id',string="Transfer Lines",copy=True)
    log_line_ids = fields.One2many('ict.process.log.line','transfer_id',string="Log Lines",copy=False)
    
    state = fields.Selection([('draft', 'Draft'), ('processed', 'Processed'),('cancel', 'Cancelled')], string='State', required=True, readonly=True, copy=False, default='draft')
    
    
    
    sale_order_id = fields.Many2one('sale.order',string="Sale Order",copy=False)
    purchase_order_id = fields.Many2one('purchase.order',string="Purchase Order",copy=False)
    
    customer_invoice_id = fields.Many2one('account.invoice',string="Invoice",copy=False)
    vendor_bill_id = fields.Many2one('account.invoice',string="Bill",copy=False)
    
    processed_date = fields.Datetime("Processed Date",copy=False)
    
    message = fields.Char("Message",copy=False)
    
    delivery_order_id = fields.Many2one('stock.picking',string="Delivery Order")
    incoming_shipment_id = fields.Many2one('stock.picking',string="Incoming Shipment")
    revesrse_ict_ids = fields.One2many('reverse.inter.company.transfer.ept','ict_id',string="Reverse ICT")


    _sql_constraints = [('src_dest_company_uniq', 'CHECK(source_warehouse_id!=destination_warehouse_id)', 'Source Warehouse and Destination warehouse must be different!')]
    

    @api.model
    def create(self, vals):
        res = super(intercompany_trasfer,self).create(vals)
        res.write({'name':self.env.ref('ICT_ept_v9.ir_sequence_intercompany_transaction')._next()})
        return res

    @api.onchange('source_warehouse_id')
    def source_warehouse_id_onchange(self):
        #self.destination_warehouse_id = False
        if not self.source_warehouse_id:
            self.price_list_id = False
            self.crm_team_id = False
            self.destination_warehouse_id = False
            return
        #self.currency_id  = self.source_company_id.currency_id
        return {
            'domain': {
                'destination_warehouse_id': [('company_id', '!=',self.source_company_id.id)]
            }
        }
          
    @api.onchange('destination_warehouse_id')
    def onchange_destination_warehouse_id(self):
        if not self.destination_warehouse_id:
            self.price_list_id = False
            self.crm_team_id = False
            return
        #print self.destination_warehouse_id.company_id.partner_id.property_product_pricelist
        #self = self.with_context({'force_company':self.source_company_id.id})
        self.price_list_id  = self.destination_company_id.partner_id.with_context({'force_company':self.source_company_id.id}).property_product_pricelist
        self.crm_team_id = self.destination_company_id.partner_id.with_context({'force_company':self.source_company_id.id}).team_id
        #self.currency_id_onchange()
        return
        
        
    @api.multi
    def action_cancel(self):
        self.write({
            'state':'cancel',
            'message' : 'ICT has been cancelled by %s'%(self.env.user.name)
            })
    
    
    @api.multi  
    def open_attached_sale_order(self):
        return {
            'name': _('Sale Order'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain':[('id','=',self.sale_order_id.id)]
        }
    
    @api.multi
    def open_attached_purchase_order(self):
        return {
            'name': _('Purchase Order'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'domain':[('id','=',self.purchase_order_id.id)]
        }
        
    @api.multi
    def open_attached_reverse_ict(self):
        return {
            'name': _('Reverse ICT'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'reverse.inter.company.transfer.ept',
            'domain':[('id','in',self.revesrse_ict_ids.ids)]
        }
    
    @api.multi
    def open_attached_invoice(self):
        tree_id = self.env.ref('account.invoice_tree').id
        form_id = self.env.ref('account.invoice_form').id
        return {
            'name': _('Customer Invocie'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'views':[(tree_id, 'tree'),(form_id, 'form')],
            'domain':[('id','=',self.customer_invoice_id.id)]
        }
        
    
    @api.multi
    def open_attached_bill(self):
        tree_id = self.env.ref('account.invoice_supplier_tree').id
        form_id = self.env.ref('account.invoice_supplier_form').id
        return {
            'name': _('Vendor Bill'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'views':[(tree_id, 'tree'),(form_id, 'form')],
            'domain':[('id','=',self.vendor_bill_id.id)]
        }
        
    @api.multi
    def create_reverse_ict(self):
        created_reverse_ids = []
        reverse_ict_line_obj = self.env['reverse.ict.line.ept']
        for line in self.line_ids:
            if line.product_id.type == 'product':
                created_reverse_ids.append(reverse_ict_line_obj.create({
                    'product_id':line.product_id.id,
                    'quantity':line.quantity or 1,
                    'price' : line.price
                    }).id)

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'reverse.ict.ept',
            'view_type': 'form',
            'view_mode': 'form',
            'context' : {'default_ict_id':self.id,
                        'default_reverse_line_ids':[(6,0,created_reverse_ids)],
#                         'default_destination_warehouse':self.warehouse_id.id,
                           },
            'target': 'new',
        }
    
    @api.multi
    def _auto_create_sale_order(self):
         
        sale_obj = self.env['sale.order']
        sale_line_obj = self.env['sale.order.line']
        res = []
        
        for record in self:
            
            source_company = record.source_company_id
            source_warehouse_id = record.source_warehouse_id
            
            intercompany_user = source_company.intercompany_user_id.id or False
            partner_id = record.destination_company_id.sudo(intercompany_user).partner_id
            sale_order_vals = sale_obj.sudo(intercompany_user).new({'partner_id':partner_id.id,'company_id':source_company.id,'warehouse_id':source_warehouse_id.id,'pricelist_id':self.price_list_id.id})
        #sale_order_vals.company_id = source_company
        
            sale_order_vals.sudo(intercompany_user).onchange_partner_id()
        
            sale_order_vals.warehouse_id = source_warehouse_id
            sale_order_vals.sudo(intercompany_user)._onchange_warehouse_id()
        
            sale_order_vals.fiscal_position_id  = partner_id.sudo(intercompany_user).property_account_position_id.id
       
            sale_order_vals.pricelist_id = self.price_list_id.id
            if record.crm_team_id:
                sale_order_vals.team_id = record.crm_team_id.id
           
                sale_order_vals = sale_order_vals.sudo(intercompany_user)
       
            sale_order = sale_obj.sudo(intercompany_user).create(sale_order_vals._convert_to_write(sale_order_vals._cache))
        
            so_lines_vals = []
        
            for line in record.line_ids:
        
                so_line_vals = sale_line_obj.sudo(intercompany_user).new({'order_id':sale_order.id,'product_id':line.product_id})
        
                so_line_vals.sudo(intercompany_user).product_id_change()
        
                so_line_vals.sudo(intercompany_user).product_uom_qty = line.quantity
        
                so_line_vals.price_unit = line.price
                so_line_vals = so_line_vals.sudo(intercompany_user)._convert_to_write(so_line_vals._cache)
        
                so_lines_vals.append((0,0,so_line_vals))
        
            sale_order.sudo(intercompany_user).write({'order_line':so_lines_vals})
        
            record.write({'sale_order_id':sale_order.id})
            res.append(sale_order)
        
        
        return res        
    
    @api.multi
    def _auto_create_purchase_order(self):
       
        purchase_obj = self.env['purchase.order']
        purchase_line_obj = self.env['purchase.order.line']
        res = []
        
        destination_company = self.destination_company_id
        intercompany_user = destination_company.intercompany_user_id.id or False
        
        for record in self:
            
            purchase_order_vals = purchase_obj.sudo(intercompany_user).new({'currency_id':self.currency_id.id,'partner_id':record.source_warehouse_id.company_id.partner_id.id,'company_id':destination_company.id})
            purchase_order_vals.sudo(intercompany_user).onchange_partner_id()
            purchase_order_vals.currency_id = self.currency_id.id
            purchase_order_vals.picking_type_id = self.destination_warehouse_id.in_type_id
            purchase_order = purchase_obj.sudo(intercompany_user).create(purchase_order_vals.sudo(intercompany_user)._convert_to_write(purchase_order_vals._cache))
            po_lines_vals = []
            for line in record.line_ids:
                po_line_vals = purchase_line_obj.sudo(intercompany_user).new({'order_id':purchase_order.id,'product_id':line.product_id,'currency_id':self.currency_id})
                po_line_vals.sudo(intercompany_user).onchange_product_id()
                po_line_vals.product_qty = line.quantity
                po_line_vals.price_unit = line.price 
                po_line_vals.product_uom = line.product_id.uom_id
                po_line_vals = po_line_vals.sudo(intercompany_user)._convert_to_write(po_line_vals._cache)
                po_lines_vals.append((0,0,po_line_vals))
            purchase_order.sudo(intercompany_user).write({'order_line':po_lines_vals})
            record.write({'purchase_order_id':purchase_order.id})
            res.append(purchase_order)
        
        return res
    
    def validate_details(self):
        context = self._context or {}
        for record in self:
            if not record.source_warehouse_id.company_id.intercompany_user_id:
                msg = _('Please specifiy intercompany user for source company')
                if context.get('is_auto_validate',False):
                    record.write({'message':msg})
                    return False
                raise ValidationError(msg)
            
            if not record.destination_warehouse_id.company_id.intercompany_user_id:
                msg = 'Please specifiy intercompany user for destination company'
                if context.get('is_auto_validate',False):
                    record.write({'message':msg})
                    return False
                raise ValidationError(msg)
        return True
    
    @api.onchange('price_list_id')
    def default_price(self):
        for record in self:
            for line in record.line_ids:
                line.default_price()
        return
    
    @api.multi
    def validate_data(self):
        
        context = self._context or {}

        for record in self:
            if not record.with_context(context).validate_details():
                continue

            sale_orders = record._auto_create_sale_order()
            purchase_orders = record._auto_create_purchase_order()
            
            sale_user = record.source_company_id.intercompany_user_id.id
            purchase_user = record.destination_company_id.intercompany_user_id.id
            
            purchase_partner_id = record.source_company_id.partner_id
            
            config_record = record.env.ref('ICT_ept_v9.intercompany_transaction_config_record')
            invoice_obj = record.env['account.invoice']
            
            bypass = record._context.get('force_validate_picking',False)

            if config_record:
                if config_record.auto_confirm_orders or bypass:
                    for sale_order in sale_orders:
                        sale_order.write({'origin':record.name or ''})
                        
                        sale_order.sudo(sale_user).action_confirm()
                        record.write({'delivery_order_id':  sale_order.picking_ids and sale_order.picking_ids[0].id})

                        if bypass:

                            if sale_order.picking_ids:
                                picking = sale_order.picking_ids[0]
                                picking.action_assign()

                                if picking.state in ['assigned']:
                                    validate_id = picking.do_new_transfer()
                                    res_id = validate_id.get('res_id')
                                    obj_stock_immediate_transfer = self.env['stock.immediate.transfer']
                                    transfer_id = obj_stock_immediate_transfer.browse(res_id)
                                    transfer_id.process()

                    for purchase_order in purchase_orders:
                        purchase_order.write({'origin':record.name or ''})

                        purchase_order.sudo(purchase_user).button_confirm()
                        
                        record.write({'incoming_shipment_id':  purchase_order.picking_ids and purchase_order.picking_ids[0].id})

                        if bypass:
                            purchase_order.picking_ids[0].action_assign()
                            validate_id = purchase_order.picking_ids[0].do_new_transfer()
                            res_id = validate_id.get('res_id')
                            obj_stock_immediate_transfer = self.env['stock.immediate.transfer']
                            transfer_id = obj_stock_immediate_transfer.browse(res_id)
                            transfer_id.process()
                            #purchase_order.picking_ids[0].move_lines.action_done()
                        
                if config_record.auto_create_invoices:
                    invoice_id = False
                    
                    for sale_order in sale_orders:
                        #invoice_id = sale_order.sudo(sale_user).action_invoice_create()
                        context = {"active_model": 'sale.order', "active_ids": [sale_order.id], "active_id": sale_order.id,'open_invoices':True}
                        payment = record.env['sale.advance.payment.inv'].sudo(sale_user).create({
                                    'advance_payment_method': 'delivered',
                                })
                        result = payment.with_context(context).sudo(sale_user).create_invoices()
                        result = result.get('res_id',False)
                        invoice_id = record.env['account.invoice'].sudo(sale_user).browse(result)
                        #invoice_id = invoice_obj.sudo(sale_user).browse(invoice_id[0])
                        invoice_id.sudo(sale_user).write({'date_invoice':datetime.today()})
                    record.write({'customer_invoice_id':invoice_id.id})
                    
                    bill_id = False
                    for purchase_order in purchase_orders:
                        context = {'default_type': 'in_invoice',
                                    'type': 'in_invoice', 
                                    'journal_type': 'purchase', 
                                    'default_purchase_id': purchase_order.id
                                }
                        
                        values = {
                            'company_id': record.destination_company_id.id or False,
                            'currency_id':record.currency_id,
                            'partner_id':purchase_partner_id.id,
                            'type': 'in_invoice',
                            'journal_type': 'purchase',
                            'purchase_id': purchase_order.id
                        }
                        
                        vals = invoice_obj.sudo(purchase_user).with_context(context).new(values)
                        vals.purchase_id = purchase_order.id
                        #vals.journal_id = vals._default_journal()
                        vals.sudo(purchase_user).purchase_order_change()
                        vals.sudo(purchase_user)._onchange_partner_id()
                        vals.date_invoice = datetime.today()
                        vals.sudo(purchase_user)._onchange_payment_term_date_invoice()
                        vals.sudo(purchase_user)._onchange_origin()
                        vals.currency_id = record.currency_id
                        vals.journal_id = record.destination_company_id.default_purchase_journal

                        for line in vals.invoice_line_ids:
                            line.quantity = line.purchase_line_id and line.purchase_line_id.product_qty or 0.0
                            line.sudo(purchase_user)._compute_price()
                            
                        bill_id =  record.env['account.invoice'].sudo(purchase_user).with_context({'type':'in_invoice'}).create(vals._convert_to_write(vals._cache))
                    record.write({'vendor_bill_id':bill_id and bill_id.id})
                    
                    if config_record.auto_validate_invoices:
                        invoice_id.sudo(sale_user).invoice_validate()
                        bill_id.sudo(purchase_user).invoice_validate()
                        
            record.write({
                'state':'processed',
                'processed_date':datetime.today(),
                'message':'ICT processed successfully by %s'%(self.env.user.name)
                })
        
class intercompany_trasfer_line(models.Model):
    
    _name = "inter.company.transfer.line"
    
    @api.onchange('product_id','transfer_id.price_list_id')
    def default_price(self):

        for record in self:
            product_id = record.product_id
            if product_id:
                pricelist_id = record.transfer_id.price_list_id
                if pricelist_id:
                    pricelist_obj = self.pool['product.pricelist']
                    record.price = pricelist_id.price_get(product_id.id, record.quantity)[pricelist_id.id]
                    #record.price =  pricelist_id.price_get(product_id.id,record.quantity,partner= record.transfer_id.destination_warehouse_id.company_id.partner_id.id)
                    #return pricelist_id.get_product_price(product_id,record.quantity,record.destination_warehouse_id.company_id.partner_id)
                else:
                    record.price = record.product_id.lst_price
                    #return record.product_id.lst_price
            else:
                record.price = 0.0
            #return 0.0

    product_id = fields.Many2one('product.product','Product',required=True)
    quantity = fields.Float("Quantity",required=True,default=1.0)
    price = fields.Float('Price')
    
    transfer_id = fields.Many2one('inter.company.transfer.ept')
    
