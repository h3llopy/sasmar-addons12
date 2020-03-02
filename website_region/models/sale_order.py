# -*- coding: utf-8 -*-
import random

from odoo import SUPERUSER_ID, tools
from odoo import models,fields,api
from odoo.http import request
from odoo.tools.translate import _
from odoo.exceptions import UserError
# from odoo.addons.website_sale.models.sale_order import website

from geoip import geolite2
import os
from socket import gethostname, gethostbyname


class website(models.Model):
    _inherit = 'website'

    def sale_get_order(self,force_create=False, force_region = False,code=None, update_pricelist=False,update_region = False, force_pricelist=False):
        
        partner = self.env.user.partner_id
        sale_order_obj = self.env['sale.order']
        sale_order_id = request.session.get('sale_order_id')
        if not sale_order_id:
            last_order = partner.last_website_so_id
            available_pricelists = self.get_pricelist_available()
            # Do not reload the cart of this user last visit if the cart is no longer draft or uses a pricelist no longer available.
            sale_order_id = last_order and last_order.state == 'draft' and last_order.pricelist_id in available_pricelists and last_order.id

        sale_order = None
        # Test validity of the sale_order_id
        if sale_order_id and sale_order_obj.exists(sale_order_id):
            sale_order = sale_order_obj.browse(sale_order_id)
        else:
            sale_order_id = None
        pricelist_id = request.session.get('website_sale_current_pl')
        if force_pricelist and self.env['product.pricelist'].search_count([('id', '=', force_pricelist)]):
            pricelist_id = force_pricelist
            request.session['website_sale_current_pl'] = pricelist_id
            update_pricelist = True
