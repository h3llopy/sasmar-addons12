from odoo import fields,models,api,_
from odoo.http import request
from requests.auth import HTTPBasicAuth
from odoo.exceptions import Warning
from datetime import datetime
import json
import requests

class shipwire_instance(models.Model):
    _name="shipwire.instance"
    
    name = fields.Char(string="Instance Name")
    user = fields.Char(string="User")
    password = fields.Char(string="Password")
    url = fields.Char("Url",default="https://api.shipwire.com")
    connected = fields.Boolean()
    api_limit = fields.Integer(string="API Limit",default=20)
    export_to_shipwire = fields.Boolean(string="Auto Export Sale Order")
    shipwire_cost_pricelist = fields.Many2one('product.pricelist',string = "Cost Pricelist")
    shipwire_wholesaleValue_pricelist = fields.Many2one('product.pricelist',string = "Wholesale Pricelist")
    shipwire_retailValue_pricelist = fields.Many2one('product.pricelist',string = "Retail pricelist")
    
    
    

    @api.multi
    def unlink(self):
        raise Warning(_("You can not delete Shipwire Instance"))
        
    @api.model
    def get_obj(self):
        instance = self.search([],limit=1)
        if instance:
            return instance
        else:
            raise Warning(_("User name or Password is required"))

    @api.multi
    def test_connection(self):
        self = self.get_obj()
        res = requests.get(self.url+"/api/v3/products", auth=HTTPBasicAuth(str(self.user), str(self.password)))
        if res.status_code == 200:
            raise Warning(_("Service Working Well"))
        else:
            raise Warning(_(res.json()['message']))
        
    @api.multi
    def live_connection(self):
        self = self.get_obj()
        res = requests.get(self.url+"/api/v3/products", auth=HTTPBasicAuth(str(self.user), str(self.password)))
        if res.status_code != 200:
            raise Warning(_(res.json()['message']))
        
    @api.multi
    def send_get_request_with_all_records(self,api,paramters={}):
        temp = {'items':[]}
        response = self.send_get_request(api,paramters)
        next_request= False
        if response : 
            next_request = response.get('resource',{}).get('next',False)
            temp['items'] = response.get('resource',{}).get('items',[])
        while next_request:
            response = self.direct_get_request(next_request)
            next_request = response.get('resource',{}).get('next',False)
            
            temp['items'] = temp['items'] + response.get('resource',{}).get('items',[])
        
        temp.update({'total':len(temp['items'])})
        
        return temp

    @api.multi
    def direct_get_request(self,url):
        res = requests.get(url, auth=HTTPBasicAuth(str(self.user), str(self.password)))
        if res.status_code == 200:
            return json.loads(res.content)
        else:
            raise Warning(_(res.content))

    @api.multi
    def send_get_request(self,api,paramters={}):
        
        parm_str = ""
        url = "%s/%s"%(self.url,api)
        
        for key in paramters:
            if paramters.get('key'):
                parm_str = parm_str + "%s=%s&"%(key,paramters.get('key'))
        if parm_str:
            url = "%s?%s"%(url,parm_str)

        
        res = requests.get(url, auth=HTTPBasicAuth(str(self.user), str(self.password)))
        if res.status_code == 200:
            return json.loads(res.content)
        else:
            log_obj = self.env['process.log']
            log_line_obj  = self.env['process.log.line']
            sequence_id=self.env.ref('shipwire_odoo_operation.shipwire_process_log_seq').ids
            if sequence_id:
                record_name=self.env['ir.sequence'].get_id(sequence_id[0])
            else:
                record_name='/'
            log_vals ={
                'name' : record_name,
                'log_date': datetime.now(),
                'operation':'import'
                    }
            log_record = log_obj.create(log_vals)
            log_line_vals = {
                        'log_type': 'error',
                        'action' : 'terminate',
                        'log_id': log_record.id,
                        'response' : json.loads(res.content),
                        'request' : url
                        }
            log_line_obj.create(log_line_vals)
            
            return False

    @api.multi
    def send_post_request(self,instance,api,data):
        if not instance:
            instance = self.env['shipwire.instance'].search([],limit=1)
        url = instance.url + api
        res = requests.post(url,data = data , auth=HTTPBasicAuth(str(instance.user), str(instance.password)))
        if res.status_code == 200:
            return res
        else:
            log_obj = self.env['process.log']
            log_line_obj  = self.env['process.log.line']
            sequence_id=self.env.ref('shipwire_odoo_operation.shipwire_process_log_seq').ids
            if sequence_id:
                record_name=self.env['ir.sequence'].get_id(sequence_id[0])
            else:
                record_name='/'
            log_vals ={
                'name' : record_name,
                'log_date': datetime.now(),
                'operation':'export'
                    }
            log_record = log_obj.create(log_vals)
            log_line_vals = {
                        'log_type': 'error',
                        'action' : 'terminate',
                        'log_id': log_record.id,
                        'response' : json.loads(res.content),
                        'request' : url
                        }
            log_line_obj.create(log_line_vals)
            
            return False

        
        