# -*- coding: utf-8 -*-
from openerp import models,api,fields,SUPERUSER_ID
from datetime import datetime
from dateutil.relativedelta import relativedelta

class ProcurementOrder(models.Model):
    _inherit = "procurement.order"

#     def _run_move_create(self,cr, uid ,procurement, context=None):
#         """
#         Context : set company_id from procurement if else from procurement rule.
#         """
#         if procurement.product_id.is_pack==True:
#             return {}
#         vals = super(ProcurementOrder,self)._run_move_create(cr, uid ,procurement, context=None)
#         vals.update({'company_id': procurement.company_id.id or procurement.rule_id.company_id.id or procurement.rule_id.location_src_id.company_id.id or procurement.rule_id.location_id.company_id.id})
#         return vals
        
#     def _run(self, cr, uid, procurement, context=None):
#         if procurement.rule_id and procurement.rule_id.action == 'move':
#             if not procurement.rule_id.location_src_id:
#                 self.message_post(cr, uid, [procurement.id], body=_('No source location defined!'), context=context)
#                 return False
#             move_obj = self.pool.get('stock.move')
#             move_dict = self._run_move_create(cr, uid, procurement, context=context)
# # Condition Not in base            
#             if not move_dict:
#                 return True
# # Condition Not in base    
#             move_obj.create(cr, SUPERUSER_ID, move_dict, context=context)
#             return True
#         return super(ProcurementOrder, self)._run(cr, uid, procurement, context=context)
#     