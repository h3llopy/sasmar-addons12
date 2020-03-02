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

from odoo import api,fields,models
from odoo import SUPERUSER_ID, tools
from odoo.http import request

class product_category(models.Model):
	_inherit='product.public.category'

	include_in_menu = fields.Boolean("Include in Navigation Menu",help="Include in Navigation Menu")
			  
class res_users(models.Model):
	_inherit='res.users'
	
	type = fields.Selection([('consumer', 'Consumer'), ('wholesaler', 'Wholesaler')], string='Types')

# product_category()

class website(models.Model):
	_inherit = 'website'
	
	def get_product_category(self):  
		category_ids=self.env['product.public.category'].search([('parent_id', '=', False),('include_in_menu','!=',False)])
		# print("category_ids=======111==========",category_ids)
		if category_ids and len(category_ids)>8:
			category_ids=category_ids[:8]
		elif category_ids and len(category_ids)<=8:
			category_ids=category_ids

		# print("category_ids======22===========",category_ids)
		# category_data = self.env['product.public.category'].browse(category_ids)
		# print(category_data,"category_data=================",category_ids)
		return category_ids

	def get_product_child_category(self,child_id):
		category_ids=self.env['product.public.category'].search([('parent_id', '=', child_id),('include_in_menu','!=',False)])        
		# print(category_ids,"category_data=================",category_ids)
		# category_data = self.env['product.public.category'].browse(category_ids)
		return category_ids


	def is_category_available(self,pl_id):
		return pl_id in [k.id for ppl in self.get_category_available(show_visible=False)]
		
	def get_category_available(self,show_visible=False):
		categ_ids=self.env['product.public.category'].search([('include_in_menu','!=',False)])
		# return self.env['product.public.category'].browse(categ_ids)
		return categ_ids
		
	def get_current_category(self):
		categ_brw = False
		category_id = request.session.get('website_current_categ')
		category_brw = self.env['product.public.category'].browse(category_id)
		
		if category_brw:
			request.session['website_current_categ'] = category_brw.id
		else:
			categ_ids = self.env['product.public.category'].search([]).ids
			category_brw = self.env['product.public.category'].browse(categ_ids[0])
			request.session['website_current_categ'] = category_brw.id
		
		request.session['website_current_categ'] = category_brw.id
		
		return category_brw
		
	def get_category_filter(self):  
		category_filter_ids=self.env['product.public.category'].search([('include_in_menu','!=',False)])
		# category_filter_data = self.env['product.public.category'].browse(category_filter_ids)
		return category_filter_ids
				
		
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:        
