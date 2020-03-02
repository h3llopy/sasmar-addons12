from odoo import tools
from odoo import models, fields, api

from datetime import date,time,datetime

class invoice_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(invoice_report, self).__init__(cr, uid, name, context=context)
        self.index = 0
        self.total_qty = 0
        self.localcontext.update({
                                  'time' : time,
                                  'get_quantity' : self.get_quantity,
                                  'get_delivery_add' : self.get_delivery_add,
                                  'get_date_format' : self.get_date_format,
                                  'get_int':self.get_int,
								  'check_origin': self.check_origin,
                                   'get_bank_id':self.get_bank_id,
                                'get_bank_bic':self.get_bank_bic,
                                'get_acc_no':self.get_acc_no, 
                                  })
    def get_delivery_add(self, o):
        order_id = self.pool.get('sale.order').search(self.cr, self.uid, [('name', '=', o.origin)])
        s_obj = self.pool.get('sale.order').browse(self.cr, self.uid, order_id)
        return s_obj
	
    def get_acc_no(self, obj):
        sale_price_cur_id =  obj.currency_id.id
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
        sale_price_cur_id =  obj.currency_id.id
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
        sale_price_cur_id =  obj.currency_id.id
        if obj.company_id.bank_ids:
            bank_ids = [x for x in obj.company_id.bank_ids if (x.currency_id.id == sale_price_cur_id and x.footer == True) ]
            if bank_ids:
                bank_bic = bank_ids[0].bank_bic
            else:
                bank_ids = [x for x in obj.company_id.bank_ids if (x.currency_id.id == obj.company_id.currency_id.id and x.footer == True)]
                if bank_ids :
                    bank_bic = bank_ids[0].bank_bic
            return bank_bic

    def check_origin(self , o):
    	order_id = self.pool.get('sale.order').search(self.cr, self.uid, [('name', '=', o.origin)])
    	if order_id:
    		return True
    	else:
    		return False	
	
                                  
    def get_quantity(self, obj):
        for line in obj.invoice_line_ids:
            self.total_qty += line.quantity
        return self.total_qty
        
    def get_date_format(self, date1):
        if date1:
            req_date = datetime.strptime(date1, '%Y-%m-%d').strftime('%d/%m/%y')
            return req_date
    def get_int(self,data3):
        if data3:
            return int(data3)
                                  
class invoice_report_template_id(models.AbstractModel):
    _name='report.sasmar_report.invoice_report_template_id'
    _inherit='report.abstract_report'
    _template='sasmar_report.invoice_report_template_id'
    _wrapped_report_class=invoice_report
    
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:        
                       

    
