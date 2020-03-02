# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.exceptions import UserError, ValidationError
#from shipwire_request import ShipwireRequest
#from odoo.addons.delivery_shipwire import shipwire_request
from odoo.addons.delivery_shipwire.models.shipwire_request import ShipwireRequest
from odoo import api, fields, models, _
import logging
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class stock_location(models.Model):
    _inherit = 'stock.location'

    @api.one
    @api.constrains('id')
    def _check_loc(self):
        if self.id == 49:
            raise ValidationError(_('You can not delete this location'))

class sale_order(models.Model):
    _inherit = 'sale.order'


    @api.onchange('warehouse_id')
    def _onchange_warehouse_id(self):
        if self.warehouse_id:
            search_warehouse = self.env['stock.warehouse'].search([('name','=', 'Shipwire Warehouse')])
            if self.warehouse_id.id == 6 :
                shipwire_carrier_id = self.env['ir.model.data'].xmlid_to_res_id('delivery_shipwire.delivery_carrier_shipwire')
                self.carrier_id = shipwire_carrier_id
            else:
                self.carrier_id = False

class stock_shipwire_stages(models.Model):
    _name = 'stock.shipwire.stages'

    name = fields.Char('Shipwire Stage')
    state_odoo = fields.Char('Relevant Odoo Stage')
    sequence = fields.Integer('Sequence')


class stock_move(models.Model):
    _inherit = 'stock.move'
    
    @api.cr_uid_ids_context
    def _picking_assign(self, cr, uid, move_ids, context=None):
        
        """Try to assign the moves to an existing picking
        that has not been reserved yet and has the same
        procurement group, locations and picking type  (moves should already have them identical)
         Otherwise, create a new picking to assign them to.
        """
        context = context or {}
        context = dict(context)
        move = self.browse(cr, uid, move_ids, context=context)[0]
        
        pick_obj = self.pool.get("stock.picking")
        picks = pick_obj.search(cr, uid, [
                ('group_id', '=', move.group_id.id),
                ('location_id', '=', move.location_id.id),
                ('location_dest_id', '=', move.location_dest_id.id),
                ('picking_type_id', '=', move.picking_type_id.id),
                ('printed', '=', False),
                ('state', 'in', ['draft', 'confirmed', 'waiting', 'partially_available', 'assigned'])], limit=1, context=context)
        if picks:
            pick = picks[0]
        else:
            values = self._prepare_picking_assign(cr, uid, move, context=context)
            for move_id in move:
                if  move_id.procurement_id.sale_line_id.order_id.carrier_id:
                    carrier_id = move.procurement_id.sale_line_id.order_id.carrier_id.id 
                    context.update({'carrier': carrier_id })
            if move:
                context.update({'moves': move })
            
            pick = pick_obj.create(cr, uid, values, context=context)
        return self.write(cr, uid, move_ids, {'picking_id': pick}, context=context)

    
