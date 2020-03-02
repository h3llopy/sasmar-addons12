from odoo import models,fields,api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class reverse_inter_company_trasfer(models.Model):
    
    _name="reverse.inter.company.transfer.ept"
    
    name = fields.Char('Name')
    
    ict_id = fields.Many2one('inter.company.transfer.ept',string="ICT")
    line_ids = fields.One2many('reverse.inter.company.transfer.line.ept','reverse_ict_id')
    
    reverse_delivery_order_id = fields.Many2one('stock.picking',string="Reverse Delivery Order")
    reverse_incoming_shipment_id = fields.Many2one('stock.picking',string="Reverse Incoming Shipment")
    refund_customer_invoice_id = fields.Many2one('account.invoice',string="Refund Customer Invoice")
    refund_vendor_bill_id = fields.Many2one('account.invoice',string="Refund Vendor Bill")
    state = fields.Selection([('draft', 'Draft'), ('processed', 'Processed'),('cancel', 'Cancelled')], string='State', required=True, readonly=True, copy=False, default='draft')
    
    @api.multi
    def action_cancel(self):
        self.write({
            'state':'cancel'
            })
        
    @api.model
    def create(self, vals):
        res = super(reverse_inter_company_trasfer,self).create(vals)
        res.write({'name':self.env.ref('ICT_ept_v9.ir_sequence_reverse_intercompany_transaction')._next()})
        return res
    
    @api.multi
    def validate_pickings(self):
        for record in self:
            delivery_order = record.reverse_delivery_order_id
            if delivery_order and delivery_order.state not in ['cancel','done']:
                if delivery_order.state == 'draft':
                    delivery_order.action_confirm()
                delivery_order.action_assign()
                if delivery_order.state == 'assigned':
                    validate_id = delivery_order.do_new_transfer()
                    res_id = validate_id.get('res_id')
                    obj_stock_immediate_transfer = self.env['stock.immediate.transfer']
                    transfer_id = obj_stock_immediate_transfer.browse(res_id)
                    transfer_id.process()

            shipment = record.reverse_incoming_shipment_id
            if shipment and shipment.state not in ['cancel','done']:
                if shipment.state == 'draft':
                    shipment.action_confirm()
                shipment.action_assign()
                if shipment.state == 'assigned':
                    validate_id = shipment.do_new_transfer()
                    res_id = validate_id.get('res_id')
                    obj_stock_immediate_transfer = self.env['stock.immediate.transfer']
                    transfer_id = obj_stock_immediate_transfer.browse(res_id)
                    transfer_id.process()


    @api.multi
    def process_reverse_ict(self):
        
        stock_return_picking = self.env['stock.return.picking']
        stock_move_obj = self.env['stock.move']

        picking_to_stock = []
        picking = self.ict_id.delivery_order_id
        
        for line in self.line_ids:
            for move_id in stock_move_obj.search([('picking_id','=',picking.id),('product_id','=',line.product_id.id),('state','=','done')]):
                line_tmp = (0,0,{'product_id': move_id.product_id.id, 'move_id': move_id.id, 'quantity': line.quantity})
                picking_to_stock.append(line_tmp)
         
        defautl_vals = stock_return_picking.with_context({'active_id':picking.id}).default_get(['move_dest_exists','original_location_id','parent_location_id','location_id','product_return_moves'])
        defautl_vals.update({'product_return_moves':picking_to_stock})
        return_picking = stock_return_picking.create(defautl_vals)
        tmp = return_picking.with_context({'active_id':picking.id}).create_returns()
        stock_picking = self.env['stock.picking'].browse(tmp.get('res_id'))
         
        if stock_picking:
            self.write({'reverse_delivery_order_id':stock_picking.id})
        
        
        incoming_picking_to_stock = []
        incoming_picking = self.ict_id.incoming_shipment_id
        
        for line in self.line_ids:
            for move_id in stock_move_obj.search([('picking_id','=',incoming_picking.id),('product_id','=',line.product_id.id),('state','=','done')]):
                line_tmp = (0,0,{'product_id': move_id.product_id.id, 'move_id': move_id.id, 'quantity': line.quantity})
                incoming_picking_to_stock.append(line_tmp)
         
        defautl_incoming_vals = stock_return_picking.with_context({'active_id':incoming_picking.id}).default_get(['move_dest_exists','original_location_id','parent_location_id','location_id','product_return_moves'])
        defautl_incoming_vals.update({'product_return_moves':incoming_picking_to_stock})
        return_incoming_picking = stock_return_picking.with_context({'active_ids':False}).create(defautl_incoming_vals)
        tmp = return_incoming_picking.with_context({'active_id':incoming_picking.id}).create_returns()
        stock_picking = self.env['stock.picking'].browse(tmp.get('res_id'))
        
        if stock_picking:
            self.write({'reverse_incoming_shipment_id':stock_picking.id})
        
        self.write({'state':'processed'})
        
        return True
    
class reverse_inter_company_trasfer_line(models.Model):
    
    _name="reverse.inter.company.transfer.line.ept"
    
    reverse_ict_id = fields.Many2one('reverse.inter.company.transfer.ept',string="Reverse ICT")
    
    product_id = fields.Many2one('product.product',string="Product")
    quantity = fields.Float("Quantity",default=1)
    price = fields.Float('Price')