#       if force_region and self.pool['website.region.country'].search_count(cr, uid, [('id', '=', force_region )], context=context):
#            region_id = force_region
#        else:
#            region_id = request.session.get('website_sale_current_pl')
			#region_id = request.session.get('website_sale_current_pl')
			#ip_add = request.httprequest.environ["REMOTE_ADDR"] # This Code is working in test/live server 
            '''ip_add  = os.popen("wget http://ipecho.net/plain -O - -q ; echo").read() # This Code is working in local
            match = geolite2.lookup(ip_add[:-1])
            locate_country= match.get_info_dict().get('country').get('names').get('en')
            region = False
            region_obj = request.registry['website.region.country']
            region_ids = region_obj.search(cr, uid, [], context=None)
            regions = region_obj.browse(cr, uid, region_ids, context=None)
            for reg in regions:
                if reg.country_id:
                    for country in reg.country_id:

					    if country.name == locate_country:
					        region = reg.id'''

        region_id = request.session.get('website_region')
        #if region_id:
            #if isinstance(region_id, (int, long)):
             #   region_id=[region_id]
            #region_brw = self.pool['website.region.country'].browse(cr, uid, region_id[0], context=context)
            #request.session['website_sale_current_pl'] = region_brw.pricelist_id.id
            #return region_brw
        
        #carrier_external_id=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'delivery_shipwire', 'delivery_carrier_shipwire')[1]
        # warehouse = self.env['stock.warehouse'].search([('name','=','Shipwire Warehouse')])

        
        # create so if needed
        if not sale_order_id and (force_create or code):
            # TODO cache partner_id session
            user_obj = self.env['res.users']
            affiliate_id = request.session.get('affiliate_id')
            salesperson_id = affiliate_id if user_obj.exists(affiliate_id) else request.website.salesperson_id.id
            for w in self:
            	#region_browse = self.pool.get('website.region.country')
                region_id = request.session.get('website_region')
                region_brw = self.env['website.region.country'].browse(region_id)
                company_id = region_brw.company_id
                region_id = region_brw.region_id
                addr = partner.address_get(['delivery', 'invoice'])
                values = {
                	'region_id':region_id.id,
                	'company_id':company_id.id,
                    'partner_id': partner.id,
                    'pricelist_id': pricelist_id,
                    'payment_term_id': partner.property_payment_term_id.id if partner.property_payment_term_id else False,
                    'team_id': w.salesteam_id.id,
                    'partner_invoice_id': addr['invoice'],
                    'partner_shipping_id': addr['delivery'],
                    'user_id': salesperson_id or w.salesperson_id.id,
                    #'carrier_id' : carrier_external_id,
                    'is_shipwire' : True,
                    'warehouse_id' : company_id.virtual_warehouse.id or region_id.shipwire_warehouse.id,
#                     'warehouse_id' : 6,
                }
                sale_order_id = sale_order_obj.create(values)
                request.session['sale_order_id'] = sale_order_id
                sale_order = sale_order_obj.browse(sale_order_id)
                if request.website.partner_id.id != partner.id:
                    partner.write(partner.id, {'last_website_so_id': sale_order_id})

        if sale_order_id:
            # check for change of pricelist with a coupon
            pricelist_id = pricelist_id or partner.property_product_pricelist.id
            '''if sale_order.region_id:
                if sale_order.region_id.id != region_id:
                    values['region_id'] = region_id
                    update_region = True
                else:
                    values['region_id'] =sale_order.region_id.id
                a = sale_order_obj.write(cr, SUPERUSER_ID, [sale_order_id], values, context=context)  '''
             	
            # check for change of partner_id ie after signup
            if sale_order.partner_id.id != partner.id and request.website.partner_id.id != partner.id:
                flag_pricelist = False
                if pricelist_id != sale_order.pricelist_id.id:
                    flag_pricelist = True
                fiscal_position = sale_order.fiscal_position_id and sale_order.fiscal_position_id.id or False

                # change the partner, and trigger the onchange
                # warehouse = self.env['stock.warehouse'].search([('name','=','Shipwire Warehouse')])
                sale_order_id.write({'partner_id': partner.id,'warehouse_id' : company_id.virtual_warehouse.id or region_id.shipwire_warehouse.id }) #'carrier_id':carrier_external_id,
                sale_order_obj.onchange_partner_id()

                # check the pricelist : update it if the pricelist is not the 'forced' one
                values = {}
                if sale_order.pricelist_id:
                    if sale_order.pricelist_id.id != pricelist_id:
                        values['pricelist_id'] = pricelist_id
                        update_pricelist = True
                # if fiscal position, update the order lines taxes
                if sale_order.fiscal_position_id:
                    sale_order._compute_tax_id()

                # if values, then make the SO update
                if values:
                    sale_order_id.write(values)
                
                # check if the fiscal position has changed with the partner_id update
                recent_fiscal_position = sale_order.fiscal_position_id and sale_order.fiscal_position_id.id or False
                if flag_pricelist or recent_fiscal_position != fiscal_position:
                    update_pricelist = True
            if code and code != sale_order.pricelist_id.code:
                pricelist_ids = self.env['product.pricelist'].search([('code', '=', code)], limit=1)
                if pricelist_ids:
                    pricelist_id = pricelist_ids[0]
                    update_pricelist = True
            elif code is not None and sale_order.pricelist_id.code:
                # code is not None when user removes code and click on "Apply"
                pricelist_id = partner.property_product_pricelist.id
                update_pricelist = True

            # update the pricelist
            if update_pricelist:
                request.session['website_sale_current_pl'] = pricelist_id
                #request.session['website_region'] = region
                region_id = request.session.get('website_region')
                region_brw = self.env['website.region.country'].browse(region_id)
                #region_browse = self.pool.get('website.region.country')
                # warehouse = self.env['stock.warehouse'].search([('name','=','Shipwire Warehouse')])
                company_id = region_brw.company_id
                region_id = region_brw.region_id
                values = {'pricelist_id': pricelist_id,'region_id': region_id.id,'company_id':company_id.id,'warehouse_id' : company_id.virtual_warehouse.id or region_id.shipwire_warehouse.id} #'carrier_id':carrier_external_id,
                sale_order.write(values)
                for line in sale_order.order_line:
                    if line.exists():
                        sale_order._cart_update(product_id=line.product_id.id, line_id=line.id, add_qty=0)
                        
                        
        # update browse record
            if (code and code != sale_order.pricelist_id.code) or sale_order.partner_id.id != partner.id or force_pricelist:
                sale_order = sale_order_obj.browse(sale_order.id)
        else:
            request.session['sale_order_id'] = None
            return None
        return sale_order    
        


    # Suggested Products in my cart instead of accessory products - code change
    def _cart_accessories(self):
        for order in self:
            s = set(j.id for l in (order.website_order_line or []) for j in (l.product_id.alternative_product_ids or []) if j.website_published)
            s -= set(l.product_id.id for l in order.order_line)
            product_ids = random.sample(s, min(len(s), 3))
            return self.env['product.product'].browse(product_ids)
            
            
                     
