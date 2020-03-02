# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class base_config_settings(models.TransientModel):
    _inherit = 'base.config.settings'
    
    reply_from_email = fields.Char('Reply From Email',help="This email address used to send reply notification email to related partners")
    
    @api.model
    def get_reply_email(self, fields):
        from_email = self.env["ir.config_parameter"].get_param("reply.from.email", default='')
        return {'reply_from_email': from_email or ''}

    @api.multi
    def set_model_ids(self):
        for record in self:
            self.env['ir.config_parameter'].set_param("reply.from.email", record.reply_from_email or '')
