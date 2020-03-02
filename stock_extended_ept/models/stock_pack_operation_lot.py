# -*- coding: utf-8 -*-
from odoo import models,api,fields

class StockPackOperationLot(models.Model):
    _inherit = "stock.pack.operation.lot"
    
    expiry_date =  fields.Date('Expiry Date')
    