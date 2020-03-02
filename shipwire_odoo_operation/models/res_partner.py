from openerp import fields, models ,api

class res_partner(models.Model):

    _inherit = "res.partner"
    
    is_shipwire_partner = fields.Boolean(string="Shiwire Partner",copy=False)