class stock_picking(models.Model):
    _inherit = 'stock.picking'

    shipwirestage_id = fields.Many2one('stock.shipwire.stages', string="Shipwire Stages")
    shipwire_items = fields.One2many('stock.shipwire.items', 'picking_id', string="Shipwire Items")
    shipwire_holds = fields.One2many('stock.shipwire.holds', 'picking_id', string="Shipwire Holds")
    shipwire_returns = fields.One2many('stock.shipwire.returns', 'picking_id', string="Shipwire Returns")
    shipwire_error = fields.Text('Shipwire Error')
    shipwire_check = fields.Boolean('Shipwire Order')
    


    def action_assign(self):
       
        """ Check availability of picking moves.
        This has the effect of changing the state and reserve quants on available moves, and may
        also impact the state of the picking as it is computed based on move's states.
        @return: True
        """
        for pick in self:
            if pick.state == 'draft':
                self.action_confirm()
            #skip the moves that don't need to be checked
            move_ids = [x.id for x in pick.move_lines if x.state not in ('draft', 'cancel', 'done')]
            if not move_ids:
                raise UserError(_('Nothing to check the availability for.'))
            self.env['stock.move']._action_assign()
            
            origin = pick.origin
            sale_order = self.env['sale.order'].search([('name','=',origin)])
            
            if sale_order:
                if sale_order.warehouse_id.delivery == True:
                    
                    move = self.env['stock.move'].browse( move_ids)
                    
                    try:
                        if not pick.carrier_tracking_ref:
                            ShipwireRequest_Object = ShipwireRequest(sale_order.warehouse_id.shipwire_username, sale_order.warehouse_id.shipwire_passwd, shipwire_test_mode=sale_order.warehouse_id.shipwire_test_mode)
                            ship_order = ShipwireRequest_Object.ShipwireOrderCreate(pick , move)
                            
                            if ship_order:
                                if ship_order['resource']['items']:
                                    for ship in ship_order['resource']['items']:
                                        
                                        ship_id = ship['resource']['id']
                                        pick.write({'carrier_tracking_ref': ship_id })
                                        
                    except Exception as e:
                        _logger.error("Error in Create Order With Shipwire")
                        _logger.error('Error message :%s' % e)

        res = super(stock_picking, self).action_assign()
        return res

    @api.multi
    def SetShipwireItems(self, items):
        '''Create shipwire items based on the returns we got in Shipwire response 
        for particular order'''
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
    def SetShipwireStatus(self, status):
        '''Set shipwire stage in odoo'''
        status_exernal_ids = ['shipwire_stage_held', 'shipwire_stage_pending', 'shipwire_stage_processed',
                              'shipwire_stage_submitted', 'shipwire_stage_completed', 'shipwire_stage_delivered',
                              'shipwire_stage_returned']
        data_obj = self.env['ir.model.data']
        id_dict = {}
        [id_dict.update({x.split('_')[2] : data_obj.get_object_reference('delivery_shipwire', x)[1]}) for x in status_exernal_ids]
        return self.write({'shipwirestage_id' : id_dict[status]})
    
    @api.multi
    def SetOdooStatus(self, status):
        '''Set shipwire stage in odoo'''
        status_exernal_ids = ['shipwire_stage_held', 'shipwire_stage_pending', 'shipwire_stage_processed',
                              'shipwire_stage_submitted', 'shipwire_stage_completed', 'shipwire_stage_delivered',
                              'shipwire_stage_returned']
        shipwire_held_id = self.env['ir.model.data'].xmlid_to_res_id('delivery_shipwire.shipwire_stage_held')
        shipwire_pending_id = self.env['ir.model.data'].xmlid_to_res_id('delivery_shipwire.shipwire_stage_pending')
        shipwire_processed_id = self.env['ir.model.data'].xmlid_to_res_id('delivery_shipwire.shipwire_stage_processed')
        shipwire_submitted_id = self.env['ir.model.data'].xmlid_to_res_id('delivery_shipwire.shipwire_stage_submitted')
        shipwire_completed_id = self.env['ir.model.data'].xmlid_to_res_id('delivery_shipwire.shipwire_stage_completed')
        shipwire_delivered_id = self.env['ir.model.data'].xmlid_to_res_id('delivery_shipwire.shipwire_stage_delivered')
        shipwire_returned_id = self.env['ir.model.data'].xmlid_to_res_id('delivery_shipwire.shipwire_stage_returned')
        data_obj = self.env['ir.model.data']
        id_dict = {}
        [id_dict.update({x.split('_')[2] : data_obj.get_object_reference('delivery_shipwire', x)[1]}) for x in status_exernal_ids]
        if id_dict[status] == shipwire_held_id:
            for move in self.move_lines:
                return move.write({'state' : 'confirmed'})
        if id_dict[status] == shipwire_pending_id:
            for move in self.move_lines:
                return move.write({'state' : 'confirmed'})
        if id_dict[status] == shipwire_processed_id:
            for move in self.move_lines:
                return move.write({'state' : 'assigned'})
        if id_dict[status] == shipwire_submitted_id:
            for move in self.move_lines:
                return move.write({'state' : 'assigned'})
        if id_dict[status] == shipwire_completed_id:
            for move in self.move_lines:
                return move.write({'state' : 'done'})
        if id_dict[status] == shipwire_delivered_id:
            for move in self.move_lines:
                return move.write({'state' : 'done'})
        if id_dict[status] == shipwire_returned_id:
            for move in self.move_lines:
                return move.write({'state' : 'done'})
        

    @api.multi
    def UpdateOrderStatus(self,warehouse):
        '''Create Relevant documents in odoo based on shipwire resonse'''
        
        ShipwireRequest_Object = ShipwireRequest(warehouse.shipwire_username, warehouse.shipwire_passwd, shipwire_test_mode=warehouse.shipwire_test_mode)
        ShipwireData = ShipwireRequest_Object.ShipwireCheckOrderStatus(self)
        
        if not ShipwireData.get('error_message'):
            items = ShipwireData.get('items')
            if items:
                self.SetShipwireItems(items)
            holds = ShipwireData.get('holds')
            if holds:
                self.SetShipwireHolds(holds)
            returns = ShipwireData.get('returns')
            if returns:
                self.SetShipwireReturns(returns)
            status = ShipwireData.get('status')
            if status:
                self.SetShipwireStatus(status)
                self.SetOdooStatus(status)
        elif ShipwireData.get('error_message'):
            self.write({'shipwire_error':ShipwireData.get('error_message')})

    @api.model
    def CheckOrderStatusShipwire(self):
        '''Check Order Status for Delivery Order in Shipwire using carrier_tracking_ref Of Order
        and update Picking with relevant stage in odoo.'''
        shipwire_carrier_id = self.env['ir.model.data'].xmlid_to_res_id('delivery_shipwire.delivery_carrier_shipwire')
        pickings = self.search([('carrier_id', '=', shipwire_carrier_id)])
        for picking in pickings:
            picking.UpdateOrderStatus()
        return True


class stock_shipwire_items(models.Model):
    _name = 'stock.shipwire.items'

    name = fields.Char('Shipwire Item Id')
    product_id = fields.Many2one('product.product', string='SKU')
    quantity = fields.Char('Quantity')
    ordered = fields.Char('ordered')
    backordered = fields.Char('Backordered')
    reserved = fields.Char('Reserved')
    shipped = fields.Char('Shipped')
    shipping = fields.Char('shipping')
    picking_id = fields.Many2one('stock.picking', string='Picking')

class stock_shipwire_returns(models.Model):
    _name = 'stock.shipwire.returns'

    name = fields.Char('Shipwire Return Id')
    transactionid = fields.Char('Shipwire Return transactionId')
    status = fields.Char('Return Status')
    picking_id = fields.Many2one('stock.picking', string='Picking')


class stock_shipwire_holds(models.Model):
    _name = 'stock.shipwire.holds'

    name = fields.Char('Shipwire Hold Id')
    description = fields.Char('Description')
    cleareddate = fields.Datetime('Hold Clearance Date')
    applieddate = fields.Datetime('Hold Applied Date')
    picking_id = fields.Many2one('stock.picking', string='Picking')
    hold_id  = fields.Char('Hold ID')
