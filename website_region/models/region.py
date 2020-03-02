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

from datetime import date
from odoo.addons.website.models.website import slugify
from odoo import api, fields, models, _
from odoo import SUPERUSER_ID, tools
from odoo.tools.translate import _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from odoo.http import request

from geoip import geolite2
import os
from socket import gethostname, gethostbyname

class website_region(models.Model):
    _name = "website.region"
    _description = "When region has been selected that particular pricelist has been applied on webshop, and once order has been placed this price-list linked to webshop"

    name = fields.Char('Region Name', required=True)

class website_region_country(models.Model):
    _name = "website.region.country"
    _description = "When region has been selected that particular pricelist has been applied on webshop, and once order has been placed this price-list linked to webshop"
    _rec_name = 'country_id'

    @api.model
    def _get_language(self):
        langs = self.env['res.lang'].search([('translatable', '=', True)])
        return [(lang.code, lang.name) for lang in langs]

    pricelist_id = fields.Many2one('product.pricelist', string="Pricelist", required=True)
    flag_image = fields.Binary('Flag Image')
    company_id = fields.Many2one('res.company', string="Company", required=True)
    country_id = fields.Many2one('res.country',  string='Country',required=True)
    region_id = fields.Many2one('website.region',  string='Region',required=True)
    lang = fields.Selection('_get_language', string='Language')

    @api.one
    @api.constrains('country_id')
    def _check_unique_constraints(self):
        if len(self.search([('country_id', '=', self.country_id.name)])) > 1:
            raise ValidationError("Country already exists.")



class SaleOrder(models.Model):
    _inherit = "sale.order"

    region_id = fields.Many2one('website.region', string='Region', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="region for current sales order.")


class ResPartner(models.Model):
    _inherit = "res.partner"

    website_pricelist_id = fields.Many2one('product.pricelist', string='Website Pricelist', help="Website Pricelist for selected Partner")
    region_country_id = fields.Many2one('website.region.country', string='Region/Country', help="Country for selected Partner")


