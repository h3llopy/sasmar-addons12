# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Browseinfo (http://browseinfo.in)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime

import odoo
from odoo import SUPERUSER_ID
from odoo import tools
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.osv import expression
from odoo import fields, models
from odoo.tools.translate import _
from odoo.tools import email_re, email_split


class sale_order(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        
        res = super(sale_order, self).create(vals)
        #self.send_mail_sasmar(cr, uid, res, context=context)
        return res

    def send_mail_sasmar(self):
        email_temp = self.env['mail.template']
        template_id = self.env['ir.model.data'].get_object_reference('send_email_finance', 'email_template_sasmar_invoice')[1]
        
        ids = self.ids
        email_temp.send_mail(template_id, ids[0], force_send=False)
        return True


class purchase_order(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def create(self, vals):
        
        res = super(purchase_order, self).create(vals)
        return res
    
