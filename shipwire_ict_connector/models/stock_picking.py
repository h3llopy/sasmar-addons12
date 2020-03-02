from odoo import models,fields,api, _

from datetime import datetime,timedelta
import base64
import time
from pytz import timezone
import pytz
import json
from odoo.exceptions import except_orm, Warning, RedirectWarning 
from odoo.exceptions import UserError, ValidationError
from odoo.api import Environment
from dateutil import parser
import datetime

import os
import logging
logger = logging.getLogger(__name__)

class stockPicking(models.Model):

    _inherit = "stock.picking"

    shipwire_stage_id = fields.Many2one('shipwire.stages',string="Shipwire Stage",copy=False)
    ict_id = fields.Many2one('inter.company.transfer.ept',string="ICT",copy=False)
    tracking_lines = fields.One2many('shipwire.tracking','picking_id',string="Tracking Lines")
    

    # def reach_to_base_product(product_id):
    #     product = product_id

    #     if product.is_pack:
    #         reach_to_base_product()

    def conver_to_picking_data(self,data):
        product_product = self.env['product.product']
        return_data = []
        for line in data:
            barcode = line.get('sku')
            product = product_product.search([('barcode','=',barcode)],limit=1)
            if product:
                product_template = product.product_tmpl_id

                if product_template.is_pack:
                    for pack in product_template.pack_ids:
                        return_data.append({
                            'sku': pack.product_id.barcode,
                            'product_id' : pack.product_id.shipwire_product_id,
                            'ordered_qty' : (line.get('ordered_qty') or 1 )* (pack.qty_uom or 1),
                            'shipped_qty' : (line.get('shipped_qty') or 0 )* (pack.qty_uom or 1),
                        })
                else:
                    return_data.append({
                            'sku': line.get('sku'),
                            'product_id' : line.get('product_id'),
                            'ordered_qty' : line.get('ordered_qty'),
                            'shipped_qty' : line.get('shipped_qty'),
                        })
            else:
                # product not found log 
                pass
    
        return return_data

    @api.multi
    def process_delivery_order(self,data):


        stock_pack_operation=self.env['stock.pack.operation']
        move_obj=self.env['stock.move']
        product_product = self.env['product.product']
        obj_stock_immediate_transfer = self.env['stock.immediate.transfer']

        pick_ids = []
        pack_op_ods = []
        picking = self
        if not picking:
            #picking not found log
            return
        
        # data = self.conver_to_picking_data(data)

        for line in data:   
            barcode = line.get('sku')

            product = product_product.search([('barcode','=',barcode)],limit=1)
            
            file_qty = float(line.get('shipped_qty',0))

            move_lines = move_obj.search([('picking_id','=',picking.id),('product_id.barcode','=',barcode),('state','not in',['cancelled','draft'])])

            if len(move_lines) == 0:
                # Move lines not found log
                continue

            if file_qty == 0:
                # qty = 0 log
                continue
                                    
            qty_grouped={}
            for move in move_lines:
                for quant in move.reserved_quant_ids:
                    key=(quant.owner_id.id,move.location_id.id,move.location_dest_id.id,move.product_id.id,move.product_id.uom_id.id,quant.package_id.id)
                    if qty_grouped.has_key(key):
                        qty_grouped[key]+=quant.qty
                    else:
                        qty_grouped.update({key:quant.qty})
            quantity=float(file_qty)
            pack_op_qty=0.0
            for key, qty in qty_grouped.items():
                if quantity>qty:                                        
                    pack_op_qty=qty
                else:
                    pack_op_qty=quantity
                pack_op=stock_pack_operation.with_context({'no_recompute':True}).create(
                    {
                            'product_qty':float(pack_op_qty) or 0,
                            'date':time.strftime('%Y-%m-%d'),
                            'location_id':key[1], 
                            'location_dest_id': key[2],
                            'product_id': key[3],
                            'product_uom_id': key[4], 
                            'qty_done':float(pack_op_qty) or 0,
                            'picking_id':picking.id,
                            'owner_id':key[0],
                            'package_id':key[5]
                     })   
                pack_op_ods.append(pack_op.id)
                quantity=quantity-pack_op_qty                                 
                if quantity<=0.0:
                    break
            
            if not qty_grouped:
                pack_op=stock_pack_operation.with_context({'no_recompute':True}).create(                                                            
                                            {
                                                        'product_qty':file_qty or 0,
                                                        'date':time.strftime('%Y-%m-%d'),
                                                        'location_id':move_lines[0].location_id and move_lines[0].location_id.id or False, 
                                                        'location_dest_id': move_lines[0].location_dest_id and move_lines[0].location_dest_id.id or False,
                                                        'product_id': move_lines[0].product_id and move_lines[0].product_id.id or False,
                                                        'product_uom_id': move_lines[0].product_id and move_lines[0].product_id.uom_id and move_lines[0].product_id.uom_id.id or False, 
                                                        'qty_done':file_qty or 0,
                                                        'picking_id':picking.id,
                                                        'owner_id':False
                                                 })   
            pack_op_ods.append(pack_op.id)
        pick_ids.append(picking.id)

        if pick_ids and pack_op_ods:   
            exists_pack_ops=stock_pack_operation.search([('picking_id','in',pick_ids),('id','not in',pack_op_ods)])
            exists_pack_ops and exists_pack_ops.unlink()
            pickings=self.browse(list(set(pick_ids)))
            for picking in pickings:
                transfer_id = obj_stock_immediate_transfer.create({'pick_id':picking.id})
                transfer_id.process()
                # backorder = self.env['stock.picking'].search([('backorder_id','=',picking.id)])
                # if backorder and backorder.id:
                #     backorder.action_cancel()        
            

    
    def prepare_tracking_list(self,items):
        return_list = []
        for item in items:
            
            vals = {
                'url': item.get('resource').get('url'),
                'id' : item.get('resource').get('id'),
                'tracking' : item.get('resource').get('tracking'),
            }
            return_list.append(vals)

        return return_list
          
    def prepare_item_list(self,items):
        return_list = []
        for item in items:
            vals = {
                'sku': item.get('resource').get('sku'),
                'product_id' : item.get('resource').get('productId'),
                'ordered_qty' : item.get('resource').get('ordered'),
                'shipped_qty' : 1 ,# item.get('resource').get('shipped'),
            }
            return_list.append(vals)

        return return_list
            
    @api.multi
    def prepare_order_details_dict(self):
        api_url = "api/v3/orders/"
        instance = self.env['shipwire.instance'].search([],limit=1)
        details_dict = {}
        if instance:
            for record in self:
                if record.shipwire_id:
                    api_url = "%s%s"%(api_url,record.shipwire_id)
                    paramters = {
                        'expand':'items,trackings'
                        
                    }
                    response = instance.send_get_request(api_url,paramters)
                    #response = "{'status': 200, 'resourceLocation': 'https://api.shipwire.com/api/v3/orders/345762913', 'message': 'Successful', 'resource': {'vendorExternalId': None, 'vendorId': None, 'commercialInvoice': {'resourceLocation': 'https://api.shipwire.com/api/v3/orders/345762913/commercialInvoice'}, 'shipwireAnywhere': {'resourceLocation': None, 'resource': {'status': None}}, 'pieces': {'resourceLocation': 'https://api.shipwire.com/api/v3/orders/345762913/pieces?expand=items%2Ctrackings&offset=0&limit=20'}, 'purchaseOrderExternalId': None, 'shippingLabel': {'resourceLocation': 'https://api.shipwire.com/api/v3/orders/345762913/shippingLabel'}, 'orderNo': 'SO18US321477', 'id': 345762913, 'needsReview': 0, 'holds': {'resourceLocation': 'https://api.shipwire.com/api/v3/orders/345762913/holds?expand=items%2Ctrackings&offset=0&limit=20'}, 'commerceName': 'Shipwire', 'processAfterDate': '2018-01-04T04:30:00-08:00', 'returns': {'resourceLocation': 'https://api.shipwire.com/api/v3/orders/345762913/returns?expand=items%2Ctrackings&offset=0&limit=20'}, 'externalId': '10114', 'routing': {'resourceLocation': None, 'resource': {'warehouseId': 18, 'originLongitude': 51.5967, 'destinationLatitude': '50.8466', 'warehouseName': 'Tilburg, NLD', 'warehouseExternalId': None, 'physicalWarehouseId': None, 'destinationLongitude': '4.3528', 'originLatitude': 5.0051}}, 'purchaseOrderId': None, 'vendorName': None, 'status': 'delivered', 'shipTo': {'resourceLocation': None, 'resource': {'city': 'BRUSSELS', 'name': 'SASMAR', 'isPoBox': 0, 'address1': 'Chaussee De La Hulpe 187', 'company': 'SASMAR', 'address3': None, 'isCommercial': 1, 'email': 'test@test.com', 'phone': '88888888', 'state': '', 'country': 'BE', 'postalCode': '1170', 'address2': None}}, 'extendedAttributes': {'resourceLocation': 'https://api.shipwire.com/api/v3/orders/345762913/extendedAttributes?expand=items%2Ctrackings&offset=0&limit=20'}, 'pricingEstimate': {'resourceLocation': None, 'resource': {'packaging': 0.48, 'total': 6.52, 'insurance': 0, 'shipping': 6.52, 'handling': 0}}, 'freightSummary': {'resourceLocation': None, 'resource': {'weightUnit': None, 'measurementType': None, 'totalWeight': '0.00'}}, 'packingList': {'resourceLocation': 'https://api.shipwire.com/api/v3/orders/345762913/packingList'}, 'items': {'resourceLocation': 'https://api.shipwire.com/api/v3/orders/345762913/items?expand=items%2Ctrackings&offset=0&limit=20', 'resource': {'previous': None, 'next': None, 'total': 1, 'items': [{'resourceLocation': 'https://api.shipwire.com/api/v3/orders/345762913/items/511225263', 'resource': {'sk': '19337213008454', 'orderId': 345762913, 'ordered': 1, 'description': 'Conceive Plus 8x 4grm Applicators BDL880845', 'backordered': 0, 'reserved': 0, 'extendedAttributes': {'resourceLocation': None, 'resource': {'previous': None, 'next': None, 'total': 0, 'items': [], 'offset': 0}}, 'serialNumbers': {'resourceLocation': 'https://api.shipwire.com/api/v3/orders/345762913/items/511225263/serialNumbers?expand=items%2Ctrackings&offset=0&limit=20', 'resource': {'previous': None, 'next': None, 'total': 0, 'items': [], 'offset': 0}}, 'shipped': 1, 'shipping': 0, 'productExternalId': None, 'orderExternalId': '10114', 'productId': 2804102, 'commercialInvoiceValue': 0, 'id': 511225263, 'quantity': 1}}], 'offset': 0}}, 'splitOrders': {'resourceLocation': 'https://api.shipwire.com/api/v3/orders/345762913/splitOrders?expand=items%2Ctrackings&offset=0&limit=20'}, 'events': {'resourceLocation': None, 'resource': {'expectedDate': '2018-01-08T00:00:00-08:00', 'cancelledDate': '2018-01-04T02:13:26-08:00', 'expectedSubmittedDate': '2018-01-04T02:13:26-08:00', 'createdDate': '2018-01-03T06:04:29-08:00', 'returnedDate': None, 'submittedDate': '2018-01-04T02:13:26-08:00', 'expectedCompletedDate': '2018-01-04T02:13:26-08:00', 'lastManualUpdateDate': '2018-01-04T01:23:57-08:00', 'pickedUpDate': None, 'completedDate': '2018-01-04T02:13:26-08:00', 'processedDate': None}}, 'shipFrom': {'resourceLocation': None, 'resource': {'company': 'SASMAR LIMITED'}}, 'lastUpdatedDate': '2018-01-04T02:13:26-08:00', 'purchaseOrderNo': None, 'transactionId': '1514988269-891886-1', 'trackings': {'resourceLocation': 'https://api.shipwire.com/api/v3/orders/345762913/trackings?expand=items%2Ctrackings&offset=0&limit=20', 'resource': {'previous': None, 'next': None, 'total': 0, 'items': [], 'offset': 0}}, 'options': {'resourceLocation': None, 'resource': {'forceDuplicate': 0, 'serviceLevelCode': None, 'lastManualEditDate': '2018-01-04T01:23:57-08:00', 'carrierId': None, 'clearPreferenceHolds': None, 'carrierType': None, 'warehouseId': 18, 'warehouseRegion': 'NHL', 'physicalWarehouseId': None, 'channelName': None, 'billingType': None, 'localizationCode': None, 'warehouseExternalId': None, 'carrierAccountNumber': None, 'sameDay': 'NOT REQUESTED', 'warehouseArea': None, 'testOrder': 0, 'referrer': '', 'thirdPartyCarrierCodeRequested': None, 'forceAddress': 0, 'carrierCode': 'DHL BLXPPNL', 'forceOverPack': None}}, 'pricing': {'resourceLocation': None, 'resource': {'packaging': 0, 'total': 0, 'handling': 0, 'insurance': 0, 'shipping': 0}}}}"
                    #response = json.loads(response)
                    if not response:
                        return False
                    res = response.get('resource')
                    order_status = res.get('status',False)
                    # Destination will always be what we placed
                    logger.info("Response Status %s"%response)
                    items = self.prepare_item_list(res.get('items').get('resource').get('items'))
                    tracking_details = self.prepare_tracking_list(res.get('trackings').get('resource').get('items'))
                    vals = {
                        'status':order_status,
                        'requested_warehouse':res.get('options').get('resource').get('warehouseId'),
                        'from_warehouse':res.get('routing').get('resource').get('warehouseId'),
                        'items':items,
                        'tracking_details':tracking_details
                    }
                    details_dict.update({record.id:vals})         
            return details_dict

        raise ValidationError(_('Please configure shipwire instance first'))
           
    def create_ICT(self,source_warehouse,items=[]):
        product_product = self.env['product.product']
        ict_obj = self.env['inter.company.transfer.ept']
        ict_line_obj = self.env['inter.company.transfer.line']
        product_lines = []
        
        ict_record = False

        items = self.conver_to_picking_data(items)

        for line in items:
            if line.get('sku',False):
                domain = [
                    '|',
                    ('default_code','=',line.get('sku')),
                    ('barcode','=',line.get('sku')),
                    ('type','=','product')
                ]
                product_obj = product_product.search(domain,limit=1)
                if not ict_record:
                    ict_record = ict_obj.new({
                        'source_warehouse_id':source_warehouse.id,
                        'destination_warehouse_id':self.sale_id.warehouse_id.id,
                        'is_auto_ict':True,
                        'line_ids':False
                    })
                    ict_record.source_warehouse_id_onchange()
                    ict_record.onchange_destination_warehouse_id()
                    ict_record = ict_record.create(ict_record._convert_to_write(ict_record._cache))
                if product_obj:
                    move_domain = [
                        ('picking_id','=',self.id),
                        ('product_id','=',product_obj.id),
                        ('state','not in',['draft','cancel','done'])
                    ]
                    move_ids = self.env['stock.move'].search(move_domain)
                    ict_line_vals = ict_line_obj.new({
                        'transfer_id':ict_record.id,
                        'product_id':product_obj.id,
                        'quantity':line.get('shipped_qty') or 0.0,
                        'stock_move_ids': False if not move_ids else [(6,0,move_ids.ids)]
                    })
                    ict_line_vals.default_price()
                    ict_line_vals = ict_line_vals._convert_to_write(ict_line_vals._cache)

                    product_lines.append((0,0,ict_line_vals))
                    
        if ict_record:
            ict_record.write({'line_ids':product_lines})

        return ict_record
    
    @api.multi
    def SetShipwireItems(self, items):

        product_obj = self.env['product.product']
        items_list = []
        resource = items['resource']['items']
        
        for i in resource:
            product_search = product_obj.search([('carrier_tracking_ref', '=', str(i['resource']['productId']) )])
            product_id = product_search[0].id if product_search else False
            item_dict = {
                'product_id' :product_id ,
                'quantity' : str(i['resource']['quantity']),
                'reserved' : str(i['resource']['reserved']),
                'shipped' : str(i['resource']['shipped']),
                'shipping' :str( i['resource']['shipping']),
                'backordered': str(i['resource']['backordered']),
                'ordered' : str(i['resource']['ordered']),
                'name' : i['resource']['productId']
                }
            if self.shipwire_items:
                for line in self.shipwire_items:
                    if product_id == line.product_id.id:
                        items_list.append((1, line.id ,item_dict))
            else:
                items_list.append((0, 0 ,item_dict))
        res = self.write({'shipwire_items' : items_list})
        return res

    @api.multi
    def SetShipwireHolds(self, holds):
        '''Create shipwire Holds based on the returns we got in Shipwire response 
        for particular order'''
        holds_list = []
        resource = holds['resource']['items']
        for hold_data in resource:
            resource = hold_data['resource']
            hold_dict = {
                'name' : resource['id'],
                'description' : resource['description'],
                'applieddate' : resource['appliedDate'],
                'cleareddate' : resource['clearedDate'],
                'hold_id' : resource['id'],
                }
            if self.shipwire_holds:
                for line in self.shipwire_holds:
                    if hold_data['resource']['id'] == line.hold_id:
                        holds_list.append((1, line.id, hold_dict))
            else:
                holds_list.append((0, 0 ,hold_dict))
        return self.write({'shipwire_holds' : holds_list})

    @api.multi
    def SetShipwireReturns(self, returns):
        '''Create shipwire Return based on the returns we got in Shipwire response 
        for particular order'''
        returns_list = []
        resource = returns['resource']['items']
        for return_data in resource:
            resource = return_data['resource']
            return_dict = {
                'name' : resource['id'],
                'transactionid' : resource['transactionid'],
                'status' : resource['status'],
                }
            if self.shipwire_returns:
                for line in self.shipwire_returns:
                    returns_list.append((1, line.id, return_dict))
            else:
                returns_list.append((0, 0 ,return_dict))
        return self.write({'shipwire_returns' : returns_list})

    @api.multi
    def process_bulk_response(self,data={}):
        picking_obj = self.env['stock.picking']
        details_dict = {}
        for record in data.get('items',[]):
            res = record.get('resource')
            order_status = res.get('status',False)
            shipwire_id = res.get('id')
            domain = [
                ('shipwire_id','=',shipwire_id),
                ('state','not in',['draft','cancel','done'])
            ]
            picking_obj = picking_obj.search(domain,limit=1)
            if not picking_obj:
                continue

            # Destination will always be what we placed
            items = self.prepare_item_list(res.get('items').get('resource').get('items'))
            tracking_details = self.prepare_tracking_list(res.get('items').get('resource').get('items'))
            vals = {
                'status':order_status,
                'requested_warehouse':res.get('options').get('resource').get('warehouseId'),
                'from_warehouse':res.get('routing').get('resource').get('warehouseId'),
                'items':items,
                'tracking_details':tracking_details
            }
            details_dict.update({picking_obj.id:vals})
        return details_dict


    @api.model
    def check_shipwire_status_all(self):
        picking_domain = [
            ('state', 'not in', ['done', 'draft', 'cancel']),
            ('shipwire_id', '!=', False),
        ]
        pickings = self.env['stock.picking'].search(picking_domain)
        for picking in pickings:
            try:
                picking.check_shipwireorder_status()
                self._cr.commit()
            except:
                continue


    @api.model
    def check_shipwireorder_status_from_last_date(self):
        shipwire_instance = self.env['shipwire.instance'].search([],limit=1)

        if shipwire_instance:
            
            if not shipwire_instance.last_do_sync_date:
                picking_domain = [
                ('state','not in',['done','draft','cancel']),
                ('shipwire_id','!=',False),
                ]
                pickings = self.env['stock.picking'].search(picking_domain)
                pickings.check_shipwireorder_status()
                shipwire_instance.write({'last_do_sync_date':datetime.datetime.today()})
                return 

            updated_after = shipwire_instance.last_do_sync_date
            updated_after = datetime.datetime.strptime(updated_after, "%Y-%m-%d %H:%M:%S")
            updated_after = updated_after.isoformat()
            api_url = "api/v3/orders"
            parameters = {
            'expand' : 'items,Trackings',
            'updatedAfter' : updated_after,
            }
            
            items = shipwire_instance.send_get_request_with_all_records(api_url,parameters)
            pickings = self.process_bulk_response(items)
            for picking,vals in pickings.iteritems():
                picking.with_context({'preloaded_response':True}).check_shipwireorder_status(vals)

            shipwire_instance.write({'last_do_sync_date':datetime.datetime.now()})
        
        return items
        # return with log 

    def add_tracking_details_to_picking(self,data):
        if not self:
            return
        self.tracking_lines and self.tracking_lines.unlink()
        
        tracking_line = self.env['shipwire.tracking']
        
        tracking_line_ids = []
        for item in data:
            
            line_id = tracking_line.create({
                'picking_id':self.id,
                'name':item.get('tracking'),
                'url':item.get('url'),
                'shipwire_id':item.get('id'),
            })
            tracking_line_ids.append(line_id.id)
            
        self.write({'tracking_lines':[(6,0,tracking_line_ids)]})
        
        
        
    @api.multi
    def check_shipwireorder_status(self,preloaded_response=[]):

        context = self._context or {}
        is_preloaded = context.get('preloaded_response',False) 

        config_record = self.env.ref('ICT_ept_v9.intercompany_transaction_config_record')
        #Create list of ('source_warehouse','destination_warehouse')
        ict_obj = self.env['inter.company.transfer.ept']
        ict_line_obj = self.env['inter.company.transfer.line']
        product_product = self.env['product.product']
        src_dest_wh_list = []
        all_items = []
        
        job_log = False
        for record in self:
            if not job_log:
                record_name='/'
                sequence_id=self.env.ref('shipwire_odoo_operation.shipwire_process_log_seq').ids
                if sequence_id:
                    record_name=self.env['ir.sequence'].get_id(sequence_id[0])

                job_log = self.env['process.log'].create(
                    {
                        'name':record_name,
                        'log_date':datetime.datetime.today(),
                        'process':'sale',
                        'operation':'import',
                        'result':False,
                        'log_line_ids':False
                    }
                )

            order_details = False
            if not is_preloaded:
                order_details = record.prepare_order_details_dict()
            else:
                order_details = preloaded_response

            if not order_details:
                continue

            data = order_details.get(record.id)
            
            code = data.get('status')
            items = data.get('items')
            tracking_details = data.get('tracking_details')
            
            logger.info("Tracking Ready")
            record.add_tracking_details_to_picking(tracking_details)
            logger.info("Tracking Added")
            
            if record.state in ['draft','done']:
                continue
            if record.ict_id:
                continue

                        
            #if code == 'cancelled':
            #    record.action_cancel()
                
            elif code in ['processing','submitted','on_hold']:
                record.action_assign()
            
            elif code in ['delivered','completed','returned','cancelled'] and items:
                logger.info("Status Ready")
		
                source_warehouse = self.env['stock.warehouse'].search([('shipwire_warehouse_id','=',data.get('from_warehouse',-1))],limit=1)
		
                if not source_warehouse:
                    # log source warehouse not found
                    # Please configure first
                    pass

                if source_warehouse.company_id.id == record.picking_type_id.warehouse_id.company_id.id:
                    # Create Internal Transfer between warehouse of same company
                    intercompany_user = source_warehouse.company_id.intercompany_user_id.id
                    stock_picking_obj = self.env['stock.picking']
                    picking = stock_picking_obj.sudo(intercompany_user).create({
                        'location_id':source_warehouse.lot_stock_id.id,
                        'location_dest_id':record.location_id.id,
                        'picking_type_id':source_warehouse.out_type_id.id,
                        'move_type': 'direct',
                        'origin':record.name,
                    })
                    items = record.conver_to_picking_data(items)
                    for response_line in items:
                        product_domain = [
                            '|',
                            ('default_code', '=', response_line.get('sku')),
                            ('barcode', '=', response_line.get('sku'))
                        ]
                        product_obj = product_product.search(product_domain, limit=1)
                        if product_obj:
                            move = self.env['stock.move'].sudo(intercompany_user).new({
                                'product_id':product_obj.id,
                                'product_uom_qty':response_line.get('shipped_qty'),
                                'location_id':source_warehouse.lot_stock_id.id,
                                'location_dest_id':record.location_id.id,
                                'procure_method':'make_to_stock',
                                'picking_id':picking.id,
                                'product_uom': product_obj.uom_id.id,
                                'name': product_obj.name
                            })
                            move.onchange_product_id()
                            move = move.create(move._convert_to_write(move._cache))
                            move.action_confirm()
                            move.action_assign()
                    picking.action_confirm()
                    if picking.state in ['waiting','confirmed','partially_available']:
                        picking.force_assign()
                    else:
                        picking.action_assign()
                    validate_id = picking.do_new_transfer()
                    res_id = validate_id.get('res_id')
                    obj_stock_immediate_transfer = self.env['stock.immediate.transfer']
                    transfer_id = obj_stock_immediate_transfer.browse(res_id)
                    transfer_id.process()
                    # Write Status
                    status = self.env['shipwire.stages'].search([('code', '=', code)], limit=1)
                    if status:
                        record.write({'shipwire_stage_id': status.id})
                    record.process_delivery_order(items)
                    continue


                append_ict = True
                if not config_record.is_ict_per_so:
                    ict_domain = [
                        ('is_auto_ict','=',True),
                        ('source_warehouse_id','=',source_warehouse.id),
                        ('destination_warehouse_id','=',record.sale_id.warehouse_id.id),
                        ('state','=','draft'),
                    ]
                    logger.info("Search ICT")
                    ict_record = ict_obj.search(ict_domain,limit=1)
                    if ict_record:
                        append_ict = False
                        line_product_ids = {}
                        for line in ict_record.line_ids:
                            line_product_ids.update({line.product_id.id:line.id})
                        line_product_keys = line_product_ids.keys()
                        for response_line in items:
                            product_domain = [
                                '|',
                                ('default_code','=',response_line.get('sku')),
                                ('barcode','=',response_line.get('sku'))
                            ]
                            product_obj = product_product.search(product_domain,limit=1)
                            if product_obj:
                                move_domain = [
                                    ('picking_id','=',record.id),
                                    ('product_id','=',product_obj.id),
                                    ('state','not in',['draft','cancel','done'])
                                ]
                                move_ids = self.env['stock.move'].search(move_domain)

                                if product_obj.id in line_product_keys:
                                    # add quantity to same line

                                    line_id = line_product_ids[product_obj.id]
                                    line_obj = ict_line_obj.browse(line_id)
                                    line_obj.write(
                                        {
                                            'quantity': line_obj.quantity + (response_line.get('shipped_qty') or 0.0),
                                            'stock_move_ids' : [(4,0,move_ids.ids)]
                                        }
                                    )
                                    line_obj.default_price()

                                else:
                                    # create new line and append line into same ICT record
                                    ict_line_vals = ict_line_obj.new({
                                        'transfer_id':ict_record.id,
                                        'product_id':product_obj.id,
                                        'quantity':response_line.get('shipped_qty') or 0.0,
                                        'stock_move_ids': False if not move_ids else [(6,0,move_ids.ids)]
                                    })
                                    ict_line_vals.default_price()
                                    ict_line_vals = ict_line_vals._convert_to_write(ict_line_vals._cache)
                            else:
                                # product not found log
                                pass

                if append_ict:
                    
                    logger.info("Create New ICT")
                    ict_record = record.create_ICT(source_warehouse,items)
                    logger.info("ICT DONE")
                if ict_record:
                    logger.info("Validate ICT")
                    ict_record.with_context({'force_validate_picking':True}).validate_data()
                    record.write({'ict_id':ict_record.id})
                    logger.info("ICT Validated")
                    product_ids = [move.product_id.id for move in record.move_lines]
                    move_domain = [
                        ('product_id','in',product_ids),
                        ('picking_type_id.code','=','outgoing'),
                        ('state','in',['assigned','confirmed']),
                    ]
                    stock_moves = self.env['stock.move'].search(move_domain)
                    #stock_moves.do_unreserve()
                    record.action_assign()
                    picking_list = [move.picking_id.id for move in stock_moves]
                    record.process_delivery_order(items)
                    logger.info("Done Current Picking")
            status = self.env['shipwire.stages'].search([('code','=',code)],limit=1)
            if status:
                record.write({'shipwire_stage_id':status.id})
                #record.process_delivery_orders()


    def conver_to_return_picking_data(self,data):
        product_product = self.env['product.product']
        return_data = []
        for line in data:
            line = line.get('resource',{})
            barcode = line.get('sku')
            product = product_product.search([('barcode','=',barcode)],limit=1)
            if product:
                product_template = product.product_tmpl_id

                if product_template.is_pack:
                    for pack in product_template.pack_ids:
                        return_data.append(
                            {'resourceLocation': None,
                                'resource':
                                 {
                                    'sku': pack.product_id.barcode,
                                    'product_id' : pack.product_id.shipwire_product_id,
                                    'good' : (line.get('good') or 1 )* (pack.qty_uom or 1),
                                    'damaged' : (line.get('damaged') or 1 )* (pack.qty_uom or 1),
                                 }
                            }
                            )
                else:
                    return_data.append(
                        {'resourceLocation': None,
                                'resource':
                                 {
                                    'sku': line.get('sku'),
                                    'product_id' : line.get('product_id'),
                                    'good' : line.get('good'),
                                    'damaged' : line.get('damaged'),
                                }
                        })
            else:
                # product not found log 
                pass
    
        return return_data

    @api.model            
    def sync_shipwire_returns_process(self):
        
        sale_order_obj = self.env['sale.order']
        picking_obj = self.env['stock.picking']
        product_obj = self.env['product.product']
        stock_return_picking = self.env['stock.return.picking']
        stock_move_obj = self.env['stock.move']
        reverse_ict_obj = self.env['reverse.inter.company.transfer.ept']
        reverse_ict_line_obj = self.env['reverse.inter.company.transfer.line.ept']
        api = 'api/v3/returns'
        instance = self.env['shipwire.instance'].search([],limit=1)
        
        parameters = {'expand' : 'items'}
        if instance.last_return_sync_date:
            
            updated_after = instance.last_return_sync_date
            updated_after = str(updated_after)
            updated_after = updated_after[:updated_after.rindex(" ")+9]
            
            updated_after = datetime.datetime.strptime(updated_after, "%Y-%m-%d %H:%M:%S")
            updated_after = updated_after.isoformat()
     
            parameters = {
            'expand' : 'items',
            'updatedAfter' : updated_after,
            }
      
        response = instance.send_get_request_with_all_records(api,parameters)