class website(models.Model):
    _inherit = 'website'



    def is_region_available(self,r_id):
        """ Return a boolean to specify if a specific pricelist can be manually set on the website.
        Warning: It check only if pricelist is in the 'selectable' pricelists or the current pricelist.

        :param int pl_id: The pricelist id to check

        :returns: Boolean, True if valid / available
        """
        return r_id in [ppl.id for ppl in self.get_region_available(show_visible=False)]


    def get_region_available(self,show_visible=False):
        #region_ids=self.pool.get('website.region.country').search(cr, uid,[], context=context)

        self._cr.execute("""SELECT id from website_region_country""")
        region_ids = self._cr.fetchall()
                    

        isocountry = request.session.geoip and request.session.geoip.get('country_code') or False

        user_id = self.env['res.users'].browse(request.uid or self.env.user)
        pl_ids = self._get_pl(isocountry, show_visible,
                              user_id.partner_id.property_product_pricelist.id,
                              request.session.get('website_sale_current_pl'),
                              self.get_pricelist_available())
        return self.env['website.region.country'].browse(region_ids)

    def get_current_region(self):
                
        region = False
        region_obj = request.env['website.region.country']
        region_id = request.session.get('website_region')
        
        #request.session['website_region'] = region
        
        if self.env.user != request.website.user_id.id:
            region_id = request.session.get('website_region')
            user_browse = self.env['res.users'].browse(self.env.user.id)
            partner_browse = self.env['res.partner'].browse(user_browse.partner_id.id)
            region_brw = self.env['website.region.country'].browse(partner_browse.region_country_id.id)
            if region_brw:
                request.session['website_region'] = partner_browse.region_country_id.id
            else:
                #region = region_obj.search(cr, uid, [('country_id.name', '=', 'United States')], context=None)
                self._cr.execute("""SELECT id from website_region_country
                    WHERE country_id IN (select id from res_country where name='United States')""")
                all_records = self._cr.fetchall()
                #if all_records:
                region = all_records[0][0]
                    
                region_brw = self.env['website.region.country'].browse(region)
                
            request.session['website_sale_current_pl'] = partner_browse.website_pricelist_id and partner_browse.website_pricelist_id.id or region_brw.pricelist_id.id
            request.session['website_region'] = region_brw.id
            
            # language code
            # res_user_obj = self.env['res.users'].browse(self.env.user.id)
            # lang = region_brw.lang
            # if lang == False:
            #     lang = 'en_US'
            # print("############################",request.context)
            # request.context.update({'lang':lang})
        
            # res_user_obj.lang = lang             
            
            return region_brw
            
        else:
            '''ip_add  = os.popen("wget http://ipecho.net/plain -O - -q ; echo").read() # This Code is working in local
            #ip_add = request.httprequest.environ["REMOTE_ADDR"] # This Code is working in test/live server
            if ip_add and len(ip_add) > 1:
                match = geolite2.lookup(ip_add[:-1])
                if match:
                    locate_country= match.get_info_dict().get('country').get('names').get('en')
                    region_ids = region_obj.search(cr, uid, [], context=None)
                    for region_brw in region_obj.browse(cr, uid, region_ids, context=None):
                        if locate_country == region_brw.country_id.name:
                            region=region_brw
                            break
                    if not region:
                        region = region_obj.search(cr, uid, [('country_id.name', '=', 'United States')], context=None)
                        region_brw = region_obj.browse(cr, uid, region[0], context=None)
                            
                else:
                    region = region_obj.search(cr, uid, [('country_id.name', '=', 'United States')], context=None)
                    region_brw = region_obj.browse(cr, uid, region[0], context=None)
            else:
                region = region_obj.search(cr, uid, [('country_id.name', '=', 'United States')], context=None)
                region_brw = region_obj.browse(cr, uid, region[0], context=None)
            request.session['website_sale_current_pl'] = region_brw.pricelist_id.id'''

            #region = region_obj.search(cr, uid, [('country_id.name', '=', 'United States')], context=None)
            
            self._cr.execute("""SELECT id from website_region_country
                WHERE country_id IN (select id from res_country where name='United States')""")
            all_records = self._cr.fetchall()
            region = all_records[0][0]
                                
            region_id = request.session.get('website_region')
            if region_id:
                if isinstance(region_id, (int, long)):
                    region_id=[region_id]
    
                region_brw = self.env['website.region.country'].browse(region_id[0])
                request.session['website_sale_current_pl'] = region_brw.pricelist_id.id
            
                # language code
                '''res_user_obj = self.pool['res.users'].browse(cr, SUPERUSER_ID, uid, context=context)
                lang = region_brw.lang
                if lang == False:
                    lang = 'en_US'
                request.context.update({'lang':lang})
                
                res_user_obj.lang = lang'''
                
                return region_brw
            else:
                #region = region_obj.search(cr, uid, [('country_id.name', '=', 'United States')], context=None)

                self._cr.execute("""SELECT id from website_region_country
                    WHERE country_id IN (select id from res_country where name='United States')""")
                all_records = self._cr.fetchall()
                #if all_records:
                region = all_records[0][0]
                
                request.session['website_region'] = region
                region_brw = self.env['website.region.country'].browse(region)
                request.session['website_sale_current_pl'] = region_brw.pricelist_id.id
            
                # language code
                '''res_user_obj = self.pool['res.users'].browse(cr, SUPERUSER_ID, uid, context=context)
                lang = region_brw.lang
                if lang == False:
                    lang = 'en_US'
                request.context.update({'lang':lang})
            
                res_user_obj.lang = lang'''

                return region_brw
#        region_browse = region_obj.browse(cr, uid, region,context=context)
#        pricelist_id = region_browse.pricelist_id.id
#        request.session['website_region'] = pricelist_id



    def get_region_category(self):
        list_of_region = []
        #region_ids=self.pool.get('website.region.country').search(cr, uid,[], context=context)

        self._cr.execute("""SELECT id from website_region_country""")
        region_ids = self._cr.fetchall()
        
        for region_id in region_ids:
            region_data = self.env['website.region.country'].browse(region_id)
            if region_data.region_id.id not in list_of_region:
                list_of_region.append(region_data.region_id.id)

                '''cr.execute("""SELECT id from website_region
                    WHERE id IN %s""",(tuple(list_of_region),))
                all_records = cr.fetchall()
                if all_records:
                    regions_ids = all_records
                    print "11111111111111111 rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr",regions_ids'''
                    
            #regions_ids=self.pool.get('website.region').search(cr, SUPERUSER_ID, [('id','in',list_of_region)], context=context)
            regions_data = self.env['website.region'].browse(list_of_region)
        return regions_data

    def get_region_child_category(self,country_id):
        #country_ids=self.pool.get('website.region.country').search(cr,uid,[('region_id', '=', country_id)])
        
        self._cr.execute("""SELECT id from website_region_country WHERE region_id IN (select id from website_region where id=%s)""",([country_id]))
        all_records = self._cr.fetchall()
        if all_records:
            country_ids = all_records
            country_list = []
            for country in country_ids:
                country_list.append(country[0])
            country_data = self.env['website.region.country'].browse(country_list)
            return country_data


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
