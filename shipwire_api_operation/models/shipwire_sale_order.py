from odoo import fields,models,api,_
from odoo.http import request
from requests.auth import HTTPBasicAuth
from odoo.exceptions import Warning
import json
import requests
import logging
from datetime import datetime
_logger = logging.getLogger(__name__)


class shipwire_order(models.Model):
#     _inherit = "stock.picking"
    _inherit = "sale.order"
        
    @api.multi
    def post_order(self):
        
        api = '/api/v3/orders'
        log_obj = self.env['process.log']
        log_line_obj  = self.env['process.log.line']
        items = []
        process_log = False
        
        if not process_log:
            sequence_id=self.env.ref('shipwire_odoo_operation.shipwire_process_log_seq').ids
            if sequence_id:
                record_name=self.env['ir.sequence'].get_id(sequence_id[0])
            else:
                record_name='/'
            
            log_vals ={
                    'name' : record_name,
                'log_date': datetime.now(),
                'process':'sale',
                'operation':'export'
                    }
            log_record = log_obj.create(log_vals)
        
#         if not self.move_lines:
        if not self.order_line:
            not_found_msg="Order Line not found for Order %s "%(self.name)
            log_line_vals = {
                    'log_type': 'error',
                    'action' : 'terminate',
                    'log_id': log_record.id,
                    'message' : not_found_msg
                    }
            log_line_obj.create(log_line_vals)
            return False
                    
        for line in self.order_line:
            if line.product_id.shipwire_product_id == 0:
                not_found_msg="Product %s is not synced with Shipwire."%(self.name)
                log_line_vals = {
                    'log_type': 'error',
                    'action' : 'skip',
                    'log_id': log_record.id,
                    'message' : not_found_msg
                    }
                log_line_obj.create(log_line_vals)
                continue
            item = {
                "sku": line.product_id.barcode , 
                "quantity" :line.product_uom_qty,
                }
            items.append(item)
        
        if not items:
            not_found_msg="There are no order lines to export in  Order %s "%(self.name)
            log_line_vals = {
                    'log_type': 'error',
                    'action' : 'terminate',
                    'log_id': log_record.id,
                    'message' : not_found_msg
                    }
            log_line_obj.create(log_line_vals)
            return False
        try:
            order_vals = {
                        "orderNo": self.name or self.origin,
                        "externalId": self.id,
                        "items": items,
                        "options": {
                            "forceDuplicate": 0,
                            "forceAddress": 0,
                            "note": "notes",
                            #"carrierCode": "ST",
                            #"serviceLevelCode": null',
                            #"warehouseRegion": '',
                        },
                        "shipFrom": {"company": self.company_id.name },
                        "shipTo": {
                            "email": self.partner_shipping_id.email or "",
                            "name":self.partner_shipping_id.name or "",
                            "company": self.partner_shipping_id.parent_id and self.partner_shipping_id.parent_id.name or self.partner_shipping_id.name or "",
                            "address1": self.partner_shipping_id.street or "",
                            "address2": self.partner_shipping_id.street2  or "",
                            "address3": "",
                            "city": self.partner_shipping_id.city or "",
                            "state": self.partner_shipping_id.state_id.code or "",
                            "postalCode": self.partner_shipping_id.zip or "",
                            "country": self.partner_shipping_id.country_id.code or "",
                            "phone": self.partner_shipping_id.phone or "",
                        },
                          "commercialInvoice": {
                                        # Amount for shipping service
                                        "shippingValue": self.amount_total},

                        "packingList": {
                            "message1": {
                                #"body": "This must be where pies go when they die. Enjoy!",
                                "header": "Enjoy this product!"
                            }
                        }
                    }
            data = json.dumps(order_vals)
            instance = self.env['shipwire.instance'].search([],limit=1)
            
            if not instance:
                msg="Instance NOT FOUND "
                log_line_vals = {
                    'log_type': 'error',
                    'action' : 'terminate',
                    'log_id': log_record.id,
                    'message' : msg
                    }
                log_line_obj.create(log_line_vals)
            
            response = instance.send_post_request(instance,api,data)
            if not response:
                return False
            res = response.json()
            
            if not res.get('errors') :
                if res.get('resource',{}).get('items',False):
                    order_id = res ['resource']['items'][0]['resource']['id']
                msg="Shipwire Order Created with External ID %s" % (order_id)
                log_line_vals = {
                'log_type': 'info',
                'action' : 'processed',
                'log_id': log_record.id,
                'message' : msg or False,
                'response' : res
                }
                log_line_obj.create(log_line_vals)
            else:
                if res.get('errors'):
                    msg= res['errors'][0]['message']
                log_line_vals = {
                    'log_type': 'error',
                    'action' : 'terminate',
                    'log_id': log_record.id,
                    'message' : msg or False,
                    'response' : res
                    }
                log_line_obj.create(log_line_vals)
                
            return res
        except Exception as e:
            _logger.error('Error while export the Order to Shipwire :%s' % e)
            return {'error_message': e}
        
        
    @api.model
    def auto_post_order(self):
        """
        Cron Method for Exporting Sale Orders to Shipwire.
        First it will search for the sale order records which has 'shipwire_id' = 0 and is_shipwire = True.
        It will search for the shipment which is not in 'draft','cancel' and 'done' state and It will execute post_order() for 
        that picking.

        """
        sale_order_obj = self.env['sale.order']
        picking_obj = self.env['stock.picking']
        log_obj = self.env['process.log']
        log_line_obj  = self.env['process.log.line']
        domain = [('shipwire_id','=',False),('is_shipwire','=',True),('state','in',['sale','done'])]
        orders_to_export = sale_order_obj.search(domain)
        sequence_id=self.env.ref('shipwire_odoo_operation.shipwire_process_log_seq').ids
        if sequence_id:
            record_name=self.env['ir.sequence'].get_id(sequence_id[0])
        else:
            record_name='/'
        log_vals ={
            'name' : record_name,
            'log_date': datetime.now(),
            'process':'sale',
            'operation':'export'
                }
        log_record = log_obj.create(log_vals)
        
        if not orders_to_export:
            msg = "Currently there are no orders to export on shipwire"
            log_line_vals = {
                        'log_type': 'error',
                        'action' : 'skip',
                        'log_id': log_record.id or False,
                        'message' : msg or False,
                        }
            log_line_obj.create(log_line_vals)
            return
                    
        for order in orders_to_export:
            if order.picking_ids:
                picking = picking_obj.search([('id','in',order.picking_ids.ids),('state','not in',['draft','cancel','done'])],limit=1)
                if not picking:
                    msg = "Picking not found for Order %s and Order hasn't exported to Shipwire"%(self.name)
                    log_line_vals = {
                        'log_type': 'error',
                        'action' : 'skip',
                        'log_id': log_record.id or False,
                        'message' : msg or False,
                        }
                    log_line_obj.create(log_line_vals)
                    continue
