# -*- coding: utf-8 -*-
from odoo import models,api,fields

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    @api.multi
    def get_price_available(self, order):
        """
        :Viki They changed this method in base we just taken it in our module.
        """
        self.ensure_one()
        total = weight = volume = quantity = 0
        total_delivery = 0.0
        ProductUom = self.env['product.uom']
        for line in order.order_line:
            if line.state == 'cancel':
                continue
            if line.is_delivery:
                total_delivery += line.price_total
            if not line.product_id or line.is_delivery:
                continue
            qty = ProductUom._compute_qty(line.product_uom.id, line.product_uom_qty, line.product_id.uom_id.id)
            weight += (line.product_id.weight or 0.0) * qty
            volume += (line.product_id.volume or 0.0) * qty
            quantity += qty
        total = (order.amount_total or 0.0) - total_delivery
        total = order.currency_id.with_context(date=order.date_order).compute(total, order.pricelist_id.currency_id)
        return self.get_price_from_picking(total, weight, volume, quantity)