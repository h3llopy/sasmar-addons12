from odoo import models,fields,api
   
class intercompany_trasfer_config(models.Model):
    
    _inherit="inter.company.transfer.config"

    help_string = "Create ICT for each SO while checking shiwpwire status. Mark True if you want to create ICT record for each SO or system will create single ICT record"
    is_ict_per_so = fields.Boolean(string="Create ICT for each SO",help=help_string)

    