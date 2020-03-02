# -*- coding: utf-8 -*-
from odoo import models,api,fields

class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"
    
    expiry_date =  fields.Date('Expiry Date')