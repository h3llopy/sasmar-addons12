from odoo import models,fields,api
class mrp_bom(models.Model):
    
    _inherit = 'mrp.bom'
    
    @api.multi
    def re_assign_sequence(self):
        context = self._context or {}
        if context.get('re_assign_sequence',True):
            for record in self:
                template_bom = record.product_tmpl_id.bom_id
                if template_bom:
                    bom_ids = self.search([('product_tmpl_id','=',record.product_tmpl_id.id)])
                    sequence = template_bom.sequence
                    for bom in bom_ids:
                        if bom.sequence <= sequence:
                            sequence = bom.sequence - 1
                    template_bom.with_context({'re_assign_sequence':False}).write({'sequence':sequence or -1})

    @api.model
    def create(self,vals):
        res = super(mrp_bom,self).create(vals)
        res.re_assign_sequence()
        return res

    @api.multi
    def write(self,vals):
        res = super(mrp_bom,self).write(vals)
        self.re_assign_sequence()
        return res
