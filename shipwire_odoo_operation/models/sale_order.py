from openerp import fields, models ,api
from datetime import datetime

class sale_order(models.Model):

    _inherit = "sale.order"
    
    is_shipwire = fields.Boolean("Shipwire Order",copy=False)
    shipwire_id = fields.Integer("Shipwire ID",copy=False)
    
    @api.multi
    def action_confirm(self):
    
        res = super(sale_order,self.with_context(send_mail=False)).action_confirm()
    #change code to not send wooo commerace order to shipwire
        if not self.is_shipwire:
            return res
        if self.woo_order_id:
        
            return res
        log_line_obj  = self.env['process.log.line']
        instance = self.env['shipwire.instance'].search([],limit=1)
        log_obj = self.env['process.log']
        sequence_id=self.env.ref('shipwire_odoo_operation.shipwire_process_log_seq').ids
        if sequence_id:
            record_name=self.env['ir.sequence'].get_id(sequence_id[0])
        else:
            record_name='/'

        log_vals ={
            'name' : record_name,
            'log_date': datetime.now(),
            'process':'sale',
            'operation':'export'
                }
        log_record = log_obj.create(log_vals)

        if not instance:
            msg = "Instance NOT FOUND while confirm the Sale Order : %s" %(self.name)
            log_line_vals = {
                'log_type': 'error',
                'action' : 'skip',
                'log_id': log_record.id,
                'message' : msg or False,
                }
            log_line_obj.create(log_line_vals)
            return res


        if not instance.export_to_shipwire:
            return res

        picking_obj = self.env['stock.picking']
#         if self.picking_ids:
        picking = picking_obj.search([('id','in',self.picking_ids.ids),('state','not in',['draft','cancel','done'])],limit=1)
#             if not picking:
#                 return res
#             resource = picking[0].post_order()
        resource = self.post_order()
        if resource and not resource.get('errors'):
            if resource.get('resource',{}).get('items',False):
                order_id = resource ['resource']['items'][0]['resource']['id']
                if picking:
                    picking.write({'shipwire_id':order_id})
                self.write({'shipwire_id':order_id})
        else:
            msg = "Order %s is not Exported to Shipwire"%(self.name)
            log_line_vals = {
                'log_type': 'error',
                'action' : 'skip',
                'log_id': log_record.id,
                'message' : msg or False,
                'response' : resource
                }
            log_line_obj.create(log_line_vals)

        if not log_record.log_line_ids:
            log_record.unlink()

        return res
