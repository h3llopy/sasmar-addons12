# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class stock_config_settings(models.TransientModel):
    _inherit = 'res.config.settings'

    user_id = fields.Char("Shipwire UserID",related="company_id.user_id",readonly=False)
    pwd = fields.Char("Shipwire Password" ,related="company_id.pwd",readonly=False )



    @api.model
    def get_values(self):
      res = super(stock_config_settings, self).get_values()
      res.update(
          user_id=self.env['ir.config_parameter'].sudo().get_param('custom_stock_shipwire.user_id'),
          pwd=self.env['ir.config_parameter'].sudo().get_param('custom_stock_shipwire.pwd')
      )
      return res


    @api.multi
    def set_values(self):
      delivery_method =self.env['delivery.carrier']
      search_delivery = self.env['ir.model.data'].xmlid_to_res_id('delivery_shipwire.delivery_carrier_shipwire')
      brw_method = delivery_method.browse(search_delivery)
      if self.pwd and  self.user_id:
          brw_method.write({'shipwire_username':self.user_id ,'shipwire_passwd':self.pwd})
      if not self.pwd or not  self.user_id:
          raise UserError(_('Please Enter UserID and Password Both'))
      super(stock_config_settings, self).set_values()
      self.env['ir.config_parameter'].sudo().set_param('custom_stock_shipwire.user_id', self.user_id)
      self.env['ir.config_parameter'].sudo().set_param('custom_stock_shipwire.pwd', self.pwd)
    
    
    # @api.multi
    # def save_button(self):
    #     delivery_method =self.env['delivery.carrier']
    #     search_delivery = self.env['ir.model.data'].xmlid_to_res_id('delivery_shipwire.delivery_carrier_shipwire')
    #     brw_method = delivery_method.browse(search_delivery)
    #     if self.pwd and  self.user_id:
    #         brw_method.write({'shipwire_username':self.user_id ,'shipwire_passwd':self.pwd})
    #     if not self.pwd or not  self.user_id:
    #         raise UserError(_('Please Enter UserID and Password Both'))
    #     return True




class Company(models.Model):
    _inherit = 'res.company'



    user_id = fields.Char("Shipwire UserID")
    pwd = fields.Char("Shipwire Password" , )