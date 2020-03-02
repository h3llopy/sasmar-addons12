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

import werkzeug
import datetime

from odoo import SUPERUSER_ID
from odoo.http import request,route
from odoo import http
from odoo import tools
from odoo.http import request
from odoo.tools.translate import _

class website_sample_request(http.Controller):

	
	@http.route(['/sample'], type='http', auth="public", website=True)
	def sample(self, page=0, category=None, search='', **post):
		return http.request.render("website_sample_request.sample")
	
			
	@http.route(['/sample/request/<int:product_id>'], type='http', auth="public", website=True)
	def sample_request(self, **post):
		abc = request.httprequest.url.split('/')
		product_id = int(abc[-1])
		#product = request.env['product.template'].browse(cr,uid,product_id,context=context)
		#values = {'product_id':product_id}
		values = {
				'product_id' : product_id,
		}
		return http.request.render("website_sample_request.sample_request",values)

	
	mandatory_request_fields = ["country_id","fname","email","product_id","lname","address","city","pin","age","gender"]
	
	def _get_mandatory_request_fields(self):
		return self.mandatory_request_fields
		
	def sample_confirm_validate(self, data):
		error = dict()
		error_message = []

		# Validation
		for field_name in self._get_mandatory_request_fields():
			if not data.get(field_name):
				error[field_name] = 'missing'

		# error message for empty required fields
		if [err for err in error.values() if err == 'missing']:
			error_message.append(_('Some required fields are empty.'))

		return error, error_message
		
	@http.route(['/sample/confirm'], type='http', auth="public", website=True)
	def sample_confirm(self, **post):
		#product = self.sample_request()
		sample_obj = request.env['product.sample.request']
		
		product_obj = request.env['product.product']
		country_obj = request.env['res.country']
		state_obj = request.env['res.country.state']
		
		country_ids = country_obj.search([])
		countries = country_obj.browse(country_ids)
		states_ids = state_obj.search([])
		states = state_obj.browse(states_ids)

		
		fname = post['fname']
		lname = post['lname']
		address = post['address']
		city = post['city']
		pin = post['pin']
		country_id = post['country_id']
		state_id = post['state_id']
		age = post['age']
		email = post['email']
		gender = post['gender']
		product_id = post['product_id']
		
		
		
		vals = {'fname':fname,'lname':lname,'address':address,'city': city, 'pin': pin, 'country_id': country_id, 'state_id': state_id, 'age' : age,'email' : email, 'gender' : gender,'product_id':product_id} #,'address':address, 'countries': countries, 'states': states
		
		vals["error"], vals["error_message"] = self.sample_confirm_validate(vals)
		
		if vals["error"]:
			return http.request.render("website_sample_request.sample_request", vals)
			
		sample_create = sample_obj.create(vals)
		massmail_list_obj = request.env['mail.mass_mailing.list']
		massmail_list_srch = massmail_list_obj.search([('name','=','FREE SAMPLE')])
		if massmail_list_srch:
			mail_mass_mailing_contact_obj = request.env['mail.mass_mailing.contact'].create({
							'email':post['email'],
							'name':post['fname'],
							'list_id':massmail_list_srch[0],
							'create_date':datetime.datetime.now()
			})

		template_id = request.env['ir.model.data'].get_object_reference(
															  'website_sample_request',
															  'email_template_sample_request')[1]
		email_template_obj = request.env['mail.template'].browse(template_id)
		if template_id:
			values = email_template_obj.sudo().generate_email(sample_create.id, fields=None)
			values['email_to'] = post['email']
			values['res_id'] = False
			mail_mail_obj = request.env['mail.mail']
			msg_id = mail_mail_obj.sudo().create(values)
			if msg_id:
				sends = mail_mail_obj.sudo().send([msg_id])
								
		return http.request.render("website_sample_request.sample_thankyou")

	@http.route(['/thank-you/<model("product.sample.request"):sample>'], type='http', auth="public", website=True)
	def thank_you(self, sample, page=0, category=None, search='', **post):
		sample_obj = request.env['product.sample.request']
		abc = request.httprequest.url.split('/')
		if '-' in abc[-1]:
			bcd = abc[-1].split('-')
			if bcd:
				w_id = int(bcd[-1])
				brw_id = sample_obj.browse(w_id)
				brw_id.update({'state':'confirm'})
		return http.request.render("website_sample_request.request_thankyou")
		
		
		

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
