# -*- coding: utf-8 -*-
from openerp import models,api,fields

class ResPartner(models.Model):
    _inherit = "res.partner"
    
    sequence = fields.Char('Number', compute = 'sequnce_fucn',readonly = 'True')
    
    @api.one
    def sequnce_fucn(self):
        if len(str(self.id)) > 0:
            sequence = {1: '00000', 2: '0000', 3: '000', 4: '00',5:'0'}
            seq = sequence.get(len(str(self.id)), '') + str(self.id)
            self.sequence =  seq
    
    # @api.model
    # def create(self, vals):
    #     """
    #     Supplier wise location creation with current company selection.
    #     """
    #     ctx = dict(self._context or {})
    #     if ctx.get('default_supplier') or ctx.get('search_default_supplier') or vals.get('supplier'):
    #         location = self.env['stock.location']
    #         parent_id = location.search([('usage','=', 'view')])
    #         if vals.get('name'):
    #             value = {'name': vals.get('name') + ' ' + 'Location',
    #                     'usage': 'supplier',
    #                     'active':True,
    #                     'location_id':parent_id[0].id,
    #                     'company_id': vals.get('company_id', False)
    #                     }
    #             create_location = location.create(value)
    #             vals['property_stock_supplier'] = create_location.id
    #     partner = super(ResPartner, self).create(vals)
    #     return partner
    
    
    # @api.multi
    # def write(self, vals):
    #     """
    #     Supplier wise location with current company selection.
    #     """
    #     if vals.get('supplier') or vals.get('company_id',False):
    #         location = self.env['stock.location']
    #         if self.property_stock_supplier:
    #             self.property_stock_supplier.write({'company_id':vals.get('company_id',False)})
    #         else:
    #             if self.supplier:
    #                 parent_id = location.search([('usage','=', 'view')])
    #                 value = {'name': self.name + ' ' + 'Location',
    #                         'usage': 'supplier',
    #                         'active':True,
    #                         'location_id':parent_id[0].id,
    #                         'company_id':vals.get('company_id',False)
    #                         }
    #                 create_location = location.create(value)
    #                 vals['property_stock_supplier'] = create_location.id
    #     partner = super(ResPartner, self).write(vals)
    #     return partner