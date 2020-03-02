# -*- coding: utf-8 -*-
from openerp import models,api,fields

class CrmTeam(models.Model):
    _inherit = 'crm.team'
    
    parent_id = fields.Many2one('crm.team', 'Parent Team')
    