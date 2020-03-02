# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2014-Today BrowseInfo (<http://www.browseinfo.in>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
import werkzeug

from odoo import SUPERUSER_ID
from odoo import http
from odoo.http import request
from odoo import tools
from odoo.http import request
from odoo.tools.translate import _
from odoo.addons.website_sale.controllers.main import WebsiteSale

PPG = 20 # Products Per Page
PPR = 4  # Products Per Row

# Find Ip address of the machine in python code as well as From that IP adress locate Country & applying on Region code
from geoip import geolite2 # install these 2 packages
#pip install python-geoip
#pip install python-geoip-geolite2

import os





class sasmar_theme(WebsiteSale):

    def get_region(self):
        region = False
        region_obj = request.env['website.region.country']
        #region = region_obj.search(cr, uid, [('country_id.name', '=', 'United States')], context=None)

        self._cr.execute("""SELECT id from website_region_country
            WHERE country_id IN (select id from res_country where name='United States')""")
        all_records = self._cr.fetchall()
        #if all_records:
        region = all_records[0][0]
                        

        region_id = request.session.get('website_region')
        if region_id:
            if isinstance(region_id, (int, long)):
                region_id=[region_id]

            region_brw = request.env['website.region.country'].browse(region_id[0])
            request.session['website_sale_current_pl'] = region_brw.pricelist_id.id
            return region_brw
        else:
            #region = region_obj.search(cr, uid, [('country_id.name', '=', 'United States')], context=None)

            self._cr.execute("""SELECT id from website_region_country
                WHERE country_id IN (select id from res_country where name='United States')""")
            all_records = self._cr.fetchall()
            #if all_records:
            region = all_records[0][0]
                    
            request.session['website_region'] = region
            region_brw = request.env['website.region.country'].browse(region)
            request.session['website_sale_current_pl'] = region_brw.pricelist_id.id
            
            return region_brw

        '''ip_add = request.httprequest.environ["REMOTE_ADDR"] # This Code is working in test/live server
        #ip_add  = os.popen("wget http://ipecho.net/plain -O - -q ; echo").read() # This Code is working in local
        match = geolite2.lookup(ip_add[:-1])
        locate_country= match.get_info_dict().get('country').get('names').get('en')

        region = False
        region_obj = request.env['website.region.country']
        region_ids = region_obj.search(cr, uid, [], context=None)
        regions = region_obj.browse(cr, uid, region_ids, context=None)
        for reg in regions:
            if reg.country_id:
                for country in reg.country_id:
                    if country.name == locate_country:
                        region = reg.id
        return region'''

    def get_attribute_value_ids(self, product):
        currency_obj = request.env['res.currency']
        attribute_value_ids = []
        visible_attrs = set(l.attribute_id.id
                                for l in product.attribute_line_ids
                                    if len(l.value_ids) > 1)
        if request.website.pricelist_id.id != context['pricelist']:
            website_currency_id = request.website.currency_id.id
            currency_id = self.get_pricelist().currency_id.id
            for p in product.product_variant_ids:
                price = currency_obj.compute(website_currency_id, currency_id, p.lst_price)
                attribute_value_ids.append([p.id, [v.id for v in p.attribute_value_ids if v.attribute_id.id in visible_attrs], p.price, price])
        else:
            attribute_value_ids = [[p.id, [v.id for v in p.attribute_value_ids if v.attribute_id.id in visible_attrs], p.price, p.lst_price]
                for p in product.product_variant_ids]

        return attribute_value_ids

    @http.route(['/shop/change_region/<model("website.region.country"):region_id>'], type='http', auth="public", website=True)
    def region_change(self, region_id, **post):
        if request.session and request.session.get('website_region'):
            if request.website.is_region_available(region_id.id):
                request.session['website_region'] = region_id.id
                region_brw = request.env['website.region.country'].browse(region_id.id)
                request.session['website_sale_current_pl'] = region_brw.pricelist_id.id
                request.website.sale_get_order(force_region=region_id.id, force_pricelist=region_brw.pricelist_id.id)
                return request.redirect(request.httprequest.referrer or '/shop')

        else:
            if request.website.is_region_available(region_id.id, context=request.context):
            	#region = region_obj.search(cr, uid, [('country_id.name', '=', 'United States')], context=None)
                request.session['website_region'] = region_id.id
                region_brw = request.env['website.region.country'].browse(region_id.id)
                request.session['website_sale_current_pl'] = region_brw.pricelist_id.id
                request.website.sale_get_order(force_region=region_id.id,force_pricelist=region_brw.pricelist_id.id)
            return request.redirect(request.httprequest.referrer or '/shop')

    @http.route(['/shop/cart'], type='http', auth="public", website=True)
    def cart(self, **post):
        if not context.get('region'):
            region = self.get_region()
            context['region'] = int(region)
        else:
            region = request.env['website.region.country'].browse(context['region']).id

        order = request.website.sale_get_order()

        if order:
            from_currency = order.company_id.currency_id
            to_currency = order.pricelist_id.currency_id
            compute_currency = lambda price: request.env['res.currency']._compute(from_currency, to_currency, price)
        else:
            compute_currency = lambda price: price

        values = {
            'website_sale_order': order,
            'compute_currency': compute_currency,
            'suggested_products': [],
        }
        if order:
            _order = order
            if not context.get('pricelist'):
                _order = order.with_context(pricelist=order.pricelist_id.id)
            values['suggested_products'] = _order._cart_accessories()

        if post.get('type') == 'popover':
            return request.render("website_sale.cart_popover", values)

        if post.get('code_not_available'):
            values['code_not_available'] = post.get('code_not_available')

        return request.render("website_sale.cart", values)


