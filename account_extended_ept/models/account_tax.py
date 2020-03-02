# -*- coding: utf-8 -*-
from odoo import models,api,fields

class AccountTax(models.Model):
    _inherit = 'account.tax'
    
    # def name_get(self, cr, uid, ids, context=None):
    #     if not ids:
    #         return []
    #     res = []
    #     for record in self.read(cr, uid, ids, ['description','name'], context=context):
    #         name = record['description'] and record['description'] or record['name']
    #         res.append((record['id'],name ))
    #     return res