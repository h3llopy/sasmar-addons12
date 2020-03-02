# -*- coding: utf-8 -*-
from odoo import models,api,fields

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    dest_address_id = fields.Many2one('res.partner', 'Customer Address')
    bid_date = fields.Date('Bid Received On', readonly = True)
    bid_validity = fields.Date('Bid Valid Until')
    validator = fields.Many2one('res.users', 'Validated By')
    expected_date = fields.Date('Expected Date')
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].with_context(company_id=vals.get('company_id') or False).next_by_code('purchase.order') or '/'
        return super(PurchaseOrder, self).create(vals)
    
    @api.onchange('company_id')
    def onchange_company_id(self):
        """
        :Viki Setting picking type based on the warehouse and company.
        """
        if not self.company_id:
            return {}
        warehouse_obj = self.env['stock.warehouse']
        picking_type_obj = self.env['stock.picking.type']
        warehouse_id = warehouse_obj.search([('company_id', '=', self.company_id.id)])
        if not warehouse_id:
            return {}
        picking_type_id = picking_type_obj.search([('warehouse_id', '=', warehouse_id[0].id or False),('code','=','incoming')])
        if not picking_type_id: 
            return {}
        else: 
            picking_type_id = picking_type_id[0].id
        self.picking_type_id = picking_type_id
    
    @api.model
    def _prepare_picking(self):
        if not self.group_id:
            self.group_id = self.group_id.create({
                'name': self.name,
                'partner_id': self.partner_id.id
            })
            """
            :Viki From Base removed this below condition.
            """        
#         if not self.partner_id.property_stock_supplier.id:
#             raise UserError(_("You must set a Vendor Location for this partner %s") % self.partner_id.name)
        return {
            'picking_type_id': self.picking_type_id.id,
            'partner_id': self.partner_id.id,
            'date': self.date_order,
            'origin': self.name,
            'location_dest_id': self._get_destination_location(),
            'location_id': self.partner_id.property_stock_supplier.id,
            'company_id': self.company_id.id
        }
        
    @api.multi
    def action_view_invoice(self):
        result = super(PurchaseOrder,self).action_view_invoice()
        return result
        '''
        :Viki 
        :1) Setting default Company id and default journal id in context.
        :2) and to search journal removed the currency domain. 
        '''
        result['context'] = {'type': 'in_invoice', 'default_purchase_id': self.id, 'default_company_id': self.company_id.id}
        journal_ids = self.env['account.journal'].search([('type', '=', 'purchase'), ('company_id', '=', self.company_id.id)])
        result['context']['default_journal_id'] = journal_ids[0].id
        return result
