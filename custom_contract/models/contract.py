 # -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class Contract(models.Model):
    _inherit = 'hr.contract'
    
    superannuation = fields.Float(String = 'Superannuation')
    car_allowance = fields.Float(String = 'Car allowance')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