# When Payment done from backend create sales order instead of Quatation

    @http.route('/shop/payment/validate', type='http', auth="public", website=True)
    def payment_validate(self, transaction_id=None, sale_order_id=None, **post):
        """ Method that should be called by the server when receiving an update
        for a transaction. State at this point :

         - UDPATE ME
        """
        email_act = None
        sale_order_obj = request.env['sale.order']

        if transaction_id is None:
            tx = request.website.sale_get_transaction()
        else:
            tx = request.env['payment.transaction'].browse(transaction_id)

        if sale_order_id is None:
            order = request.website.sale_get_order()
        else:
            order = request.env['sale.order'].browse(sale_order_id)
            assert order.id == request.session.get('sale_last_order_id')

        if not order or (order.amount_total and not tx):
            return request.redirect('/shop')

        if (not order.amount_total and not tx) or tx.state in ['pending', 'done']:
            #if (not order.amount_total and not tx):
                # Orders are confirmed by payment transactions, but there is none for free orders,
                # (e.g. free events), so confirm immediately
            order.with_context(dict(context, send_email=True)).action_confirm()
            order.force_quotation_send() # Send Mail when order placed from webshop
        elif tx and tx.state == 'cancel':
            # cancel the quotation
            order.action_cancel()

        # clean context and session, then redirect to the confirmation page
        request.website.sale_reset(context=context)
        if tx and tx.state == 'draft':
            return request.redirect('/shop')
        return request.redirect('/shop/confirmation')



    #this is for click on shop menu, region will be called
    '''@http.route(['/shop/page'], type='http', auth="public", website=True)
    def comments(self, page=0, category=None, search='', **post):
    	cr, uid, context, pool = request.cr, request.uid, request.context, request.env

    	ip_add  = os.popen("wget http://ipecho.net/plain -O - -q ; echo").read()
    	match = geolite2.lookup(ip_add[:-1])
    	locate_country= match.get_info_dict().get('country').get('names').get('en')
    	print "!!!!!!!!!!!!!!!!!!!!!!! locate_country !!!!!!!!!!!!!!!!!!!!!!",locate_country

    	region = False
    	region_obj = request.env['website.region']
        region_ids = region_obj.search(cr, uid, [], context=context)
        regions = region_obj.browse(cr, uid, region_ids, context=context)
        for reg in regions:
        	print reg.name
        	if reg.country_id:
        		for country in reg.country_id:
        			if country.name == locate_country:
        				region = reg

    	return request.redirect('/shop')'''
