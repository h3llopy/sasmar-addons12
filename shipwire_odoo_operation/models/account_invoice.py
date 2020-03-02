from openerp import fields, models ,api

class account_invoice(models.Model):

    _inherit = "account.invoice"
    
    is_shipwire_invoice = fields.Boolean(string="Shipwire Invoice",copy=False)
    
    
class sale_advance_payment(models.TransientModel):

    _inherit = "sale.advance.payment.inv"


    @api.multi
    def create_invoices(self):
        
        res = super(sale_advance_payment,self).create_invoices()
        
        return res