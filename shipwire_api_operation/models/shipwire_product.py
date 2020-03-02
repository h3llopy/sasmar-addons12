from odoo import fields,models,api,_
from odoo.http import request
from requests.auth import HTTPBasicAuth
from odoo.exceptions import Warning
import json
import requests
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


class shipwire_product(models.Model):

    _inherit='product.product'
    
    @api.model
    def sync_product(self,instance=False):
        
        
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
            'operation':'import'
                }
        log_record = log_obj.create(log_vals)
        product_obj = self.env['product.product']
        
        if not instance:
            if not self.env['shipwire.instance'].search([],limit=1):
                not_found_msg="Instance NOT FOUND"
                log_line_vals = {
                        'log_type': 'error',
                        'action' : 'terminate',
                        'log_id': log_record.id,
                        'message' : not_found_msg
                        }
                log_line_obj.create(log_line_vals)
            else:
                instance = self.env['shipwire.instance'].search([],limit=1)
        
        api = 'api/v3/products?offset=0&limit=%s'%(instance.api_limit)
        res = False
        try:
            response = instance.send_get_request(api)
            if not response:
                return False
            res = response
            items = res ['resource']['items']
            for item in items:
                try:
                    sku = item['resource']['sku']
                    shipwire_product_id = item['resource']['id']
                    synced_product_id = product_obj.search([('shipwire_product_id', '=', shipwire_product_id)])
                    product_id = product_obj.search([('barcode', '=', sku)])
                    if not synced_product_id and product_id :
                        product_id.write({'shipwire_product_id':shipwire_product_id})
                        not_found_msg="Shipwire Product synced with ID %s at Product with SKU %s " % (shipwire_product_id,sku)
                        log_line_vals = {
                            'log_type': 'info',
                            'action' : 'processed',
                            'log_id': log_record.id,
                            'message' : not_found_msg
                            }
                        log_line_obj.create(log_line_vals)
                except Exception as e:
                    not_found_msg="%s" % (e)
                    log_line_vals = {
                            'log_type': 'error',
                            'action' : 'terminate',
                            'log_id': log_record.id,
                            'message' : not_found_msg,
                            'response': res or False
                            }
                    log_line_obj.create(log_line_vals)
                    _logger.error("Error in Product Synchronization With Shipwire ")
                    return False
            return True
        except Exception as e:
            not_found_msg="%s" % (e)
            log_line_vals = {
                    'log_type': 'error',
                    'action' : 'terminate',
                    'log_id': log_record.id,
                    'message' : not_found_msg,
                    'response': res or False
                    }
            log_line_obj.create(log_line_vals)
            _logger.error("Error in Product Synchronization With Shipwire ")
            return False
           
            
    @api.model
    def sync_product_stock(self,instance=False):
        
        log_obj = self.env['process.log']
        log_line_obj  = self.env['process.log.line']
        product_obj = self.env['product.product']
        warehouse_obj = self.env['stock.warehouse']
        inventory_obj = self.env['stock.inventory']
        inventory_line_obj = self.env['stock.inventory.line']
        sequence_id=self.env.ref('shipwire_odoo_operation.shipwire_process_log_seq').ids
        if sequence_id:
            record_name=self.env['ir.sequence'].get_id(sequence_id[0])
        else:
            record_name='/'
        log_vals ={
            'name' : record_name,
            'log_date': datetime.now(),
            'process':'stock',
            'operation':'import'
                }
        log_record = log_obj.create(log_vals)
            
        if not instance and not self.env['shipwire.instance'].search([],limit=1):
            not_found_msg="Instance NOT FOUND"
            log_line_vals = {
                    'log_type': 'error',
                    'action' : 'terminate',
                    'log_id': log_record.id,
                    'message' : not_found_msg
                    }
            log_line_obj.create(log_line_vals)
            return False
        
        instance = self.env['shipwire.instance'].search([],limit=1)
        api = 'api/v3/stock?offset=0&limit=%s'%(instance.api_limit)
        response = instance.send_get_request(api)
        if not response:
            return False
        res = response
        items = res['resource']['items']
        warehouse_list=[]
        shipwire_warehouse_list = []
        inventory_warehouse = []
        damage_inventory_warehouse =[]
        temp =[]
        temp1 = []
        
        for invt in inventory_obj.search([('is_shipwire','=',True),('state','in',['confirm'])]):
            invt.action_cancel_inventory()
            inv_msg="Inventory %s Cancelled" % (invt.name)
            log_line_vals = {
                    'log_type': 'info',
                    'action' : 'processed',
                    'log_id': log_record.id,
                    'message' : inv_msg
                    }
            log_line_obj.create(log_line_vals)
        
        for item in items:
            shipwirewarehouseId = item['resource']['warehouseId']
            warehouse = warehouse_obj.search([('shipwire_warehouse_id','=',shipwirewarehouseId)])
            if not warehouse:
                not_found_msg="Warehouse NOT FOUND for shipwire id %s " % (shipwirewarehouseId)
                log_line_vals = {
                    'log_type': 'error',
                    'action' : 'skip',
                    'log_id': log_record.id,
                    'message' : not_found_msg
                    }
                log_line_obj.create(log_line_vals)
                continue
            if shipwirewarehouseId not in shipwire_warehouse_list:
                shipwire_warehouse_list.append(shipwirewarehouseId)
            if warehouse.id not in warehouse_list:
                warehouse_list.append(warehouse.id)
            else :
                continue
            
            if not warehouse.inventory_adjust:
                continue
            
            vals = self.prepare_inventory_dict(warehouse,warehouse.lot_stock_id.id)
            inventory = inventory_obj.create(vals)
            if inventory:
                not_found_msg="Inventory %s Created " % (inventory.name)
                log_line_vals = {
                    'log_type': 'info',
                    'action' : 'skip',
                    'log_id': log_record.id,
                    'message' : not_found_msg
                    }
                log_line_obj.create(log_line_vals)
