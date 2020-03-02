# coding=utf-8
from odoo import fields, models,api

class AccountInvoice(models.Model):

    _inherit = "account.invoice"



    def _get_intercompany_transaction(self):
        for record in self:
            ict = self.env['inter.company.transfer.ept'].search([('customer_invoice_id','=',record.id)],limit=1)
            record.ict_id = ict

    ict_id = fields.Many2one('inter.company.transfer.ept',string="ICT",compute='_get_intercompany_transaction')
    invoice_id = fields.Many2one('account.invoice',related='ict_id.customer_invoice_id')
    bill_id = fields.Many2one('account.invoice',related='ict_id.vendor_bill_id')

   
    