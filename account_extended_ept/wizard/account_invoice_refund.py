from odoo import fields,models,api

class AccountInvoiceRefund(models.TransientModel):
    _inherit = "account.invoice.refund"

    @api.model
    def _get_reason(self):
        res = super(AccountInvoiceRefund,self)._get_reason()
        if res == '':
            return 'Refund'

    description = fields.Char(string='Reason', required=True, default=_get_reason)