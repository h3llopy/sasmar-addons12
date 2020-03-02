from odoo import models,fields,api,_
from odoo.exceptions import Warning

class intercompany_trasfer_config(models.Model):
    
    _name="inter.company.transfer.config"
    _rec_name = "sequence_id"
    
    sequence_id = fields.Many2one('ir.sequence','Sequence')
    
    auto_confirm_orders = fields.Boolean('Auto Confirm Orders')
    #auto_confirm_po = fields.Boolean('Auto Confirm PO ?')
    
    auto_create_invoices = fields.Boolean('Auto Create Invoices')
    auto_validate_invoices = fields.Boolean('Auto Validate Invoices')
    
    auto_validate_refunds = fields.Boolean('Auto Validate Refunds')
    
    #auto_create_vendor_bill = fields.Boolean('Auto Create Vendor Bill ?')
    #auto_validate_vendor_bill = fields.Boolean('Auto Validate Vendor Bill ?')
    
    
    @api.multi
    def unlink(self):
        raise Warning(_("You can not delete this record"))