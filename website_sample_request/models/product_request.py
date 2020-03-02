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

from odoo import fields, models, api, _
from odoo.exceptions import UserError
import werkzeug


class ProductTemplate(models.Model):
    _inherit = "product.template"    
    
    def sample_product_publish_button(self,context):
        for rec in self.browse(context['params'].get('id')):
            rec.update({'website_publish': not rec.website_publish})
        return True
    
    sample_products = fields.Boolean('Sample Products',default=False)
    website_publish = fields.Boolean('Published',default=False)

class res_sample_country(models.Model):
    _inherit = 'res.country'
    
    is_sample_country = fields.Boolean('Sample Country')
            
class SampleRequest(models.Model):
    _name = 'product.sample.request'
    _rec_name = 'fname' 
        
    fname = fields.Char('First Name', required=True)
    lname = fields.Char('Last Name', required=True)
    address = fields.Char('Address')
    city = fields.Char('City')
    pin = fields.Char('Zip')
    country_id = fields.Many2one('res.country','Country')
    state_id = fields.Many2one('res.country.state','State')
    age = fields.Selection([('18_25','18 to 25'), ('26_35','26 to 35'), ('36_45','36 to 45'), ('46','46+')], 'Age')
    email = fields.Char('Email', required=True)
    gender = fields.Selection([('male','Male'), ('female','Female'), ('other','Other')], 'Gender')
    product_id = fields.Many2one('product.template','Product', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ], string='Status', readonly=True, copy=False, index=True, default='draft')
            

class Website(models.Model):
    _inherit = 'website'
        
    def get_sample_products(self):   
        sample_ids = self.env['product.template'].search([('sample_products','=','True'), ("website_published", "=", True), ("website_publish", "=", True)])
        return sample_ids    

    def get_country_list(self):            
        country_ids=self.env['res.country'].search([('is_sample_country','=',True)])   
        return country_ids
        
    def get_state_list(self):            
        state_ids=self.env['res.country.state'].search([])
        return state_ids
        
    def get_product_list(self):            
        product_ids=self.env['product.template'].search([('sample_products','=','True'), ("website_published", "=", True), ("website_publish", "=", True)])        
        return product_ids
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