#                 resource = picking[0].post_order()
                resource = order.post_order()
                if not resource:
                    continue
                if not resource.get('errors'):
                    if resource.get('resource',{}).get('items',False):
                        order_id = resource ['resource']['items'][0]['resource']['id']
                        picking.write({'shipwire_id':order_id})
                        order.write({'shipwire_id':order_id})
                else:
                    msg = "Order %s is not Exported to Shipwire"%(self.name)
                    log_line_vals = {
                        'log_type': 'error',
                        'action' : 'skip',
                        'log_id': log_record.id,
                        'message' : msg or False,
                        'response' : resource
                        }
                    log_line_obj.create(log_line_vals)
            msg="Shipwire Order Created with External ID %s" % (order_id)
            log_line_vals = {
            'log_type': 'info',
            'action' : 'processed',
            'log_id': log_record.id,
            'message' : msg or False,
            }
            log_line_obj.create(log_line_vals)

                    
        return True
    
    @api.one
    def post_single_order(self):
        
        if not self.is_shipwire:
            return False
        resource = self.post_order()
        if not resource:
            return False
        if not resource.get('errors'):
            order_id = resource ['resource']['items'][0]['resource']['id']
            picking = self.env['stock.picking'].search([('id','in',self.picking_ids.ids),('state','not in',['draft','cancel','done'])],limit=1)
            if picking:
                picking.write({'shipwire_id':order_id})
            self.write({'shipwire_id':order_id})
        return True
    
    @api.multi
    def action_cancel(self):
        
        res = super(shipwire_order,self).action_cancel()
        if self.is_shipwire:
            if self.shipwire_id:
                api = '/api/v3/orders/%s/cancel' % self.shipwire_id
            else :
                api = '/api/v3/orders/E%s/cancel' % self.id  
            vals ={}
            data = json.dumps(vals)
            instance = self.env['shipwire.instance'].search([],limit=1)
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
                'process':'sale',
                'operation':'export'
                }
            log_record = log_obj.create(log_vals)
            if not instance:
                msg="Instance NOT FOUND while Cancel the Order"  
                log_line_vals = {
                    'log_type': 'error',
                    'action' : 'terminate',
                    'log_id': log_record.id,
                    'message' : msg
                    }
                log_line_obj.create(log_line_vals)
            response = instance.send_post_request(instance,api,data)
            if not response:
                return res
            if response.status_code == 200:
                msg="Order %s canceled on Shipwire" % (self.name)
                log_line_vals = {
                    'log_type': 'info',
                    'action' : 'processed',
                    'log_id': log_record.id,
                    'message' : msg,
                    'response' : response.json(),
                    }
                log_line_obj.create(log_line_vals)
        return res
    
    @api.model
    def sync_order(self):
        
        sale_order_obj = self.env['sale.order']
        log_obj = self.env['process.log']
        log_line_obj  = self.env['process.log.line']
        domain = [('shipwire_id','=',False),('is_shipwire','=',True),('state','in',['sale','done'])]
        orders_to_sync = sale_order_obj.search(domain)
        
        sequence_id=self.env.ref('shipwire_odoo_operation.shipwire_process_log_seq').ids
        if sequence_id:
            record_name=self.env['ir.sequence'].get_id(sequence_id[0])
        else:
            record_name='/'
        log_vals ={
            'name' : record_name,
            'log_date': datetime.now(),
            'process':'sale',
            'operation':'export'
                }
        log_record = log_obj.create(log_vals)
        
        if not self.env['shipwire.instance'].search([],limit=1):
            not_found_msg="Instance NOT FOUND while Syncing Orders"
            log_line_vals = {
                    'log_type': 'error',
                    'action' : 'terminate',
                    'log_id': log_record.id,
                    'message' : not_found_msg
                    }
            log_line_obj.create(log_line_vals)
            return False
        
        instance = self.env['shipwire.instance'].search([],limit=1)
        
        for order in orders_to_sync:
            api = 'api/v3/orders/E%s' % (order.id)
            res = instance.send_get_request(api)
            if not res:
                continue
            if res.get('resource',{}).get('id',False):
                order_id = res['resource']['id']
                order.write({'shipwire_id':order_id})
                picking = self.env['stock.picking'].search([('id','in',order.picking_ids.ids),('state','not in',['draft','cancel','done'])],limit=1)
                if picking:
                    picking.write({'shipwire_id':order_id})
                msg="Shipwire Order Synced with Shipwire ID %s" % (order_id)
                log_line_vals = {
                'log_type': 'info',
                'action' : 'processed',
                'log_id': log_record.id,
                'message' : msg or False,
                }
                log_line_obj.create(log_line_vals)
