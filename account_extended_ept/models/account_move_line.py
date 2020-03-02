# -*- coding: utf-8 -*-
from odoo import models,api,fields

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.multi
    def unlink(self):
        return super(AccountMoveLine, self).unlink()
        """
        :Viki Why below code deleting the statement_id from moveline ??
        """
        for line in self:
            if line.statement_id !=  False:
                line.statement_id = False
                return True
            else:
                return super(AccountMoveLine, self).unlink()