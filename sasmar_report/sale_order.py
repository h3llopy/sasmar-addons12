import itertools
from lxml import etree

from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning
from odoo.tools import float_compare
import odoo.addons.decimal_precision as dp

class sale_order(models.Model):
    _inherit = 'sale.order'
    
    ship_via = fields.Many2one('ship.via', 'SHIP VIA')
    delivery_date = fields.Date('Delivery Date')
    po_number = fields.Char('Purchase Order')
    supplier_number = fields.Char('Supplier Number')

    @api.multi
    def print_quotation(self):
        self.filtered(lambda s: s.state == 'draft').write({'state': 'sent'})
        return self.env['report'].get_action(self, 'sasmar_report.sale_order_report_template_id')
    
    
class ship_via(models.Model):
    _name = 'ship.via'
    
    name = fields.Char('Name')
