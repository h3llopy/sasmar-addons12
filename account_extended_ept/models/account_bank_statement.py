# -*- coding: utf-8 -*-
from odoo import models,api,fields

class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"
    
    move_line_ids = fields.One2many('account.move.line', 'statement_id', string='Entry lines')
    account_id = fields.Many2one('account.account', related='journal_id.default_debit_account_id', string='Account', readonly=True, help='used in statement reconciliation domain, but shouldn\'t be used elswhere.')
    
    @api.one
    @api.depends('line_ids', 'balance_start', 'line_ids.amount', 'balance_end_real','move_line_ids')
    def _end_balance(self):
# Base method
        self.total_entry_encoding = sum([line.amount for line in self.line_ids])
        self.balance_end = self.balance_start + self.total_entry_encoding
        self.difference = self.balance_end_real - self.balance_end
# commented for corrections
        statement_balance_start = self.balance_start
        for line in self.move_line_ids:
             if line.debit > 0:
                 if line.account_id.id == \
                         self.journal_id.default_debit_account_id.id:
                     statement_balance_start += line.amount_currency or line.debit
             else:
                 if line.account_id.id == \
                         self.journal_id.default_credit_account_id.id:
                     statement_balance_start += line.amount_currency or (-line.credit)
        self.balance_end = statement_balance_start
        if self.state in ('open'):
             for line in self.line_ids:
                 statement_balance_start += line.amount
                 self.balance_end = statement_balance_start
        
