# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2015-Today BrowseInfo (<http://www.browseinfo.in>)
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

from datetime import datetime, timedelta
import time
from odoo import fields, models,api
from odoo.tools.translate import _


class stock_picking(models.Model):
    _inherit = "stock.picking"
    _description = "Stock Picking"

    def do_print_picking(self):
        '''This function prints the picking list'''
        return self.env.ref('custom_picking_report.stock.action_report_delivery').report_action(self)

        
        #return self.pool.get("report").get_action(cr, uid, ids, 'custom_picking_report.report_picking_1', context=context)



