# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)
TRACK_URL = 'https://api.beta.shipwire.com'

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    carrier_id = fields.Many2one("delivery.carrier", string="Delivery Method", help="Fill this field if you plan to invoice the shipping based on picking.")
            
"""class ProviderShipwire(models.Model):
    _inherit = 'delivery.carrier'

    delivery = fields.Boolean( "Shipwire")
    shipwire_username = fields.Char(string='Shipwire User ID')
    shipwire_passwd = fields.Char(string='Shipwire Password')
    shipwire_test_mode = fields.Boolean(default=True, string="Test Mode", help="Uncheck this box to use production Shipwire Web Services")
    
        
    @api.multi
    def CheckOrderStatusShipwireButton(self):
        shipwire_carrier_id = self.env['ir.model.data'].xmlid_to_res_id('delivery_shipwire.delivery_carrier_shipwire')
        pickings = self.env['stock.picking'].search([('carrier_id', '=', shipwire_carrier_id)])
        for picking in pickings:
            self.CheckOrderStatusShipwire(picking)

    @api.multi
    def SyncProductsShipwireButton(self):
        self.SyncProductsShipwire()
        
    @api.multi
    def SyncProductsStockButton(self):
        self.SyncProductsStockShipwire()

    @api.model
    def SyncProductsShipwire(self):
        if not self.id:
            carrier = self.env['ir.model.data'].xmlid_to_object('delivery_shipwire.delivery_carrier_shipwire', raise_if_not_found=False, context={})
            ShipwireRequest_Object = ShipwireRequest(carrier.shipwire_username, carrier.shipwire_passwd, shipwire_test_mode=carrier.shipwire_test_mode)
            ShipwireRequest_Object.ShipwireProductIDsSync()
            return True
        ShipwireRequest_Object = ShipwireRequest(self.shipwire_username, self.shipwire_passwd, shipwire_test_mode=self.shipwire_test_mode)
        ShipwireRequest_Object.ShipwireProductIDsSync()
        return True
    
    @api.model
    def SyncProductsStockShipwire(self):
        if not self.id:
            carrier = self.env['ir.model.data'].xmlid_to_object('delivery_shipwire.delivery_carrier_shipwire', raise_if_not_found=False, context={})
            ShipwireRequest_Object = ShipwireRequest(carrier.shipwire_username, carrier.shipwire_passwd, shipwire_test_mode=carrier.shipwire_test_mode)
            ShipwireRequest_Object.ShipwireProductStockSync()
            return True
        ShipwireRequest_Object = ShipwireRequest(self.shipwire_username, self.shipwire_passwd, shipwire_test_mode=self.shipwire_test_mode)
        ShipwireRequest_Object.ShipwireProductStockSync()
        return True

    @api.model
    def CheckOrderStatusShipwire(self, order):
        order.UpdateOrderStatus()
        return True"""
    
    