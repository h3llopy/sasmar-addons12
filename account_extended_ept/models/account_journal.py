# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    active = fields.Boolean(string="Active",  default = True)

