from odoo import models,fields,api

class product_pack(models.Model):

    _inherit="product.pack"
    
    
    @api.model
    def create(self,vals):
        res = super(product_pack,self).create(vals)
        if res.bi_product_template:
          self.env['product.template'].sync_bom_with_product(product_ids=[res.bi_product_template.id])
        return res

    @api.multi
    def write(self,vals):
        res = super(product_pack,self).write(vals)
        for record in self: 
           if record.bi_product_template:
                     self.env['product.template'].sync_bom_with_product(product_ids=[record.bi_product_template.id])
        return res

    @api.multi
    def unlink(self):
      super(product_pack,self).unlink()  
      for record in self:
         product_id = record.bi_product_template
         
         if product_id:
            self.env['product.template'].sync_bom_with_product(product_ids=[product_id.id])

      return True
