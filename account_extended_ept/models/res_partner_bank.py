# -*- coding: utf-8 -*-
from odoo import models,api,fields

class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    company_id = fields.Many2one('res.company', 'Company Bank Account')
    footer = fields.Boolean('Display on Report')
    bank_name = fields.Char('Bank Name', required=True)
    bank_bic = fields.Char('Bank Identifier Code')
    bank_name_t = fields.Char('Bank Name', required=False) 
    
    @api.onchange('bank_id')
    def onchange_bank_id(self):
        if self.bank_id:
            self.bank_name = self.bank_id.name or False
            self.bank_bic = self.bank_id.bic or False