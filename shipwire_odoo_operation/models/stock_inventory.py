from openerp import fields,models,api,_
from openerp.http import request
from requests.auth import HTTPBasicAuth
from openerp.exceptions import Warning
import json
import requests
from datetime import datetime


class stock_inventory(models.Model):

    _inherit= 'stock.inventory'
    
    is_shipwire = fields.Boolean(string="Is Shipwire",copy=False)