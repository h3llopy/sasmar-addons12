# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses odoo, Open Source Management Solution Framework.
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

from odoo import api,fields,models
from datetime import date
from odoo import SUPERUSER_ID, tools
import odoo.addons.decimal_precision as dp
from odoo.tools.float_utils import float_round, float_compare
from odoo.http import request
import itertools

class product_tags(models.Model):
    _name = "product.tags"

    name = fields.Char('Product Tags', required=True)

    
class product_template(models.Model):
    _inherit = "product.template"

    featured_products = fields.Boolean('Featured Products',default=False)
    popular_products = fields.Boolean('Most Popular Products',default=False)
    pack_price = fields.Float(compute='_product_pack_price', string='Pack Price')
    pack_new_price = fields.Float(string="Pack")    
    
    def _product_pack_price(self,ids):
        if request.session.get('website_sale_current_pl'):
            current_pl = request.session['website_sale_current_pl']
            for id in ids:
                price_unit = 0.0
                prod_tmpl_record = self.browse(ids[0])
                val = {}
                list_of_pack_product = []
                if prod_tmpl_record.is_pack == True:
                    product_search_list = []
                    for pack_pro in prod_tmpl_record.pack_ids:
                        pack_record = self.env['product.pack'].browse(pack_pro.id)
                        product_search_list.append(pack_record.product_id.product_tmpl_id.id)
                        
                    
                    pricelist_item = self.env['product.pricelist.item'].search([('pricelist_id','=',current_pl),('product_tmpl_id','in',product_search_list)])
                    pricelist_item_obj = self.env['product.pricelist.item'].browse(pricelist_item)
        
                    for pack_pro in prod_tmpl_record.pack_ids:
                        list_of_pack_product.append(pack_pro.id)
                        
                    for price,qty in zip(pricelist_item_obj,list_of_pack_product):
                        
                        pack_product = self.env['product.pack'].browse(qty)
                        price_unit =price_unit + (price.fixed_price * pack_product.qty_uom)
                        
                    prod_tmpl_record['pack_new_price'] = price_unit
                    
                    val[prod_tmpl_record.id] = price_unit
                return val
        else:
            if request.session.get('website_sale_current_pl'):
                current_pl = request.session['website_sale_current_pl']
                for id in ids:
                    price_unit = 0.0
                    prod_tmpl_record = self.browse(ids[0])
                    val = {}
                    list_of_pack_product = []
                    if prod_tmpl_record.is_pack == True:
                        product_search_list = []
                        for pack_pro in prod_tmpl_record.pack_ids:
                            pack_record = self.env['product.pack'].browse(pack_pro.id)
                            product_search_list.append(pack_record.product_id.product_tmpl_id.id)
                            
                        pricelist_item = self.env['product.pricelist.item'].search([('pricelist_id','=',current_pl),('product_tmpl_id','in',product_search_list)])
                        pricelist_item_obj = self.env['product.pricelist.item'].browse(pricelist_item)
            
                        prod_tmpl_record['pack_new_price'] = price_unit
                        
                        val[prod_tmpl_record.id] = price_unit
                    return val
    

class website(models.Model):
    _inherit = 'website'

#     def pack_pricelist(self,cr,uid,ids,context=None):
#         product_pack = self.pool.get('product.template').search(cr,uid,[('is_pack','=',True)],context=context)
#         print "0000product_pack00000000product_pack00000000000000000000",product_pack
#         for pack in product_pack:
#             pack_record = self.pool.get('product.template').browse(cr,uid,pack,context=context)
#             print "----------pack_record----------------",pack_record
#             print "--------pack_record.pack_ids------------------",pack_record.pack_ids
#             for pack in pack_record.pack_ids:
#                 print "----------pack_record.pack_ids.product_id.list_price----------------",pack.product_id.list_price
#                 
#             product_pack = self.pool.get('product.pack').browse(cr,uid,pack_record.pack_ids.product_id,context=context)
#             print ".........................................",product_pack
#         return product_pack
            
    '''def _website_product_id_change(self, cr, uid, ids, order_id, product_id, qty=0, context=None):
        context = dict(context or {})
        order = self.pool['sale.order'].browse(cr, SUPERUSER_ID, order_id, context=context)
        pro_record = self.pool.get('product.product').browse(cr,uid,product_id,context=context)
        pro_tmpl = self.pool['product.template'].browse(cr, SUPERUSER_ID, pro_record.product_tmpl_id.id, context=context)
        product_context = context.copy()
        vals = {}
        if pro_tmpl.is_pack:
            product_context.update({
                'lang': order.partner_id.lang,
                'partner': order.partner_id.id,
                'quantity': qty,
                'date': order.date_order,
                'pricelist': order.pricelist_id.id,
                'price_unit' : pro_tmpl.pack_new_price,
            })
        else:
            product_context.update({
                'lang': order.partner_id.lang,
                'partner': order.partner_id.id,
                'quantity': qty,
                'date': order.date_order,
                'pricelist': order.pricelist_id.id,
            })
        product = self.pool['product.product'].browse(cr, uid, product_id, context=product_context)
        if pro_tmpl.is_pack:
            values = {
                'product_id': product_id,
                'name': product.display_name,
                'product_uom_qty': qty,
                'order_id': order_id,
                'product_uom': product.uom_id.id,
                'price_unit': pro_tmpl.pack_new_price,
            }
        else:
            values = {
                'product_id': product_id,
                'name': product.display_name,
                'product_uom_qty': qty,
                'order_id': order_id,
                'product_uom': product.uom_id.id,
                'price_unit': product.price,
            }
        if product.description_sale:
            values['name'] += '\n' + product.description_sale
        return values
           
    def get_featured_products(self, cr, uid,ids, context=None):  
        uid=SUPERUSER_ID      
        prod_ids=self.pool.get('product.template').search(cr, uid, [('featured_products','=','True'),("sale_ok", "=", True)], context=context)
        if prod_ids and len(prod_ids)>20:
            prod_ids=prod_ids[:20]
        elif prod_ids and len(prod_ids)<=20:
            prod_ids=prod_ids
        price_list=self.price_list_get();
        product_data = self.pool.get('product.template').browse(prod_ids})
        return product_data   

    def price_list_get(self):
            pricelist_id = request.website.get_current_pricelist().id
            return pricelist_id '''        
        
    def get_popular_products(self):          
        prod_ids=self.env['product.template'].search([('popular_products','=','True'),("sale_ok", "=", True)])
        if prod_ids and len(prod_ids)>20:
            prod_ids=prod_ids[:20]
        elif prod_ids and len(prod_ids)<=20:
            prod_ids=prod_ids
        price_list=self.get_current_pricelist();
        product_data = self.env['product.template'].browse(prod_ids)
        return product_data       

    
