from openerp import fields, models,api
import string

class process_log(models.Model):

    _name = "process.log"
    
    name = fields.Char(string="Name")
    log_date = fields.Datetime(string="Log Date")
    process = fields.Selection([('sale','Sale'),('product','Product'),('stock','Stock')],string="Application")
    operation = fields.Selection([('import','Import'),('export','Export')],string="Operation")
    result = fields.Char(string="Result")
    log_line_ids = fields.One2many('process.log.line','log_id')
    
class process_log_line(models.Model):

    _name = "process.log.line"
    _rec_name = "log_id"
    
    log_type = fields.Selection([('info','Info'),('error','Error')],string="Log Type")
    action = fields.Selection([('skip','Skip and Proceed'),('terminate','Terminate Process'),('ignore','Logged and Ignore'),('processed','Processed')],string="Action")
    log_id = fields.Many2one('process.log',string="Process Log")
    message = fields.Text(string="Message")
    request = fields.Char(string="Request")
    response = fields.Text(string="Response")
    