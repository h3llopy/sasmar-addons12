from openerp import fields, models ,api, _
from openerp.http import request
from requests.auth import HTTPBasicAuth
from openerp.exceptions import Warning
import json
import requests
from datetime import datetime


class amazon_prepare_product_wizard(models.TransientModel):
    _name = 'shipwire.product.export.wizard'
    
    
    @api.multi
    def export_product(self):
        
        active_ids=self._context.get('active_ids',[])
        
        api = '/api/v3/products'
        
        if active_ids:
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
                'process':'product',
                'operation':'export'
                    }
            log_record = log_obj.create(log_vals)
            instance = self.env['shipwire.instance'].search([],limit=1)
            
            if not instance:
                not_found_msg="Instance NOT FOUND"
                log_line_vals = {
                        'log_type': 'error',
                        'action' : 'terminate',
                        'log_id': log_record.id,
                        'message' : not_found_msg
                        }
                log_line_obj.create(log_line_vals)
            for product in self.env['product.product'].browse(active_ids):
                if product.shipwire_product_id:
                    msg = "Product %s is already synced" % (product.name)
                    log_line_vals = {
                        'log_type': 'info',
                        'action' : 'skip',
                        'log_id': log_record.id,
                        'message' : msg
                        }
                    log_line_obj.create(log_line_vals)
                    continue
                shipwire_cost_pricelist = instance.shipwire_cost_pricelist
                shipwire_wholesaleValue_pricelist = instance.shipwire_wholesaleValue_pricelist
                shipwire_retailValue_pricelist = instance.shipwire_retailValue_pricelist
                
                product_vals = [
                    {
                        "sku": product.barcode,
                        "externalId": product.id,
                        "classification": "baseProduct",
                        "description": product.description or product.name,
        #                 "hsCode": "010612",
        #                 "htscode": "0063079075",
        #                 "eccn": "123456",
        #                 "countryOfOrigin": "US",
                        "category": "HEALTH_&_PERSONAL_CARE",
                        "batteryConfiguration": "NOBATTERY",
                        "values": {
                            "costValue": shipwire_cost_pricelist and shipwire_cost_pricelist.price_get(product.id,1.0)[shipwire_cost_pricelist.id] or  product.standard_price,
                            "wholesaleValue": shipwire_wholesaleValue_pricelist and shipwire_wholesaleValue_pricelist.price_get(product.id,1.0)[shipwire_wholesaleValue_pricelist.id]
                            or product.lst_price,
                            "retailValue": shipwire_retailValue_pricelist and shipwire_retailValue_pricelist.price_get(product.id,1.0)[shipwire_retailValue_pricelist.id]
                            or product.lst_price,
                            "costCurrency": shipwire_cost_pricelist and shipwire_cost_pricelist.currency_id.name or "USD",
                            "wholesaleCurrency": shipwire_wholesaleValue_pricelist and shipwire_wholesaleValue_pricelist.currency_id.name or "USD",
                            "retailCurrency": shipwire_retailValue_pricelist and shipwire_retailValue_pricelist.currency_id.name or "USD"
                        },
        #                 "alternateNames": [
        #                     {
        #                         "name": "SuperSportsWatch1"
        #                     }
        #                 ],
        #                 "alternateDescriptions": [
        #                     {
        #                         "description": "I am German"
        #                     }
        #                 ],
                        "dimensions": {
                            "length": product.shipwire_length,
                            "width": product.shipwire_width,
                            "height": product.shipwire_height,
                            "weight": product.shipwire_weight
                        },
        #                 "technicalData": {
        #                     "battery": {
        #                         "type": "ALKALINE",
        #                         "batteryWeight": 3,
        #                         "numberOfBatteries": 5,
        #                         "capacity": 6,
        #                         "numberOfCells": 7,
        #                         "capacityUnit": "WATTHOUR"
        #                     }
        #                 },
        #                 "flags": {
        #                     "isPackagedReadyToShip": 0,
        #                     "isFragile": 1,
        #                     "isDangerous": 0,
        #                     "isPerishable": 0,
        #                     "isMedia": 0,
        #                     "isAdult": 1,
        #                     "isLiquid": 0,
        #                     "hasInnerPack": 1,
        #                     "hasMasterCase": 1,
        #                     "hasPallet": 1
        #                 },
        #                 "innerPack": {
        #                     "individualItemsPerCase": 2,
        #                     "externalId": "narp2",
        #                     "sku": "singleInner2",
        #                     "description": "innerdesc",
        #                     "values": {
        #                         "costValue": 1,
        #                         "wholesaleValue": 2,
        #                         "retailValue": 4,
        #                         "costCurrency": "USD",
        #                         "wholesaleCurrency": "USD",
        #                         "retailCurrency": "USD"
        #                     },
        #                     "dimensions": {
        #                         "length": 2,
        #                         "width": 2,
        #                         "height": 2,
        #                         "weight": 2
        #                     },
        #                     "flags": {
        #                         "isPackagedReadyToShip": 0
        #                     }
        #                 },
        #                 "masterCase": {
        #                     "individualItemsPerCase": 10,
        #                     "externalId": "narp3",
        #                     "sku": "singleMaster2",
        #                     "description": "masterdesc",
        #                     "values": {
        #                         "costValue": 1,
        #                         "wholesaleValue": 2,
        #                         "retailValue": 4,
        #                         "costCurrency": "USD",
        #                         "wholesaleCurrency": "USD",
        #                         "retailCurrency": "USD"
        #                     },
        #                     "dimensions": {
        #                         "length": 4,
        #                         "width": 4,
        #                         "height": 4,
        #                         "weight": 4
        #                     },
        #                     "flags": {
        #                         "isPackagedReadyToShip": 0
        #                     }
        #                 },
        #                 "pallet": {
        #                     "individualItemsPerCase": 1000,
        #                     "externalId": "narp4",
        #                     "sku": "singlePallet2",
        #                     "description": "palletdesc",
        #                     "values": {
        #                         "costValue": 1,
        #                         "wholesaleValue": 2,
        #                         "retailValue": 4,
        #                         "costCurrency": "USD",
        #                         "wholesaleCurrency": "USD",
        #                         "retailCurrency": "USD"
        #                     },
        #                     "dimensions": {
        #                         "length": 8,
        #                         "width": 8,
        #                         "height": 8,
        #                         "weight": 8
        #                     },
        #                     "flags": {
        #                         "isPackagedReadyToShip": 0
        #                     }
        #                 }
                    }
                ]
                
                
                data = json.dumps(product_vals)
                response = instance.send_post_request(instance,api,data)
                if not response:
                    continue
                res = response.json()
                
                if res.get('errors',{}):
                    log_line_vals = {
                        'log_type': 'error',
                        'action' : 'skip',
                        'log_id': log_record.id,
                        'request' : product_vals,
                        'response' : res
                        }
                    log_line_obj.create(log_line_vals)
                    continue
                    
                    
                shipwire_id =  res ['resource']['items'][0]['resource']['id']
                
                product.shipwire_product_id = shipwire_id
                msg = "Product with sku %s expored the shipwire and synced with ID %s" % (product.barcode,shipwire_id)
                log_line_vals = {
                        'log_type': 'info',
                        'action' : 'processed',
                        'log_id': log_record.id,
                        'message' : msg,
                        'request' : product_vals,
                        'response' : res
                        }
                log_line_obj.create(log_line_vals)
        return True