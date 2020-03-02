from odoo import models,fields,api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning 
from odoo.exceptions import UserError, ValidationError

import logging

class stockPicking(models.Model):

    _inherit = "stock.move"

    ict_line_id = fields.Many2one('inter.company.transfer.line',string="ICT line",copy=False)