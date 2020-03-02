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
    'name': 'Website Product Request Sample',
    'description': 'Request Product Demo/Sample in Webshop',
    'category': 'eCommerce',
    'version': '12.0.0.0',
    'author': 'BrowseInfo',
    'depends': ['sale_management','website','website_sale','mass_mailing'],
    'data': [
        'views/templates/sample_request_page.xml',
        'views/templates/product_view.xml',
        'views/templates/partner_mass_mail.xml',
        'edi/product_sample_email.xml',
        'security/ir.model.access.csv',
    ],
    'application': True,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
