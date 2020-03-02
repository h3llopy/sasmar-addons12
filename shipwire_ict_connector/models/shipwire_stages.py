from odoo import models,fields,api
   
class shipwire_stages(models.Model):
    
    _name="shipwire.stages"
    
    name = fields.Char("Name",required=True)
    code = fields.Char("Code",required=True,copy=False)
    
    create_ict = fields.Boolean("Create ICT",help="Create ICT record when this stage is reached from information of shipwire order stage")
    
    _sql_constraints = [('stage_code_uniq', 'unique(code)', 'Shipwire stage code must be unique')]
    