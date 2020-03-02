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

# -*- coding: utf-8 -*-
import werkzeug
import odoo
from odoo import addons
from odoo import SUPERUSER_ID
from odoo.http import request,route
from odoo import http
from odoo.addons.http_routing.models.ir_http import slug, unslug_url
import odoo.http as http
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.website_sale.controllers.main import WebsiteSale
import werkzeug.urls
import werkzeug.wrappers
from odoo.tools import pycompat, OrderedSet

import odoo.addons.auth_signup.controllers.main as main  # add library for Registration page

import re
PPG = 16 # Products Per Page
PPR = 2  # Products Per Row

class TableCompute(object):
	def __init__(self):
		self.table = {}

	def _check_place(self, posx, posy, sizex, sizey):
		res = True
		for y in range(sizey):
			for x in range(sizex):
				if posx+x>=PPR:
					res = False
					break
				row = self.table.setdefault(posy+y, {})
				if row.setdefault(posx+x) is not None:
					res = False
					break
			for x in range(PPR):
				self.table[posy+y].setdefault(x, None)
		return res

	def process(self, products, ppg=PPG):
		# Compute products positions on the grid
		minpos = 0
		index = 0
		maxy = 0
		for p in products:
			x = min(max(p.website_size_x, 1), PPR)
			y = min(max(p.website_size_y, 1), PPR)
			if index>=ppg:
				x = y = 1

			pos = minpos
			while not self._check_place(pos%PPR, pos/PPR, x, y):
				pos += 1
			# if 21st products (index 20) and the last line is full (PPR products in it), break
			# (pos + 1.0) / PPR is the line where the product would be inserted
			# maxy is the number of existing lines
			# + 1.0 is because pos begins at 0, thus pos 20 is actually the 21st block
			# and to force python to not round the division operation
			if index >= ppg and ((pos + 1.0) / PPR) > maxy:
				break

			if x==1 and y==1:   # simple heuristic for CPU optimization
				minpos = pos/PPR

			for y2 in range(y):
				for x2 in range(x):
					self.table[(pos/PPR)+y2][(pos%PPR)+x2] = False
			self.table[pos/PPR][pos%PPR] = {
				'product': p, 'x':x, 'y': y,
				'class': " ".join(map(lambda x: x.html_class or '', p.website_style_ids))
			}
			if index<=ppg:
				maxy=max(maxy,y+(pos/PPR))
			index += 1

		# Format table according to HTML needs
		rows = sorted(self.table.items())
		rows = [r[1] for r in rows]
		for col in range(len(rows)):
			cols = sorted(rows[col].items())
			x += len(cols)
			rows[col] = [r[1] for r in cols if r[1]]

		return rows

		# TODO keep with input type hidden


class QueryURL(object):
	def __init__(self, path='', path_args=None, **args):
		self.path = path
		self.args = args
		self.path_args = OrderedSet(path_args or [])

	def __call__(self, path=None, path_args=None, **kw):
		path = path or self.path
		for key, value in self.args.items():
			kw.setdefault(key, value)
		path_args = OrderedSet(path_args or []) | self.path_args
		paths, fragments = {}, []
		for key, value in kw.items():
			if value and key in path_args:
				if isinstance(value, models.BaseModel):
					paths[key] = slug(value)
				else:
					paths[key] = u"%s" % value
			elif value:
				if isinstance(value, list) or isinstance(value, set):
					fragments.append(werkzeug.url_encode([(key, item) for item in value]))
				else:
					fragments.append(werkzeug.url_encode([(key, value)]))
		for key in path_args:
			value = paths.get(key)
			if value is not None:
				path += '/' + key + '/' + value
		if fragments:
			path += '?' + '&'.join(fragments)
		return path


def get_pricelist():
	return request.website.get_current_pricelist()
  

	  
