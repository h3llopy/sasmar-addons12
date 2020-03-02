from odoo import fields, models

class resCompany(models.Model):

    _inherit = "res.company"

    intercompany_user_id = fields.Many2one('res.users',string="Intercompnay User")