class sale_order(models.Model):
    _inherit = 'sale.order'

    '''def _website_product_id_change(self, cr, uid, ids, order_id, product_id, qty=0, context=None):
        context = dict(context or {})
        order = self.pool['sale.order'].browse(cr, SUPERUSER_ID, order_id, context=context)
        pro_record = self.pool.get('product.product').browse(cr,uid,product_id,context=context)
        pro_tmpl = self.pool['product.template'].browse(cr, SUPERUSER_ID, pro_record.product_tmpl_id.id, context=context)
        product_context = context.copy()
        vals = {}
        if pro_tmpl.is_pack:
            product_context.update({
                'lang': order.partner_id.lang,
                'partner': order.partner_id.id,
                'quantity': qty,
                'date': order.date_order,
                'pricelist': order.pricelist_id.id,
                'price_unit' : pro_tmpl.pack_new_price,
            })
        else:
            product_context.update({
                'lang': order.partner_id.lang,
                'partner': order.partner_id.id,
                'quantity': qty,
                'date': order.date_order,
                'pricelist': order.pricelist_id.id,
            })
        product = self.pool['product.product'].browse(cr, uid, product_id, context=product_context)
        if pro_tmpl.is_pack:
            values = {
                'product_id': product_id,
                'name': product.display_name,
                'product_uom_qty': qty,
                'order_id': order_id,
                'product_uom': product.uom_id.id,
                'price_unit': pro_tmpl.pack_new_price,
            }
        else:
            values = {
                'product_id': product_id,
                'name': product.display_name,
                'product_uom_qty': qty,
                'order_id': order_id,
                'product_uom': product.uom_id.id,
                'price_unit': product.price,
            }
        if product.description_sale:
            values['name'] += '\n' + product.description_sale
        return values'''
     

        
# For Registration page

class res_users(models.Model):
    _inherit = 'res.users'
    
    def signup(self,values,token=None):
        """ signup a user, to either:
            - create a new user (no token), or
            - create a user for a partner (with token, but no user for partner), or
            - change the password of a user (with token, and existing user).
            :param values: a dictionary with field values that are written on user
            :param token: signup token (optional)
            :return: (dbname, login, password) for the signed up user
        """
        if token:
            # signup with a token: find the corresponding partner id
            res_partner = self.pool.get('res.partner')
            partner = res_partner._signup_retrieve_partner(
                    token, check_validity=True, raise_exception=True)
            # invalidate signup token
            partner.write({'signup_token': False, 'signup_type': False, 'signup_expiration': False})

            partner_user = partner.user_ids and partner.user_ids[0] or False

            # avoid overwriting existing (presumably correct) values with geolocation data
            if partner.country_id or partner.zip or partner.city:
                values.pop('city', None)
                values.pop('country_id', None)
            if partner.lang:
                values.pop('lang', None)

            if partner_user:
                # user exists, modify it according to values
                values.pop('login', None)
                values.pop('name', None)
                partner_user.write(values)
                return (partner_user.login, values.get('password'), values.get('type'))
            else:
                # user does not exist: sign up invited user
                values.update({
                    'name': partner.name,
                    'partner_id': partner.id,
                    'email': values.get('email') or values.get('login'),
                })
                if partner.company_id:
                    values['company_id'] = partner.company_id.id
                    values['company_ids'] = [(6, 0, [partner.company_id.id])]
                self._signup_create_user(values)
        else:
            # no token, sign up an external user
            values['email'] = values.get('email') or values.get('login')
            region = request.session.get('website_region')
            region_browse = self.env['website.region.country'].browse(region)
            res = self._signup_create_user(values)
            # this custom code is for set company_id when creating new user 
            user_browse = self.env['res.users'].browse(res)
            user_browse.company_ids = [(4,region_browse.company_id.id)]
            user_browse.company_id = region_browse.company_id.id
        return (values.get('login'), values.get('password'),values.get('type'))    

# This code is for current region,pricelist will be applied in particular res.partner when you click on signup button
class res_partner(models.Model):
    _inherit = 'res.partner'
    
    def create(self,values):
        # if self._context is None:
        #     context = {}
        if request.session and request.session.get('website_region'):
            
            reg_country = request.session.get('website_region') or request.session.get('website_region') and request.session.get('website_region')[0]
            if not isinstance(reg_country, int):
                reg_country = reg_country[0]
            values.update({'property_product_pricelist':request.session.get('website_sale_current_pl'),'website_pricelist_id':request.session.get('website_sale_current_pl'), 'region_country_id':reg_country})
            
        return super(res_partner, self).create(values)
 
    
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