class ProductBundle(WebsiteSale):

	# @http.route([
	# 	'''/shop''',
	# 	'''/shop/page/<int:page>''',
	# 	'''/shop/category/<model("product.public.category", "[('website_id', 'in', (False, current_website_id))]"):category>''',
	# 	'''/shop/category/<model("product.public.category", "[('website_id', 'in', (False, current_website_id))]"):category>/page/<int:page>'''
	# ], type='http', auth="public", website=True)
	# def shop(self, page=0, category=None, search='', ppg=False, **post):
	# 	add_qty = int(post.get('add_qty', 1))
	# 	if ppg:
	# 		try:
	# 			ppg = int(ppg)
	# 		except ValueError:
	# 			ppg = PPG
	# 		post["ppg"] = ppg
	# 	else:
	# 		ppg = PPG

	# 	attrib_list = request.httprequest.args.getlist('attrib')
	# 	attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
	# 	attributes_ids = set([v[0] for v in attrib_values])
	# 	attrib_set = set([v[1] for v in attrib_values])

	# 	domain = self._get_search_domain(search, category, attrib_values)

	# 	keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list)
		
	# 	pricelist_context, pricelist = self._get_pricelist_context()
	# 	request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

	# 	# url = "/shop"
	# 	# if search:
	# 	#     post["search"] = search
	# 	# if attrib_list:
	# 	#     post['attrib'] = attrib_list

	# 	Product = request.env['product.template'].with_context(bin_size=True)

	# 	product_template_ids = []    
	# 	# if not request._context.get('pricelist'):
	# 	# 	pricelist = request.website.get_current_pricelist()
	# 	# 	request._context['pricelist'] = int(pricelist)
	# 	# 	# pricelist products shows in shop page, 
	# 	# 	pricelist_ids = request.env['product.pricelist.item'].search([('pricelist_id','=',pricelist.id)])
			
			
	# 	# 	for product_tmpl in pricelist_ids:
	# 	# 		product_tmpl_obj = request.env['product.pricelist.item'].browse(product_tmpl).product_tmpl_id.id
	# 	# 		product_template_ids.append(product_tmpl_obj)
				
	# 	# 	pricelist_item_obj = pool.get('product.pricelist.item').browse(cr,uid,ids,context=context)
	# 	#    pack_list = {}
	# 	#    list_of_pricelist_item = []
	# 	#    price_unit = 0.0
	# 	#    product_pack = pool.get('product.template').search(cr,uid,[('is_pack','=',True)],context=context)
	# 	#    for pack in product_pack:
	# 	# 	   item_price=0.00
	# 	# 	   pack_obj = pool.get('product.template').browse(cr, uid, pack, context=context)
	# 	# 	   for pack_item in pack_obj.pack_ids:
	# 	# 		   pack_obj = pool.get('product.pack').browse(cr, uid, pack_item.id, context=context)
	# 	# 		   price_pack_item = pool.get('product.pricelist.item').search(cr,uid,[('pricelist_id','=',pricelist.id),('product_tmpl_id','=',pack_obj.product_id.product_tmpl_id.id)],context=context)
	# 	# 		   pricelist_item_browse = pool.get('product.pricelist.item').browse(cr, uid, price_pack_item, context=context)
	# 	# 		   item_price += pricelist_item_browse.fixed_price * pack_obj.qty_uom
	# 	# 	   print "pack>>>>>>>>>>>>>>", pack
	# 	# 	   print "pack_price>>>>>>>>>>>>>>>>>", item_price
	# 	# else:
	# 	#     pricelist = request.env['product.pricelist'].browse(context['pricelist'])
	# 	url = "/shop"
	# 	if search:
	# 		post["search"] = search
	# 	if category:
	# 		category = request.env['product.public.category'].browse(int(category))
			
	# 		# Store Selected/Current Category in request.session
	# 		request.session['website_current_categ'] = category.id
			
	# 		url = "/shop/category/%s" % slug(category)
			
	# 	if attrib_list:
	# 		post['attrib'] = attrib_list

	# 	style_obj = request.env['product.style']
	# 	style_ids = style_obj.search([]).ids
	# 	for style_name in style_ids:
	# 		styles_1 = style_obj.browse(style_name)
			
	# 		if styles_1.name == "Sale Ribbon":
	# 			styles = style_obj.browse(style_name)
		
	# 	# product_pack = request.env['product.template'].search([('is_pack','=',True)])
		
	# 	# for pack in product_pack:
	# 	#     pack_record = request.env['product.template'].browse(pack)
	# 	#     pack_record.website_style_ids=[[6,0,[1]]]

	# 	category_obj = request.env['product.public.category']
	# 	category_ids = category_obj.search([('parent_id', '=', False)])
	# 	categs = category_obj.browse(category_ids)

	# 	product_obj = request.env['product.template']

	# 	parent_category_ids = []
	# 	if category:
	# 		parent_category_ids = [category.id]
	# 		current_category = category
	# 		while current_category.parent_id:
	# 			parent_category_ids.append(current_category.parent_id.id)
	# 			current_category = current_category.parent_id

	# 	product_count = product_obj.search_count(domain)
	# 	pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=3, url_args=post)
	# 	domain += [('id', 'in', product_template_ids)]
	# 	product_ids = product_obj.search(domain, limit=ppg, offset=pager['offset'], order='website_published desc, website_sequence desc')
	# 	products = product_obj.browse(product_ids)

	# 	attributes_obj = request.env['product.attribute']
	# 	if product_ids:
	# 		attributes_ids = attributes_obj.search([('attribute_line_ids.product_tmpl_id', 'in', product_ids)])
	# 	attributes = attributes_obj.browse(attributes_ids)

	# 	from_currency = request.env['res.users'].browse(request.uid).company_id.currency_id
	# 	to_currency = pricelist.currency_id
	# 	compute_currency = lambda price: request.env['res.currency']._compute(from_currency, to_currency, price)

	# 	values = {
	# 		'search': search,
	# 		'category': category,
	# 		'attrib_values': attrib_values,
	# 		'attrib_set': attrib_set,
	# 		'pager': pager,
	# 		'pricelist': pricelist,
	# 		'products': products,
	# 		# 'bins': table_compute().process(products, ppg),
	# 		'rows': PPR,
	# 		'styles': styles,
	# 		'categories': categs,
	# 		'attributes': attributes,
	# 		'compute_currency': compute_currency,
	# 		'keep': keep,
	# 		'parent_category_ids': parent_category_ids,
	# 		'style_in_product': lambda style, product: style.id in [s.id for s in product.website_style_ids],
	# 		'attrib_encode': lambda attribs: werkzeug.url_encode([('attrib',i) for i in attribs]),
	# 	}
	# 	if category:
	# 		values['main_object'] = category
	# 	return http.request.render("website_sale.products", values)



	# @http.route(['/shop/payment/transaction/<int:acquirer_id>'], type='json', auth="public", website=True)
	# def payment_transaction(self, acquirer_id):
	# 	""" Json method that creates a payment.transaction, used to create a
	# 	transaction when the user clicks on 'pay now' button. After having
	# 	created the transaction, the event continues and the user is redirected
	# 	to the acquirer website.

	# 	:param int acquirer_id: id of a payment.acquirer record. If not set the
	# 							user is redirected to the checkout page
	# 	"""
	# 	#print "custom callllllllllllllllllllllllleeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeddddddddddddddddddddddddddddddddddddddd"
	# 	payment_obj = request.env['payment.acquirer']
	# 	transaction_obj = request.env['payment.transaction']
	# 	order = request.website.sale_get_order()

	# 	if not order or not order.order_line or acquirer_id is None:
	# 		return request.redirect("/shop/checkout")

	# 	assert order.partner_id.id != request.website.partner_id.id

	# 	# find an already existing transaction
	# 	tx = request.website.sale_get_transaction()
	# 	if tx:
	# 		tx_id = tx.id
	# 		if tx.sale_order_id.id != order.id or tx.state in ['error', 'cancel'] or tx.acquirer_id.id != acquirer_id:
	# 			tx = False
	# 			tx_id = False
	# 		elif tx.state == 'draft':  # button cliked but no more info -> rewrite on tx or create a new one ?
	# 			tx.write({
	# 				'amount': order.amount_total,
	# 			})
	# 	if not tx:
	# 		tx_id = transaction_obj.create({
	# 			'acquirer_id': acquirer_id,
	# 			'type': 'form',
	# 			'amount': order.amount_total,
	# 			'currency_id': order.pricelist_id.currency_id.id,
	# 			'partner_id': order.partner_id.id,
	# 			'partner_country_id': order.partner_id.country_id.id,
	# 			'reference': request.env['payment.transaction'].get_next_reference(order.name),
	# 			'sale_order_id': order.id,
	# 		})
	# 		#print "tx_id!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!transaction_obj",tx_id,transaction_obj
	# 		request.session['sale_transaction_id'] = tx_id
	# 		tx = transaction_obj.browse(tx_id)
	# 		#print "====================txxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",tx.create_date
	# 	# update quotation
	# 	order.write({
	# 			'payment_acquirer_id': acquirer_id,
	# 			'payment_tx_id': request.env['sale_transaction_id'],
	# 			'date_order' : tx.create_date
	# 		})

	# 	#print "((((((((((((((((((((order)))))))))))))))))))))))))))))))",order
	# 	# confirm the quotation
	# 	if tx.acquirer_id.auto_confirm == 'at_pay_now':
	# 		order.action_confirm(send_email=True)

	# 	return payment_obj.render(
	# 		tx.acquirer_id.id,
	# 		tx.reference,
	# 		order.amount_total,
	# 		order.pricelist_id.currency_id.id,
	# 		values={
	# 			'return_url': '/shop/payment/validate',
	# 			'partner_id': order.partner_shipping_id.id or order.partner_invoice_id.id,
	# 			'billing_partner_id': order.partner_invoice_id.id,
	# 		},
	# 		context=dict(context, submit_class='btn btn-primary', submit_txt=_('Pay Now')))



	# Clear Shopping cart code
	@http.route(['/shop/cart/clear_cart'], type='json', auth="public", website=True)
	def clean_cart(self, type_id=None):
		order = request.website.sale_get_order()
		request.website.sale_reset()
		if order:
			order.sudo().unlink();
		return {}            
			
