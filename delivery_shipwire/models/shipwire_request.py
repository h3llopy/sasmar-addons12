# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime, timedelta, date
import requests
import json
from requests.auth import HTTPBasicAuth
from odoo.http import request
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class ShipwireRequest():
    ''' Base Class ,Provides API to Connect to Shipwire.'''

    def __init__(self, user, password, shipwire_test_mode=True):
        if shipwire_test_mode:
            self.url = 'https://api.beta.shipwire.com'
        else:
            self.url = 'https://api.shipwire.com'
        self.user = user
        self.password = password


    def ShipwireCheckOrderStatus(self, order):
        '''Check Order Status and relevant document in Shipwire'''
        api = '/api/v3/orders/'
        try:
            order_url = self.url + api + str(order.carrier_tracking_ref)
            status_response = requests.get(order_url, auth=HTTPBasicAuth(str(self.user), str(self.password)))
            r = status_response.json()
            status = r['resource']['status']
            items_url = r['resource']['items']['resourceLocation']
            items_response2 = requests.get(items_url, auth=HTTPBasicAuth(str(self.user), str(self.password)))
            items = items_response2.json()

            holds_url = r['resource']['holds']['resourceLocation']
            holds_response2 = requests.get(holds_url, auth=HTTPBasicAuth(str(self.user), str(self.password)))
            holds = holds_response2.json()
            holds_url = r['resource']['holds']['resourceLocation']
            holds_response2 = requests.get(holds_url, auth=HTTPBasicAuth(str(self.user), str(self.password)))
            holds = holds_response2.json()

            returns_url = r['resource']['returns']['resourceLocation']
            returns_response2 = requests.get(returns_url, auth=HTTPBasicAuth(str(self.user), str(self.password)))
            returns = returns_response2.json()
            return {'status' : status, 'items' : items, 'holds' : holds, 'returns' : returns}
        except Exception as e:
            _logger.error('Error in Request Process for Shipwire Order(%s) ' % order.carrier_tracking_ref)
            _logger.error('Error message :%s' % e)
            return {'error_message': e}

    def ShipwireProductIDsSync(self):
        '''Sync Product id from Shipwire Db to Odoo Db based on SKU in shipwire and barcode in Odoo'''
        product_obj = request.env['product.product']
        api = '/api/v3/products?offset=0&limit=200'
        stock_url = self.url + api
        res = False
        try:
            stock_response = requests.get(stock_url, auth=HTTPBasicAuth(str(self.user), str(self.password)))
            r = stock_response.json()
            items = r['resource']['items']
            for item in items:
                sku = item['resource']['sku']
                shipwireproduct_id = item['resource']['id']
                try:
                    synced_product_id = product_obj.search([('carrier_tracking_ref', '=', shipwireproduct_id)])
                    product_id = product_obj.search([('barcode', '=', sku)])
                    if not synced_product_id and product_id:
                        res = product_id.write({'carrier_tracking_ref':shipwireproduct_id})
                except Exception as e:
                    _logger.error("Error in Product Synchronization With Shipwire,For Item %s " % sku)
                    _logger.error('Error message :%s' % e)
                    return {'error_message': e}
            return res
        except Exception as e:
            _logger.error("Error in Product Synchronization With Shipwire ")
            _logger.error('Error message :%s' % e)
            return {'error_message': e}

    def ShipwireProductStockSync(self):
        '''Sync Product id from Shipwire Db to Odoo Db based on SKU in shipwire and barcode in Odoo'''
        product_obj = request.env['product.product']
        quant_obj =request.env['stock.quant']
        sync_loc_obj =request.env['odoo.shipwire.location']
        company_obj = request.env['res.company']
        api = '/api/v3/stock?offset=0&limit=1000'
        stock_url = self.url + api
        res = False
        stock_response = requests.get(stock_url, auth=HTTPBasicAuth(str(self.user), str(self.password)))
        r = stock_response.json()
        items = r['resource']['items']
        syched_product_ids = product_obj.search([('carrier_tracking_ref', '!=', False)])
        for item in items:
            sku = item['resource']['sku']
            shipwireproduct_id = item['resource']['productId']
            shipwirewarehouseId = item['resource']['warehouseId']
            if shipwireproduct_id:
                synced_product_id = product_obj.search([('carrier_tracking_ref', '=', shipwireproduct_id)])
                product_id = product_obj.search([('barcode', '=', sku)])
                sync_id = sync_loc_obj.search([('shipwire_warehouse_id', '=', shipwirewarehouseId)])
                if sync_id.id:
                    location_id= sync_id.location_id
                    quant_ids = quant_obj.search([('location_id', '=', location_id.id),('product_id','=',synced_product_id.id)])
                    if quant_ids:
                        for quant_id in quant_ids:
                            quant_id.with_context(force_unlink=True).unlink()
                        if product_id and synced_product_id:
                            company_id = company_obj.search([('name','=','SASMAR LIMITED')])
                            qty = float(item['resource']['good'])
                            vals = {
                            'location_id':location_id.id,
                            'product_id':product_id[0].id,
                            'qty': qty,
                            'company_id':company_id[0].id
                            }
                            quant_id = quant_obj.create(vals)

    def ShipwireOrderCreate(self , order , moves):
        ''' create order from odoo in shipwire '''
       
        api = '/api/v3/orders'
        product = []
        amount = 0.0
        
        if order.move_lines:
            
            for line in order.move_lines:
                pro = {"sku": line.product_id.barcode , "quantity" :line.product_uom_qty}
                product.append(pro)
        elif moves:
            
            for move in moves:
                amount = move.procurement_id.sale_line_id.order_id.amount_total
                pro = {"sku": move.product_id.barcode , "quantity" :move.product_uom_qty}
                product.append(pro)
        
        try:
            order_vals = {
                        "orderNo": order.origin or order.name,
                        "externalId": order.id,
                        "items": product,
                        "options": {
                            "forceDuplicate": 0,
                            "forceAddress": 0,
                            "note": "notes",
                            #"carrierCode": "ST",
                            #"serviceLevelCode": null',
                            #"warehouseRegion": '',
                        },
                        "shipFrom": {"company": order.company_id.name },
                        "shipTo": {
                            "email": order.partner_id.email or "",
                            "name":order.partner_id.name or "",
                            "company": order.partner_id.parent_id.name or order.partner_id.name or"",
                            "address1": order.partner_id.street or "",
                            "address2": order.partner_id.street2  or "",
                            "address3": "",
                            "city": order.partner_id.city or "",
                            "state": order.partner_id.state_id.code or "",
                            "postalCode": order.partner_id.zip or "",
                            "country": order.partner_id.country_id.code or "",
                            "phone": order.partner_id.phone or "",
                        },
                          "commercialInvoice": {
                                        # Amount for shipping service
                                        "shippingValue": amount,},

                        "packingList": {
                            "message1": {
                                #"body": "This must be where pies go when they die. Enjoy!",
                                "header": "Enjoy this product!"
                            }
                        }
                    }
            
            data = json.dumps(order_vals)
            status_response = requests.post(self.url + api , data = data ,auth=HTTPBasicAuth(str(self.user), str(self.password)))
            r = status_response.json()
            
            return r
        except Exception as e:
            _logger.error("Error in Create Order With Shipwire ")
            _logger.error('Error message :%s' % e)
            return {'error_message': e}

            
