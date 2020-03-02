# -*- coding: utf-8 -*-
from odoo import models,fields

class HrExpense(models.Model):
    _inherit  = 'hr.expense'
    
    product_id = fields.Many2one('product.product',required=False)        
    ref = fields.Char('Description')