class website_sasmar(http.Controller):

	
	@http.route(['/faq'], type='http', auth="public", website=True)
	def faq(self, page=0, category=None, search='', **post):
		
		return http.request.render("sasmar_theme.faq")
		
	@http.route(['/retailers'], type='http', auth="public", website=True)
	def retailers(self, page=0, category=None, search='', **post):
		
		return http.request.render("sasmar_theme.retailers")
		
	@http.route(['/about-us'], type='http', auth="public", website=True)
	def about_us(self, page=0, category=None, search='', **post):
		
		return http.request.render("sasmar_theme.about-us")
		
	@http.route(['/free-shipping'], type='http', auth="public", website=True)
	def free_shipping(self, page=0, category=None, search='', **post):
		
		return http.request.render("sasmar_theme.free-shipping")  
		
	@http.route(['/your-privacy'], type='http', auth="public", website=True)
	def your_privacy(self, page=0, category=None, search='', **post):
		
		return http.request.render("sasmar_theme.your-privacy")   
		
	@http.route(['/our-terms'], type='http', auth="public", website=True)
	def our_terms(self, page=0, category=None, search='', **post):
		
		return http.request.render("sasmar_theme.our-terms") 
		
	@http.route(['/wholesale-orders'], type='http', auth="public", website=True)
	def wholesale_orders(self, page=0, category=None, search='', **post):
		
		return http.request.render("sasmar_theme.wholesale-orders")
		
	@http.route(['/helpdesk'], type='http', auth="public", website=True)
	def helpdesk(self, page=0, category=None, search='', **post):
		
		return http.request.render("sasmar_theme.helpdesk")
		
	# home page
	@http.route(['/'], type='http', auth="public", website=True)
	def home(self, page=0, category=None, search='', **post):
		
		return http.request.render("sasmar_theme.sasmar_home")

