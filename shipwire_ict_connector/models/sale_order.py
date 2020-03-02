from odoo import fields,models,api,_
from odoo.http import request
from requests.auth import HTTPBasicAuth
from odoo.exceptions import Warning
import json
import requests
import logging
from datetime import datetime
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):

    _inherit = "sale.order"

    ict_id = fields.Many2one('inter.company.transfer.ept',string="ICT",copy=False)

    @api.multi
    def action_view_ict(self):
        return

    @api.multi
    def create_ict(self):
        created_ids = []
        transfer_line_obj = self.env['sale.order.transfer.line']
        for line in self.order_line:
            if line.product_id.type == 'product':
                created_ids.append(transfer_line_obj.create({
                    'product_id':line.product_id.id,
                    'quantity':line.product_uom_qty or 1,
                    }).id)

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.transfer.ict',
            'view_type': 'form',
            'view_mode': 'form',
            'context' : {'default_order_id':self.id,
                        'default_line_ids':[(6,0,created_ids)],
                        'default_destination_warehouse':self.warehouse_id.id,
                           },
            'target': 'new',
        }