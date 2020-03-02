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

{
    'name': 'Website Region',
    'description': 'When region has been selected that particular pricelist has been applied on webshop, and once order has been placed this price-list linked to webshop.',
    'category': 'Pricelist/Ecommerce',
    'version': '12.0.0.0',
    'author': 'BrowseInfo',
    'depends': ['base','sale_management','product','website','website_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/region.xml',
        'views/template.xml',
        #'data/data.xml',
        
    ],
    'application': True,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
