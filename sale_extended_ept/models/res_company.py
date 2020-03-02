# -*- coding: utf-8 -*-
from openerp import models,api,fields

class ResCompany(models.Model):
    _inherit = "res.company"

    bank_ids = fields.One2many('res.partner.bank', 'company_id', 'Bank Accounts', help='Bank accounts related to this company')

