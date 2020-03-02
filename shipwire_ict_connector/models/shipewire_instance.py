from odoo import fields, models

class shipwire_instance(models.Model):

    _inherit = 'shipwire.instance'

    last_do_sync_date = fields.Datetime("Last DO Sync Date",copy=False)
    last_return_sync_date = fields.Datetime("Last Return Sync Date",copy=False)

    