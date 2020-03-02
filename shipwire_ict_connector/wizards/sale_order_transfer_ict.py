# -*- coding: utf-8 -*-

from openerp import api, fields, models


class SaleToICt(models.TransientModel):
    _name = "sale.order.transfer.ict"
    
    _description = "Create ICT from Sale Order"

    order_id = fields.Many2one('sale.order',"Sale Order",required=True)
    line_ids = fields.One2many("sale.order.transfer.line",'transfer_id',string="Lines",required=True)

    source_warehouse = fields.Many2one('stock.warehouse',required=True,string="Source Warehouse")
    destination_warehouse = fields.Many2one('stock.warehouse',related="order_id.warehouse_id",string="Destination Warehouse")

    @api.multi
    def create_ict(self):

        product_product = self.env['product.product']
        ict_obj = self.env['inter.company.transfer.ept']
        ict_line_obj = self.env['inter.company.transfer.line']

        ict_record = ict_obj.new({
                        'source_warehouse_id':self.source_warehouse.id,
                        'destination_warehouse_id':self.order_id.warehouse_id.id,
                        'line_ids':False
                    })
        ict_record.source_warehouse_id_onchange()
        ict_record.onchange_destination_warehouse_id()
        ict_record = ict_obj.create(ict_record._convert_to_write(ict_record._cache))

        product_lines = []
        for line in self.line_ids:
            ict_line_vals = ict_line_obj.new({
                        'transfer_id':ict_record.id,
                        'product_id':line.product_id.id,
                        'quantity':line.quantity or 1,
                    })
            ict_line_vals.default_price()
            ict_line_vals = ict_line_obj._convert_to_write(ict_line_vals._cache)
            product_lines.append((0,0,ict_line_vals))

        ict_record.write({'line_ids':product_lines})

        self.order_id.write({'ict_id':ict_record.id})
        return ict_record


class SaleToICtLines(models.TransientModel):

    _name = "sale.order.transfer.line"
    
    transfer_id = fields.Many2one("sale.order.transfer.ict",string="Trasfer id")

    product_id = fields.Many2one('product.product',string="Product")
    quantity = fields.Float("Quantity",default=1)

