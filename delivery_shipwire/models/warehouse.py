# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
#from shipwire_request import ShipwireRequest
from odoo.addons.delivery_shipwire.models.shipwire_request import ShipwireRequest
import logging
_logger = logging.getLogger(__name__)
TRACK_URL = 'https://api.beta.shipwire.com'

            
class warehouse(models.Model):
    _inherit = 'stock.warehouse'

    delivery = fields.Boolean("Shipwire")
    shipwire_username = fields.Char(string='Shipwire User ID')
    shipwire_passwd = fields.Char(string='Shipwire Password')
    shipwire_test_mode = fields.Boolean(default=True, string="Test Mode", help="Uncheck this box to use production Shipwire Web Services")
    location_sync_line = fields.One2many('odoo.shipwire.location', 'warehouse_id', string='Location Sync')
    
        
    @api.multi
    def CheckOrderStatusShipwireButton(self):
        if self.delivery == True:
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
        if self.delivery == True:
            ShipwireRequest_Object = ShipwireRequest(self.shipwire_username, self.shipwire_passwd, shipwire_test_mode=self.shipwire_test_mode)
            ShipwireRequest_Object.ShipwireProductIDsSync()
            return True
        ShipwireRequest_Object = ShipwireRequest(self.shipwire_username, self.shipwire_passwd, shipwire_test_mode=self.shipwire_test_mode)
        ShipwireRequest_Object.ShipwireProductIDsSync()
        return True
    
    @api.model
    def SyncProductsStockShipwire(self):
        if self.delivery == True:
            ShipwireRequest_Object = ShipwireRequest(self.shipwire_username, self.shipwire_passwd, shipwire_test_mode=self.shipwire_test_mode)
            ShipwireRequest_Object.ShipwireProductStockSync()
            return True
        ShipwireRequest_Object = ShipwireRequest(self.shipwire_username, self.shipwire_passwd, shipwire_test_mode=self.shipwire_test_mode)
        ShipwireRequest_Object.ShipwireProductStockSync()
        return True

    @api.model
    def CheckOrderStatusShipwire(self):
        for line in self.env['stock.picking'].search([]) :
            line.UpdateOrderStatus(self)
        return True
    
    
class OdooShipwireLocation(models.Model):
    _name = "odoo.shipwire.location"
    _description = "Odoo locations synched with Shipwire Warehouse ID."


    location_id = fields.Many2one('stock.location', string='Stock Location Sync', required=True, help="This is locations of current warehouse")
    shipwire_warehouse_id = fields.Char(string='Shipwire Warehouse Id', help="Shipwire Warehouse ID.")
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')



