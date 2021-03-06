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
from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo import SUPERUSER_ID


class ProductPack(models.Model):
    _name = 'product.pack'

    product_id = fields.Many2one(comodel_name='product.product', string='Product', required=True)
    qty_uom = fields.Float(string='Quantity', required=True, defaults=1.0)
    bi_product_template = fields.Many2one(comodel_name='product.template', string='Product pack')
    bi_image = fields.Binary(related='product_id.image_medium', string='Image', store=True)
    price = fields.Float(related='product_id.lst_price', string='Product Price')
    uom_id = fields.Many2one(related='product_id.uom_id' , string="Unit of Measure", readonly="1")
    name = fields.Char(related='product_id.name', readonly="1")

class ProductProduct(models.Model):
    _inherit = 'product.template'

    is_pack = fields.Boolean(string='Is Product Pack')
    pack_ids = fields.One2many('product.pack', 'bi_product_template', string='Product pack')
    