#                 inventory.prepare_inventory()
    
            temp.append(warehouse)
            temp.append(inventory)
            inventory_warehouse.append(temp)
            temp = []
            
            if not warehouse.damage_inventory:
                continue
            
            damage_vals = self.prepare_inventory_dict(warehouse,warehouse.shipwire_damage_location.id)
            damage_inventory = inventory_obj.create(damage_vals)
            
            if damage_inventory:
                not_found_msg="Damage Inventory %s Created " % (damage_inventory.name)
                log_line_vals = {
                    'log_type': 'info',
                    'action' : 'skip',
                    'log_id': log_record.id,
                    'message' : not_found_msg
                    }
                log_line_obj.create(log_line_vals)
            
            
            temp1.append(warehouse)
            temp1.append(damage_inventory)
            damage_inventory_warehouse.append(temp1)
            temp1 =[]
        
        for item in items:
            
            sku = item['resource']['sku']
            shipwireproduct_id = item['resource']['productId']
            shipwirewarehouseId = item['resource']['warehouseId']
                
            if (shipwireproduct_id or sku) and shipwirewarehouseId:
                synced_product = product_obj.search([('shipwire_product_id', '=', shipwireproduct_id),('is_pack','=',False)],limit=1)
                if not synced_product:
                    synced_product = product_obj.search([('barcode', '=', sku),('is_pack','=',False)],limit=1)
                if not synced_product:
                    not_found_msg="Product NOT FOUND for shipwire SKU %s " % (sku)
                    log_line_vals = {
                        'log_type': 'error',
                        'action' : 'skip',
                        'log_id': log_record.id,
                        'message' : not_found_msg
                        }
                    log_line_obj.create(log_line_vals)
                    continue
                    
                if synced_product.is_pack:
                    not_found_msg="%s  is Pack Product and Skipped " % (synced_product.name)
                    log_line_vals = {
                        'log_type': 'info',
                        'action' : 'skip',
                        'log_id': log_record.id,
                        'message' : not_found_msg
                        }
                    log_line_obj.create(log_line_vals)
                    continue
                
                warehouse = warehouse_obj.search([('shipwire_warehouse_id','=',shipwirewarehouseId)])
                
                if not warehouse :
                    not_found_msg="Warehouse NOT FOUND for shipwire Id %s " % (shipwirewarehouseId)
                    log_line_vals = {
                        'log_type': 'error',
                        'action' : 'skip',
                        'log_id': log_record.id,
                        'message' : not_found_msg
                        }
                    log_line_obj.create(log_line_vals)
                    continue
                
                for inv in inventory_warehouse:
                    if inv[0]== warehouse:
                        product_inventory = inv[1].id 
                        break
                
                product_damage_inventory = False
                for d_inv in damage_inventory_warehouse:
                    if d_inv[0]== warehouse:
                        product_damage_inventory = d_inv[1].id
                        break
            try: 
                if warehouse.inventory_adjust:
                    if synced_product and warehouse:
                        qty = float(item['resource']['good'])
                        """
                        Create Inventory Adjustment
                        """
                        line_vals = self.prepare_inventory_line_dict(synced_product,qty,warehouse,warehouse.lot_stock_id.id,product_inventory)
                        inventory_line = inventory_line_obj.create(line_vals)
    #                     inventory.prepare_inventory()
            except Exception as e:
                not_found_msg="%s" % (e)
                log_line_vals = {
                        'log_type': 'error',
                        'action' : 'terminate',
                        'log_id': log_record.id,
                        'message' : not_found_msg,
                        'response': res or False
                        }
                log_line_obj.create(log_line_vals)
                _logger.error("Error in Product Stock Synchronization from Shipwire ")
                return False
            
            try: 
                if not product_damage_inventory:
                    continue
                if warehouse.damage_inventory:
                    if synced_product and warehouse:
                        damage_qty = float(item['resource']['damaged'])
                        """
                        Create Inventory Adjustment
                        """
                        damage_line_vals = self.prepare_inventory_line_dict(synced_product,damage_qty,warehouse,warehouse.shipwire_damage_location.id,product_damage_inventory)
                        damage_inventory_line = inventory_line_obj.create(damage_line_vals)
    #                     inventory.prepare_inventory()
            except Exception as e:
                not_found_msg="%s" % (e)
                log_line_vals = {
                        'log_type': 'error',
                        'action' : 'terminate',
                        'log_id': log_record.id,
                        'message' : not_found_msg,
                        'response': res or False
                        }
                log_line_obj.create(log_line_vals)
                _logger.error("Error in Product Stock Synchronization from Shipwire ")
                return False

        for inventory in inventory_warehouse:
            inventory[1].prepare_inventory()
            
        for inventory in damage_inventory_warehouse:
            inventory[1].prepare_inventory()
            
        
        return True
                     
         
    @api.multi        
    def prepare_inventory_dict(self,warehouse,location):
            
        vals={
            'name': warehouse.name+ ' - ' + str(datetime.now()),
            'location_id':location,
            'company_id' : warehouse.company_id.id,
            'filter':'partial',
            'is_shipwire' : True
        }
        return vals
    
    @api.multi
    def prepare_inventory_line_dict(self,product,real_qty,warehouse,location,inventory):
        vals={
            'location_id':location,
            'company_id':warehouse.company_id.id,
            'product_id':product.id,
            'inventory_id':inventory,
            'product_uom_id':product.uom_id.id,
            'product_qty':real_qty,
            }
        return vals
