# -*- coding: utf-8 -*-
from openerp import models,api,fields,SUPERUSER_ID
from openerp.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import UserError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)], change_default=True, ondelete='restrict', required=False)
    
    @api.multi
    def _compute_tax_id(self):
        for line in self:
            fpos = line.order_id.fiscal_position_id or line.order_id.partner_id.property_account_position_id
            # If company_id is set, always filter taxes by the company
            """
            :Viki Find the tax base on the order's company.
            """
            taxes = line.product_id.taxes_id.filtered(lambda r: r.company_id == line.order_id.company_id)
            line.tax_id = fpos.map_tax(line.product_id.taxes_id).filtered(lambda r: r.company_id == line.order_id.company_id) if fpos else taxes

                
    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}

        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        """
            :Viki Check the uom category instead of uom in below condition..
        """
        if not (self.product_uom and (self.product_id.uom_id.category_id.id == self.product_uom.category_id.id)):
            vals['product_uom'] = self.product_id.uom_id
            
        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )

        name = product.name_get()[0][1]
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['name'] = name
        self._compute_tax_id()

        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price(product.price, product.taxes_id, self.tax_id)
        self.update(vals)
        return {'domain': domain}


    # Properly Managed in Force company module : Comment By Dhaval
    # @api.multi
    # def _prepare_invoice_line(self, qty ):
    #     return super(SaleOrderLine,self)._prepare_invoice_line(qty)
    #     """
    #     :Viki wrong way to get accounts from property fields. 
    #     """
    #     self.ensure_one()
    #     res = {}
    #     property_obj = self.env['ir.property']
    #     field_obj = self.env['ir.model.fields']
    #     if self.invoice_status != 'invoiced':
    #         if self.product_id:
    #             field_id = field_obj.search( [('field_description', '=', 'Income Account'), ('name', '=', 'property_account_income_categ_id')])
    #             if field_id and self._context:
    #                 property_id = property_obj.search([('fields_id', '=', field_id[0].id), ('company_id', '=', self.order_id.company_id.id)])
    #             else:
    #                 property_id = False
    #             if property_id:
    #                 acc_ref = property_obj.browse( property_id[0].id).value_reference
    #                 account_id = acc_ref and acc_ref.split(',') and acc_ref.split(',')[1]
    #                 account_id = int(account_id)
    #             else:
    #                 account_id = False
    #             if not account_id:
    #                 raise UserError(_('Error!'),
    #                         _('Please define income account for this product: "%s" (id:%d).') % \
    #                         (self.product_id.name, self.product_id.id,))
    #         else:
    #             prop = self.pool.get('ir.property').get(
    #                     'property_account_income_categ_id', 'product.category')
    #             account_id = prop and prop.id or False
    #         if not account_id:
    #             raise UserError(_('Error!'),
    #                         _('There is no Fiscal Position defined or Income category account defined for default properties of Product categories.'))
    #     res = {
    #         'name': self.name,
    #         'sequence': self.sequence,
    #         'origin': self.order_id.name,
    #         'account_id': account_id or False,
    #         'price_unit': self.price_unit,
    #         'quantity': qty,
    #         'discount': self.discount,
    #         'uom_id': self.product_uom.id,
    #         'product_id': self.product_id.id or False,
    #         'invoice_line_tax_ids': [(6, 0, self.tax_id.ids)],
    #         'account_analytic_id': self.order_id.project_id.id,
    #     }
    #     return res