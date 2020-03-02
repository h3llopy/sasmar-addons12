# -*- coding: utf-8 -*-
from odoo import fields, models

class HrContract(models.Model):
    _inherit = 'hr.contract'
    
    superannuation = fields.Float(String = 'Superannuation')
    car_allowance = fields.Float(String = 'Car allowance')