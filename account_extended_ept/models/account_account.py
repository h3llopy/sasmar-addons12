# -*- coding: utf-8 -*-
from odoo import models,api,fields
from odoo.osv import expression

class AccountAccount(models.Model):
    _inherit = "account.account"
    
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        ctx = dict(self._context or {})
        if ctx.get('account'):
            com = ctx.get('account')[0][1]
            company_id = self.env['account.invoice'].browse(com).company_id.id
            args.append(['company_id','=' ,company_id ])
        if name:
            domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&'] + domain
        accounts = self.search(domain + args, limit=limit)
        return accounts.name_get()