from openerp import fields, models,api

class odoo_shipwire_operation(models.TransientModel):

    _name = "odoo.shipwire.operation"
    
    shipwire_instance = fields.Many2many('shipwire.instance','shipwire_operation_instance_rel',string="Shipwire Instance")
    sync_product = fields.Boolean('Sync Product')
    sync_stock = fields.Boolean('Sync Stock')
    export_sale_order = fields.Boolean('Export Order')
    
    @api.model
    def default_get(self, fields):
        res = super(odoo_shipwire_operation,self).default_get(fields)
        if self.env['shipwire.instance'].search([]):
            res.update({'shipwire_instance':[(6,0,self.env['shipwire.instance'].search([])[0].ids)]})
        return res
    
    @api.multi
    def execute(self):
        product_obj = self.env['product.product']
        sale_order_obj = self.env['sale.order']
        if self.sync_product:
            product_obj.sync_product(self.shipwire_instance)
        if self.sync_stock:
            product_obj.sync_product_stock(self.shipwire_instance)
        if self.export_sale_order:
            sale_order_obj.auto_post_order()
            
        return True
    
    
    
    
    