# New Menu Changes as per PPT
	@http.route(['/our-mission'], type='http', auth="public", website=True)
	def our_mission(self, page=0, category=None, search='', **post):
		
		return http.request.render("sasmar_theme.our-mission")

	@http.route(['/our-responsibility'], type='http', auth="public", website=True)
	def our_responsibility(self, page=0, category=None, search='', **post):
		
		return http.request.render("sasmar_theme.our-responsibility")
		
	@http.route(['/innovation'], type='http', auth="public", website=True)
	def innovation(self, page=0, category=None, search='', **post):
		
		return http.request.render("sasmar_theme.innovation")
		
	@http.route(['/research-development'], type='http', auth="public", website=True)
	def research_development(self, page=0, category=None, search='', **post):
		
		return http.request.render("sasmar_theme.research-development")

	@http.route(['/partnerships'], type='http', auth="public", website=True)
	def partnerships(self, page=0, category=None, search='', **post):
		
		return http.request.render("sasmar_theme.partnerships")

	@http.route(['/submit-an-idea'], type='http', auth="public", website=True)
	def submit_an_idea(self, page=0, category=None, search='', **post):
		
		return http.request.render("sasmar_theme.submit-an-idea")

	@http.route(['/our-brands'], type='http', auth="public", website=True)
	def our_brands(self, page=0, category=None, search='', **post):
		
		return http.request.render("sasmar_theme.our-brands")
		
	@http.route(['/conceive-plus'], type='http', auth="public", website=True)
	def conceive_plus(self, page=0, category=None, search='', **post):
		
		return http.request.render("sasmar_theme.conceive-plus") 
				
	@http.route(['/erexia'], type='http', auth="public", website=True)
	def erexia(self, page=0, category=None, search='', **post):
		
		return http.request.render("sasmar_theme.erexia")

	@http.route(['/purfeet'], type='http', auth="public", website=True)
	def purfeet(self, page=0, category=None, search='', **post):
		
		return http.request.render("sasmar_theme.purfeet")

	@http.route(['/sasmar-brand-personal-lubricant'], type='http', auth="public", website=True)
	def sasmar_brand_personal_lubricant(self, page=0, category=None, search='', **post):
		
		return http.request.render("sasmar_theme.sasmar-brand-personal-lubricant")    	

	@http.route(['/press-office'], type='http', auth="public", website=True)
	def press_office(self, page=0, category=None, search='', **post):
		
		return http.request.render("sasmar_theme.press-office") 

	@http.route(['/sitemap'], type='http', auth="public", website=True)
	def sitemap(self, page=0, category=None, search='', **post):
		
		return http.request.render("sasmar_theme.sitemap")     	

	@http.route(['/careers'], type='http', auth="public", website=True)
	def careers(self, page=0, category=None, search='', **post):
		
		return http.request.render("sasmar_theme.careers")  
		
	@http.route(['/working-at-sasmar'], type='http', auth="public", website=True)
	def working_at_sasmar(self, page=0, category=None, search='', **post):
		
		return http.request.render("sasmar_theme.working-at-sasmar")  

