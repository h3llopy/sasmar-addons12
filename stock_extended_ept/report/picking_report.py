# -*- coding: utf-8 -*-
from openerp.report import report_sxw
from openerp.osv import osv
from datetime import time, date
from openerp import models, fields, api, _
from openerp.tools import ustr

class picking_reports(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        super(picking_reports, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time' : time,
            'get_ship_via':self.get_ship_via,
            'get_invoice': self.get_invoice,
            'get_invoice_date':self.get_invoice_date,
            'get_ship_date': self.get_ship_date,
            'get_po_no': self.get_po_no,
            'get_volume': self.get_volume,
            'get_weight_gross': self.get_weight_gross,
            'get_weight_net': self.get_weight_net,
            'get_volume_op': self.get_volume_op,
            'get_weight_gross_op': self.get_weight_gross_op,
            'get_weight_net_op': self.get_weight_net_op,
            'get_partner_company' : self.get_partner_company,
            'get_partner_name' : self.get_partner_name,
            'get_partner_phone':self.get_partner_phone,
            'get_partner_street': self.get_partner_street,
            'get_partner_street2': self.get_partner_street2,
            'get_partner_zip': self.get_partner_zip,
            'get_partner_country': self.get_partner_country,
            'get_partner_company_invoice' : self.get_partner_company_invoice,
            'get_partner_street_invoice': self.get_partner_street_invoice,
            'get_partner_street_invoice2': self.get_partner_street_invoice2,
            'get_partner_zip_invoice': self.get_partner_zip_invoice,
            'get_partner_country_invoice': self.get_partner_country_invoice,
            'get_invoice_partner_phone':self.get_invoice_partner_phone,
                                  
        })


    def get_ship_via(self, obj):
        sale_obj = self.pool.get('sale.order')
        if obj:
            if obj.origin:
                sale_order = sale_obj.search(self.cr, self.uid, [('name', '=', obj.origin)])
                if sale_order:
                    sale_browse = sale_obj.browse(self.cr, self.uid, sale_order[0])
                    if sale_browse.ship_via.name:
                        return sale_browse.ship_via.name

    def get_ship_date(self, obj):
        sale_obj = self.pool.get('sale.order')
        if obj:
            if obj.origin:
                sale_order = sale_obj.search(self.cr, self.uid, [('name', '=', obj.origin)])
                if sale_order:
                    sale_browse = sale_obj.browse(self.cr, self.uid, sale_order[0])
                    if sale_browse.date_order:
                        return sale_browse.date_order




    def get_invoice(self, obj):
        account_obj = self.pool.get('account.invoice')
        if obj:
            if obj.origin:
                account_invoice = account_obj.search(self.cr, self.uid, [('origin', '=', obj.origin)])
                if account_invoice:
                    number = [str(x.number) for x in account_obj.browse(self.cr, self.uid, account_invoice) if x.number]
                    number = ','.join(number)
                    return  number or ''

    def get_invoice_date(self, obj):
        account_obj = self.pool.get('account.invoice')
        if obj:
            if obj.origin:
                account_invoice = account_obj.search(self.cr, self.uid, [('origin', '=', obj.origin)])
                if account_invoice:
                    date = [str(x.date_invoice) for x in account_obj.browse(self.cr, self.uid, account_invoice) if x.date_invoice]
                    date = ','.join(date)
                    return  date or ''

    def get_po_no(self, obj):
        sale_obj = self.pool.get('sale.order')
        if obj:
            if obj.origin:
                sale_order = sale_obj.search(self.cr, self.uid, [('name', '=', obj.origin)])
                if sale_order:
                    sale_browse = sale_obj.browse(self.cr, self.uid, sale_order[0])
                    if sale_browse.po_number:
                        return  sale_browse.po_number

    def get_volume(self, obj):
        product_obj = self.pool.get('product.product')
        if obj:
            product_volume = 0.0
            if obj.product_id:
                product = product_obj.search(self.cr, self.uid, [('default_code', '=', obj.product_id.default_code)])
                if product:
                    product_browse = product_obj.browse(self.cr, self.uid, product[0])
                    if product_browse.volume:
                        product_volume = product_browse.volume * obj.product_uom_qty
                    else:
                        prodcut_volume = 0.0
                    return  product_volume

    def get_weight_gross(self, obj):
        product_obj = self.pool.get('product.product')
        if obj:
            product_weight = 0.0
            if obj.product_id:
                product = product_obj.search(self.cr, self.uid, [('default_code', '=', obj.product_id.default_code)])
                if product:
                    product_browse = product_obj.browse(self.cr, self.uid, product[0])
                    if product_browse.weight:
                        product_weight = product_browse.weight * obj.product_uom_qty
                    else:
                        product_weight = 0.0
                    return  product_weight

    def get_weight_net(self, obj):
        product_obj = self.pool.get('product.product')
        if obj:
            product_net = 0.0
            if obj.product_id:
                product = product_obj.search(self.cr, self.uid, [('default_code', '=', obj.product_id.default_code)])
                if product:
                    product_browse = product_obj.browse(self.cr, self.uid, product[0])
                    if product_browse.weight_net:
                        product_net = product_browse.weight_net * obj.product_uom_qty
                    else:
                        product_net = 0.0
                    return  product_net


    def get_volume_op(self, obj):
        product_obj = self.pool.get('product.product')
        if obj:
            product_net = 0.0
            if obj.product_id:
                product = product_obj.search(self.cr, self.uid, [('default_code', '=', obj.product_id.default_code)])
                if product:
                    product_browse = product_obj.browse(self.cr, self.uid, product[0])
                    if product_browse.volume:
                        product_net = product_browse.volume * obj.product_qty
                    else:
                        product_net = 0.0
                    return  product_net

    def get_weight_gross_op(self, obj):
        product_obj = self.pool.get('product.product')
        if obj:
            product_net = 0.0
            if obj.product_id:
                product = product_obj.search(self.cr, self.uid, [('default_code', '=', obj.product_id.default_code)])
                if product:
                    product_browse = product_obj.browse(self.cr, self.uid, product[0])
                    if product_browse.weight:
                        product_net = product_browse.weight * obj.product_qty
                    else:
                        product_net = 0.0
                    return  product_net

    def get_weight_net_op(self, obj):
        product_obj = self.pool.get('product.product')
        if obj:
            product_net = 0.0
            if obj.product_id:
                product = product_obj.search(self.cr, self.uid, [('default_code', '=', obj.product_id.default_code)])
                if product:
                    product_browse = product_obj.browse(self.cr, self.uid, product[0])
                    if product_browse.weight_net:
                        product_net = product_browse.weight_net * obj.product_qty
                    else:
                        product_net = 0.0
                    return  product_net


    def get_partner_company(self, obj):
        sale_obj = self.pool.get('sale.order')
        if obj:
            if obj.origin:
                sale_order = sale_obj.search(self.cr, self.uid, [('name', '=', obj.origin)])
                if sale_order:
                    sale_browse = sale_obj.browse(self.cr, self.uid, sale_order[0])
                    if sale_browse.partner_shipping_id:
                        if sale_browse.partner_shipping_id.parent_id.name != False:
                            shipping = sale_browse.partner_shipping_id.parent_id.name
                        else:
                            shipping = False
                    return shipping
                else:
                    picking_object = self.pool.get('stock.picking')
                    picking_order = picking_object.browse(self.cr, self.uid, obj.id) 
                    if picking_order.partner_id.parent_id.name != False:
                        p_shipping = picking_order.partner_id.parent_id.name 
                    else:
                        p_shipping = False
                    return p_shipping
            else:
                picking_object = self.pool.get('stock.picking')
                picking_order = picking_object.browse(self.cr, self.uid, obj.id) 
                if picking_order.partner_id.parent_id.name != False:
                    p_shipping = picking_order.partner_id.parent_id.name 
                else:
                    p_shipping = False
                return p_shipping

                       
    def get_partner_name(self, obj):
        sale_obj = self.pool.get('sale.order')
        if obj:
            if obj.origin:
                sale_order = sale_obj.search(self.cr, self.uid, [('name', '=', obj.origin)])
                if sale_order:
                    sale_browse = sale_obj.browse(self.cr, self.uid, sale_order[0])
                    if sale_browse.partner_shipping_id.name != False:
                        name = sale_browse.partner_shipping_id.name 
                    return name
                else:
                    picking_object = self.pool.get('stock.picking')
                    picking_order = picking_object.browse(self.cr, self.uid, obj.id) 
                    if picking_order.partner_id.name != False:
                        p_name = picking_order.partner_id.name 
                    else:
                        p_name = False
                    return p_name
                        
            else:
                picking_object = self.pool.get('stock.picking')
                picking_order = picking_object.browse(self.cr, self.uid, obj.id) 
                if picking_order.partner_id.name != False:
                    p_name = picking_order.partner_id.name 
                else:
                    p_name = False
                return p_name
                
    
    def get_partner_phone(self, obj):
        sale_obj = self.pool.get('sale.order')
        if obj:
            if obj.origin:
                sale_order = sale_obj.search(self.cr, self.uid, [('name', '=', obj.origin)])
                if sale_order:
                    sale_browse = sale_obj.browse(self.cr, self.uid, sale_order[0])
                    if sale_browse.partner_shipping_id.phone != False:
                        phone = sale_browse.partner_shipping_id.phone
                    else:
                        phone = False
                    return phone
                else:
                    picking_object = self.pool.get('stock.picking')
                    picking_order = picking_object.browse(self.cr, self.uid, obj.id) 
                    if picking_order.partner_id.phone != False:
                        p_phone = picking_order.partner_id.phone 
                    else:
                        p_phone = False
                    return p_phone
            else:
                picking_object = self.pool.get('stock.picking')
                picking_order = picking_object.browse(self.cr, self.uid, obj.id) 
                if picking_order.partner_id.phone != False:
                    p_phone = picking_order.partner_id.phone 
                else:
                    p_phone = False
                return p_phone
              
            

    def get_partner_street(self, obj):
        sale_obj = self.pool.get('sale.order')
        if obj:
            if obj.origin:
                sale_order = sale_obj.search(self.cr, self.uid, [('name', '=', obj.origin)])
                if sale_order:
                    sale_browse = sale_obj.browse(self.cr, self.uid, sale_order[0])
                    if sale_browse.partner_shipping_id.street != False:
                        street = sale_browse.partner_shipping_id.street 
                    else:
                        street = False
                    return street
                else:
                    picking_object = self.pool.get('stock.picking')
                    picking_order = picking_object.browse(self.cr, self.uid, obj.id) 
                    if picking_order.partner_id.street != False:
                        p_street = picking_order.partner_id.street 
                    else:
                        p_street = False
                    return p_street
            else:
                picking_object = self.pool.get('stock.picking')
                picking_order = picking_object.browse(self.cr, self.uid, obj.id) 
                if picking_order.partner_id.street != False:
                    p_street = picking_order.partner_id.street 
                else:
                    p_street = False
                return p_street
                          
    def get_partner_street2(self, obj):
        sale_obj = self.pool.get('sale.order')
        if obj:
            street= ""
            if obj.origin:
                sale_order = sale_obj.search(self.cr, self.uid, [('name', '=', obj.origin)])
                if sale_order:
                    sale_browse = sale_obj.browse(self.cr, self.uid, sale_order[0])
                    if sale_browse.partner_shipping_id.street2 != False:
                        street = sale_browse.partner_shipping_id.street2 
                    return street
                else:
                    picking_object = self.pool.get('stock.picking')
                    picking_order = picking_object.browse(self.cr, self.uid, obj.id) 
                    if picking_order.partner_id.street2 != False:
                        p_street = picking_order.partner_id.street2 
                    else:
                        p_street = False
                    return p_street
            else:
                   
                picking_object = self.pool.get('stock.picking')
                picking_order = picking_object.browse(self.cr, self.uid, obj.id) 
                if picking_order.partner_id.street2 != False:
                    p_street = picking_order.partner_id.street2 
                else:
                    p_street = False
                return p_street


    def get_partner_zip(self, obj):
        sale_obj = self.pool.get('sale.order')
        if obj:
            if obj.origin:
                sale_order = sale_obj.search(self.cr, self.uid, [('name', '=', obj.origin)])
                if sale_order:
                    sale_browse = sale_obj.browse(self.cr, self.uid, sale_order[0])
                    if sale_browse.partner_shipping_id.zip != False or sale_browse.partner_shipping_id.city != False:
                        zip = sale_browse.partner_shipping_id.zip or ""
                        city = sale_browse.partner_shipping_id.city or ""
                        zipcity = zip + ', ' + city
                    else:
                        zipcity = False
                    return zipcity
                else:
                    picking_object = self.pool.get('stock.picking')
                    picking_order = picking_object.browse(self.cr, self.uid, obj.id) 
                    if picking_order.partner_id.zip != False or picking_order.partner_id.city != False:
                        p_zip = picking_order.partner_id.zip or ""
                        p_city = picking_order.partner_id.city or ""
                        p_zipcity = p_zip + ', ' + p_city
                    else:
                        p_zipcity = False
                    return p_zipcity
            else:
                picking_object = self.pool.get('stock.picking')
                picking_order = picking_object.browse(self.cr, self.uid, obj.id) 
                if picking_order.partner_id.zip != False and picking_order.partner_id.city != False:
                    p_zip = picking_order.partner_id.zip or ""
                    p_city = picking_order.partner_id.city or ""
                    p_zipcity = p_zip + ', ' + p_city
                else:
                    p_zipcity = False
                return p_zipcity


    def get_partner_country(self, obj):
        sale_obj = self.pool.get('sale.order')
        if obj:
            if obj.origin:
                sale_order = sale_obj.search(self.cr, self.uid, [('name', '=', obj.origin)])
                if sale_order:
                    sale_browse = sale_obj.browse(self.cr, self.uid, sale_order[0])
                    if sale_browse.partner_shipping_id.country_id.name != False:
                        country = sale_browse.partner_shipping_id.country_id.name
                    else:
                        country = False
                    return country
                else:
                    picking_object = self.pool.get('stock.picking')
                    picking_order = picking_object.browse(self.cr, self.uid, obj.id) 
                    if picking_order.partner_id.country_id.name != False:
                        p_country = picking_order.partner_id.country_id.name 
                    else:
                        p_country = False
                    return p_country
            else:
                picking_object = self.pool.get('stock.picking')
                picking_order = picking_object.browse(self.cr, self.uid, obj.id) 
                if picking_order.partner_id.country_id.name != False:
                    p_country = picking_order.partner_id.country_id.name 
                else:
                    p_country = False
                return p_country
               
    def get_partner_company_invoice(self, obj):
        sale_obj = self.pool.get('sale.order')
        if obj:
            if obj.origin:
                sale_order = sale_obj.search(self.cr, self.uid, [('name', '=', obj.origin)])
                if sale_order:
                    sale_browse = sale_obj.browse(self.cr, self.uid, sale_order[0])
                    if sale_browse.partner_invoice_id:
                        if sale_browse.partner_invoice_id.parent_id.name != False:
                            invoicing = sale_browse.partner_invoice_id.parent_id.name
                        else:
                            invoicing = False
                        return invoicing
                else:
                    picking_object = self.pool.get('stock.picking')
                    picking_order = picking_object.browse(self.cr, self.uid, obj.id) 
                    if picking_order.partner_id.name != False:
                        p_shipping = picking_order.partner_id.parent_id.name 
                    else:
                        p_shipping = False
            else:
                picking_object = self.pool.get('stock.picking')
                picking_order = picking_object.browse(self.cr, self.uid, obj.id) 
                if picking_order.partner_id.name != False:
                    p_shipping = picking_order.partner_id.parent_id.name 
                else:
                    p_shipping = False
        return p_shipping
                                
    def get_partner_name_invoice(self, obj):
        sale_obj = self.pool.get('sale.order')
        if obj:
            if obj.origin:
                sale_order = sale_obj.search(self.cr, self.uid, [('name', '=', obj.origin)])
                if sale_order:
                    sale_browse = sale_obj.browse(self.cr, self.uid, sale_order[0])
                    if sale_browse.partner_invoice_id.name != False:
                        name = sale_browse.partner_invoice_id.name
                    else:
                        name = False 
                    return name
                else:
                    picking_object = self.pool.get('stock.picking')
                    picking_order = picking_object.browse(self.cr, self.uid, obj.id) 
                    if picking_order.partner_id.name != False:
                        p_name = picking_order.partner_id.name 
                    else:
                        p_name = False
                    return p_name
            else:
                picking_object = self.pool.get('stock.picking')
                picking_order = picking_object.browse(self.cr, self.uid, obj.id) 
                if picking_order.partner_id.name != False:
                    p_name = picking_order.partner_id.name 
                else:
                    p_name = False
                return p_name
              
    def get_partner_street_invoice(self, obj):
        sale_obj = self.pool.get('sale.order')
        if obj:
            if obj.origin:
                sale_order = sale_obj.search(self.cr, self.uid, [('name', '=', obj.origin)])
                if sale_order:
                    sale_browse = sale_obj.browse(self.cr, self.uid, sale_order[0])
                    if sale_browse.partner_invoice_id.street != False:
                        street = sale_browse.partner_invoice_id.street
                    else:
                        street = False    
                    return street
                else:
                    picking_object = self.pool.get('stock.picking')
                    picking_order = picking_object.browse(self.cr, self.uid, obj.id) 
                    if picking_order.partner_id.street != False:
                        p_street = picking_order.partner_id.street 
                    else:
                        p_street = False
                    return p_street
            else:
                picking_object = self.pool.get('stock.picking')
                picking_order = picking_object.browse(self.cr, self.uid, obj.id) 
                if picking_order.partner_id.street != False:
                    p_street = picking_order.partner_id.street 
                else:
                    p_street = False
                return p_street

    def get_partner_street_invoice2(self, obj):
        sale_obj = self.pool.get('sale.order')
        if obj:
            if obj.origin:
                sale_order = sale_obj.search(self.cr, self.uid, [('name', '=', obj.origin)])
                if sale_order:
                    sale_browse = sale_obj.browse(self.cr, self.uid, sale_order[0])
                    if sale_browse.partner_invoice_id.street2 != False:
                        street = sale_browse.partner_invoice_id.street2
                    else:
                        street = False 
                    return street
                else:
                    picking_object = self.pool.get('stock.picking')
                    picking_order = picking_object.browse(self.cr, self.uid, obj.id) 
                    if picking_order.partner_id.street2 != False:
                        p_street = picking_order.partner_id.street2
                    else:
                        p_street = False
                    return p_street
            else:
                picking_object = self.pool.get('stock.picking')
                picking_order = picking_object.browse(self.cr, self.uid, obj.id) 
                if picking_order.partner_id.street2 != False:
                    p_street = picking_order.partner_id.street2 
                else:
                    p_street = False
                return p_street



    def get_invoice_partner_phone(self, obj):
        sale_obj = self.pool.get('sale.order')
        if obj:
            phone = ""
            if obj.origin:
                sale_order = sale_obj.search(self.cr,self.uid,[('name','=',obj.origin)])
                if sale_order:
                    sale_browse = sale_obj.browse(self.cr,self.uid,sale_order[0])
                    if sale_browse.partner_invoice_id.phone != False:
                        phone = sale_browse.partner_invoice_id.phone
                    else:
                        False 
                    return phone
                else:
                    picking_object = self.pool.get('stock.picking')
                    picking_order = picking_object.browse(self.cr, self.uid, obj.id) 
                    if picking_order.partner_id.phone != False:
                        p_phone = picking_order.partner_id.phone 
                    else:
                        p_phone = False
                    return p_phone
            else:
                picking_object = self.pool.get('stock.picking')
                picking_order = picking_object.browse(self.cr, self.uid, obj.id) 
                if picking_order.partner_id.phone != False:
                    p_phone = picking_order.partner_id.phone 
                else:
                    p_phone = False
                return p_phone
    
    def get_partner_zip_invoice(self, obj):
        sale_obj = self.pool.get('sale.order')
        if obj:
            if obj.origin:
                sale_order = sale_obj.search(self.cr, self.uid, [('name', '=', obj.origin)])
                if sale_order:
                    sale_browse = sale_obj.browse(self.cr, self.uid, sale_order[0])
                    if sale_browse.partner_invoice_id.zip != False and  sale_browse.partner_invoice_id.city != False:
                        zip = sale_browse.partner_invoice_id.zip or ""
                        city = sale_browse.partner_invoice_id.city  or ""
                        zipcity = zip + ',' + city
                    else:
                        zipcity = False
                    return zipcity
                else:
                    picking_object = self.pool.get('stock.picking')
                    picking_order = picking_object.browse(self.cr, self.uid, obj.id) 
                    if picking_order.partner_id.zip != False and picking_order.partner_id.city != False:
                        p_zip = picking_order.partner_id.zip or ""
                        p_city = picking_order.partner_id.city or ""
                        p_zipcity = p_zip + ', ' + p_city
                    else:
                        p_zipcity = False
                    return p_zipcity
            else:
                picking_object = self.pool.get('stock.picking')
                picking_order = picking_object.browse(self.cr, self.uid, obj.id) 
                if picking_order.partner_id.zip != False and picking_order.partner_id.city != False:
                    p_zip = picking_order.partner_id.zip or ""
                    p_city = picking_order.partner_id.city or ""
                    p_zipcity = p_zip + ', ' + p_city
                return p_zipcity
                    
    
    def get_partner_country_invoice(self, obj):
        sale_obj = self.pool.get('sale.order')
        if obj:
            if obj.origin:
                sale_order = sale_obj.search(self.cr, self.uid, [('name', '=', obj.origin)])
                if sale_order:
                    sale_browse = sale_obj.browse(self.cr, self.uid, sale_order[0])
                    if sale_browse.partner_invoice_id.country_id.name != False:
                        country = sale_browse.partner_invoice_id.country_id.name
                    else:
                        country = False 
                    return country
                else:
                    picking_object = self.pool.get('stock.picking')
                    picking_order = picking_object.browse(self.cr, self.uid, obj.id) 
                    if picking_order.partner_id.country_id.name != False:
                        p_country = picking_order.partner_id.country_id.name
                    else:
                        p_country = False
                    return p_country
            else:
                picking_object = self.pool.get('stock.picking')
                picking_order = picking_object.browse(self.cr, self.uid, obj.id) 
                if picking_order.partner_id.country_id.name != False:
                    p_country = picking_order.partner_id.country_id.name 
                else:
                    p_country = False 
                return p_country



class picking_note_report(osv.AbstractModel):
    _name = 'report.stock_extended_ept.report_picking_1'
    _inherit = 'report.abstract_report'
    _template = 'stock_extended_ept.report_picking_1'
    _wrapped_report_class = picking_reports