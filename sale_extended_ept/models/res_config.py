# -*- coding: utf-8 -*-
from openerp import api, fields, models, _
from openerp.exceptions import UserError

class stock_config_settings(models.TransientModel):
    _inherit = 'res.config.settings'

    user_id = fields.Char("Shipwire UserID")
    pwd = fields.Char("Shipwire Password" , )
    
    



    
    