# Login page based on type of registration.

class AuthSignupHomeCustom(main.AuthSignupHome):      
		
	@http.route('/web/signup', type='http', auth='public', website=True)
	def web_auth_signup(self, *args, **kw):
		qcontext = self.get_auth_signup_qcontext()

		if not qcontext.get('token') and not qcontext.get('signup_enabled'):
			raise werkzeug.exceptions.NotFound()
		
		
		if qcontext.get('type') == 'wholesaler':
			if 'error' not in qcontext and request.httprequest.method == 'POST':
				try:
					self.do_signup(qcontext)
					return request.render('sasmar_theme.thank_you', qcontext)
				except (SignupError, AssertionError,e):
					qcontext['error'] = _(e.message)
					
		else: 
			if 'error' not in qcontext and request.httprequest.method == 'POST':
				try:
					self.do_signup(qcontext)
					if qcontext.get('token'):
						user_sudo = request.env['res.users'].sudo().search([('login', '=', qcontext.get('login'))])
						template = request.env.ref('auth_signup.mail_template_user_signup_account_created', raise_if_not_found=False)
						if user_sudo and template:
							template.sudo().with_context(
								lang=user_sudo.lang,
								auth_login=werkzeug.url_encode({'auth_login': user_sudo.email}),
							).send_mail(user_sudo.id, force_send=True)
					return super(AuthSignupHomeCustom, self).web_login(*args, **kw)
				except UserError as e:
					qcontext['error'] = e.name or e.value
				except (SignupError, AssertionError,e):
					if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
						qcontext["error"] = _("Another user is already registered using this email address.")
					else:
						_logger.error("%s", e)
						qcontext['error'] = _("Could not create a new account.")

		response = request.render('auth_signup.signup', qcontext)
		response.headers['X-Frame-Options'] = 'DENY'
		return request.render('auth_signup.signup', qcontext)
			
	def do_signup(self, qcontext):
		""" Shared helper that creates a res.partner out of a token """
		values = dict((key, qcontext.get(key)) for key in ('login', 'name', 'password','type'))
		if not values:
			raise UserError(_("The form was not properly filled in."))
		if values.get('password') != qcontext.get('confirm_password'):
			raise UserError(_("Passwords do not match; please retype them."))
		supported_langs = [lang['code'] for lang in request.registry['res.lang'].search_read([], ['code'])]
		if request.lang in supported_langs:
			values['lang'] = request.lang
		self._signup_with_values(qcontext.get('token'), values)
		request.cr.commit()

	def _signup_with_values(self, token, values):
		db, login, password ,type = request.registry['res.users'].signup(values,token)
		if type == 'consumer':
			request.cr.commit()     # as authenticate will use its own cursor we need to commit the current transaction
			uid = request.session.authenticate(db, login, password)
			if not uid:
				raise SignupError(_('Authentication Failed.'))

