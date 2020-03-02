from odoo import models,fields,api
class stock_picking(models.Model):
    _inherit="product.template"
    
    bom_id = fields.Many2one('mrp.bom',"BOM")

    
    @api.model
    def sync_bom_with_product(self,product_ids=[]):

        bom_obj = self.env['mrp.bom']
        bom_line_ids = self.env['mrp.bom.line']

        if not product_ids:
            product_objs=self.sudo().search([('is_pack','=',True)])
        else:
            product_objs=self.sudo().search([('is_pack','=',True),('id','in',product_ids)])
            
        for product in product_objs:
            #product = product.product_tmpl_id
            product_bom = product.bom_id
            if not product_bom:
                #create BOM for for Product 
                bom_obj = self.env['mrp.bom']
                product_bom = bom_obj.create({
                    'product_tmpl_id':product.id,
                    'type':'phantom',
                    'company_id':1
                })

            product_bom.bom_line_ids and product_bom.bom_line_ids.unlink()

            for pack in product.pack_ids:
                bom_line_ids.create({
                    'product_id':pack.product_id.id,
                    'product_qty':pack.qty_uom or 1,
                    'bom_id':product_bom.id
                    })

            product.write({'bom_id':product_bom.id})
        return True
    
