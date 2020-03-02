from odoo import models,fields,api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning 
from odoo.exceptions import UserError, ValidationError

import logging

class intercompany_trasfer_line(models.Model):
    
    _inherit = "inter.company.transfer.line"

    stock_move_ids = fields.One2many('stock.move','ict_line_id',string="Stock Moves",copy=False)
    product_id = fields.Many2one('product.product','Product',required=True,domain=[('type','=','product')])
    