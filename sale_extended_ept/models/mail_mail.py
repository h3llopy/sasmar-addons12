# -*- coding: utf-8 -*-
from openerp import api, fields, models, _

class mail_mail(models.Model):
    _inherit = 'mail.mail'
    
    @api.model
    def create(self, values):
        res = super(mail_mail, self).create(values)
        if values.has_key('fetchmail_server_id'):
            from_email = self.env["ir.config_parameter"].get_param("reply.from.email", default='')
            res.write({'email_from':str(from_email)})
        return res

    @api.model
    def _cron_retry_mail(self):
        mail_mail_ids =self.env['mail.mail'].search([('state', '=', 'exception')])
        for mail_ids in mail_mail_ids:
            mail_ids.mark_outgoing()
            mail_ids.send(auto_commit=False, raise_exception=False)
        return True