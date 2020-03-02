from odoo.report import report_sxw
from odoo.osv import osv
from datetime import date,time,datetime

class sale_order_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(sale_order_report, self).__init__(cr, uid, name, context=context)
        self.index = 0
        self.localcontext.update({
                                  'time' : time,
                                  'get_quantity' : self.get_quantity,
                                  '_get_date' : self._get_date,
                                  'get_est_date' : self.get_est_date,
                                  'get_int' : self.get_int,
                                  'get_float_format' : self.get_float_format,
                                  'get_bank_id':self.get_bank_id,
                                'get_bank_bic':self.get_bank_bic,
                                'get_acc_no':self.get_acc_no,    
                                  })
  
  
    def get_acc_no(self, obj):
        sale_price_cur_id =  obj.pricelist_id.currency_id.id
        bank_no = ''
        if obj.company_id.bank_ids:
            bank_ids = [x for x in obj.company_id.bank_ids if (x.currency_id.id == sale_price_cur_id and x.footer == True)]
            if bank_ids:
                bank_no = bank_ids[0].acc_number
            else:
                bank_ids = [x for x in obj.company_id.bank_ids if (x.currency_id.id == obj.company_id.currency_id.id and x.footer == True)]
                if bank_ids :
                    bank_no = bank_ids[0].acc_number    
            return bank_no

    
    def get_bank_id(self, obj):
        bank_name = ''
        sale_price_cur_id =  obj.pricelist_id.currency_id.id
        if obj.company_id.bank_ids:
            bank_ids = [x for x in obj.company_id.bank_ids if (x.currency_id.id == sale_price_cur_id and x.footer == True) ]
            if  bank_ids:
                bank_name = bank_ids[0].bank_name_t
            else:
                bank_ids = [x for x in obj.company_id.bank_ids if (x.currency_id.id == obj.company_id.currency_id.id and x.footer == True)]
                if bank_ids :
                    bank_name = bank_ids[0].bank_name_t 
            return bank_name

    def get_bank_bic(self, obj):
        bank_bic = ''
        sale_price_cur_id =  obj.pricelist_id.currency_id.id
        if obj.company_id.bank_ids:
            bank_ids = [x for x in obj.company_id.bank_ids if (x.currency_id.id == sale_price_cur_id and x.footer == True) ]
            if bank_ids:
                bank_bic = bank_ids[0].bank_bic
            else:
                bank_ids = [x for x in obj.company_id.bank_ids if (x.currency_id.id == obj.company_id.currency_id.id and x.footer == True)]
                if bank_ids :
                    bank_bic = bank_ids[0].bank_bic
            return bank_bic
  
                                  
    def get_float_format(self, value):
        result = "{:.3f}".format(value)
        return result

    def get_quantity(self, obj):
        product_uom_qty= 0.0
        for line in obj.order_line:
            product_uom_qty += line.product_uom_qty
        return product_uom_qty

    def _get_date(self, obj):
        if obj.date_order:
            req_date = datetime.strptime(obj.date_order, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%y')
            return req_date

    def get_est_date(self, obj):
        if obj.delivery_date:
            req_date = datetime.strptime(obj.delivery_date, '%Y-%m-%d').strftime('%d/%m/%y')
            return req_date

    def get_int(self,data3):
        if data3:
            return int(data3)

    
class sale_order_report_template_id(osv.AbstractModel):
    _name='report.sasmar_report.sale_order_report_template_id'
    _inherit='report.abstract_report'
    _template='sasmar_report.sale_order_report_template_id'
    _wrapped_report_class=sale_order_report
    
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:        
                       

    