#         items = response.get('resource').get('items')
        items = response.get('items') 
        
        for item in items :
            
            order_url = item.get('resource').get('originalOrder').get('resourceLocation')
            
            id = int ( order_url.replace('https://api.shipwire.com/api/v3/orders/','') ) 

            picking = picking_obj.search([('shipwire_id','=',id)],limit=1,order='id desc')
     
            
            if not picking:
                continue

            picking_to_stock = []

            return_items = item.get('resource').get('items').get('resource').get('items')
     
            return_items = self.conver_to_return_picking_data(return_items)


            for product_item in return_items:
                
                sku = product_item.get('resource').get('sku')

                product= product_obj.search([('barcode','=',sku)])
                
                if not product:
                    continue
                
                qty = product_item.get('resource').get('good')
                if qty == 0:
                    continue
                
                move_id = stock_move_obj.search([('picking_id','=',picking.id),('product_id','=',product.id)],limit=1)
                
                line = (0,0,{'product_id': move_id.product_id.id, 'move_id': move_id.id, 'quantity': qty})
                picking_to_stock.append(line)
  

            if not picking_to_stock:
                #log here
                continue


            if not picking.ict_id:
                picking.check_shipwireorder_status()
            
            if not picking.ict_id:
                continue


            defautl_vals = stock_return_picking.with_context({'active_id':picking.id}).default_get(['move_dest_exists','original_location_id','parent_location_id','location_id','product_return_moves'])
            defautl_vals.update({'product_return_moves':picking_to_stock})
            return_picking = stock_return_picking.create(defautl_vals)
            tmp = return_picking.with_context({'active_id':picking.id}).create_returns()
            stock_picking = self.env['stock.picking'].browse(tmp.get('res_id'))
                
            reverse_ict = reverse_ict_obj.create({'ict_id':picking.ict_id.id})
            
            product_lines = []
            for line in stock_picking.move_lines:
                reverse_ict_line = reverse_ict_line_obj.create({
                            'reverse_ict_id':reverse_ict.id,
                            'product_id':line.product_id.id,
                            'quantity':line.product_uom_qty or 1,
                        })
                product_lines.append(reverse_ict_line.id)
    
            reverse_ict.write({'line_ids':[(6,0,product_lines)]})
            
            reverse_ict.process_reverse_ict()
            reverse_ict.validate_pickings()

            validate_id = stock_picking.do_new_transfer()
            res_id = validate_id.get('res_id')
            obj_stock_immediate_transfer = self.env['stock.immediate.transfer']
            transfer_id = obj_stock_immediate_transfer.browse(res_id)
            transfer_id.process()
        instance.write({'last_return_sync_date':datetime.datetime.today()})
        return True
        

