# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2014-Today BrowseInfo (<http://www.browseinfo.in>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
from odoo.http import request
from geoip import geolite2 # install these 2 packages
#pip install python-geoip
#pip install python-geoip-geolite2

import os

ip_add  = os.popen("wget http://ipecho.net/plain -O - -q ; echo").read()
match = geolite2.lookup(ip_add[:-1])

# Add comments in Cart page...        
    @http.route(['/shop/addcomments'], type='http', auth="public", methods=['POST'], website=True)
    def add_comments(self, **post):
        orm_partner = request.registry.get('res.partner')
        
        logo = post['logo']
        
        logodict = {'logo':logo}

        order = request.website.sale_get_order(force_create=1)
    
        comments = post['comments']
        vals = {'comments':comments}

        #sale_order =  request.registry['sale.order'].write(cr,SUPERUSER_ID,sale_order_id,vals,context=context)        
        
        order.partner_id.write(logodict)
        order.write(vals)
        
        return request.redirect("/shop/cart")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
