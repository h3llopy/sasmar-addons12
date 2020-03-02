# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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


from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp

class purchase_order(models.Model):
    _inherit = 'purchase.order'
    
    user_id = fields.Many2one('res.users', 'Responsible Person')
    qoute_no = fields.Char('Your Quotation #')
    ship_via = fields.Many2one('ship.via', 'SHIP VIA')
    
    @api.multi
    def print_quotation(self):
        self.write({'state': "sent"})
        return self.env['report'].get_action(self, 'sasmar_report.purchase_order_report_template_id')
#
#
#    def wkf_send_rfq(self, cr, uid, ids, context=None):
#		res = super(purchase_order, self).wkf_send_rfq(cr, uid, ids, context=context)
#		company = self.browse(cr, uid, ids)[0].company_id.name
#		mail_temp = self.pool.get('email.template')
#		# 1 - SASMAR SPRL
#		# 5 - SASMAR LIMITED
#		temp_id = res.get('context').get('default_template_id')
#		if company == 'SASMAR SPRL':
#			temp_id = mail_temp.search(cr, uid, [('name', '=', 'Purchase Order Sasmar-SASMAR SPRL')])
#		if company == 'SASMAR LIMITED':
#			temp_id = mail_temp.search(cr, uid, [('name', '=', 'Purchase Order Sasmar-SASMAR LIMITED')])
#		res.get('context').update({'default_template_id':temp_id})
#		return res    
