# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class wizard_product_bundle(models.TransientModel):
	_name = 'wizard.product.bundle'

	product_id = fields.Many2one('product.product',string='Bundle',required=True)
	quantity = fields.Integer('Quantity',required=True ,default=1)
	

	@api.multi
	def button_add_product_bundle(self):
		ctx =dict(self._context or {})
		sale_obj =self.env['sale.order'].browse(ctx.get('active_id'))
		taxes_id = []
		unit_price = 0.0
		if self.product_id.taxes_id:
			taxes_id = self.product_id.taxes_id.ids
		if self.product_id.pack_ids:
			for pro in self.product_id.pack_ids:
				product = pro.product_id.with_context(
	                pricelist=sale_obj.pricelist_id.id,
	            )
				price_unit= self.env['account.tax']._fix_tax_included_price(product.price, product.taxes_id,False)
				multi_price = price_unit * pro.qty_uom
				unit_price+= multi_price 
		self.env['sale.order.line'].create({'order_id':self._context['active_id'],'product_id':self.product_id.id, 'name':self.product_id.name,'price_unit':unit_price or self.product_id.list_price,'product_uom':1,'product_uom_qty':self.quantity,'tax_id':[(6, 0, taxes_id)]})	
		return True
