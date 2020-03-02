# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResCompany(models.Model):

    _inherit = 'res.company'

    default_sales_journal = fields.Many2one('account.journal',copy=False,string="Default Sales Journal",domain="[('type','=','sale')]")
    default_purchase_journal = fields.Many2one('account.journal', copy=False, string="Default Purchase Journal",domain="[('type','=','purchase')]")

    default_sales_refund_journal = fields.Many2one('account.journal', copy=False, string="Default Sales Refund Journal",domain="[('type','=','sale')]")
    default_purchase_refund_journal = fields.Many2one('account.journal', copy=False, string="Default Purchase Refund Journal",domain="[('type','=','purchase')]")