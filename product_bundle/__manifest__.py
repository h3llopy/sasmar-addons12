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
    "name": "Bundle Product",
    "category": 'Sales Management',
    "summary": """
       Combine two or more products together in order to create a bundle product.""",
    "description": """
    """,
    "sequence": 1,
    "author": "BrowseInfo",
    "website": "http://www.browseinfo.in",
    "version": '12.0.0.0',
    "depends": ['sale','product','stock','sale_stock', 'sasmar_user_preference'],
    "data": [
        'views/product_view.xml',
        'wizard/product_bundle.xml',
        'security/ir.model.access.csv',
        'report/sale_report_view.xml',
    ],
    "price": 39,
    "currency": 'EUR',
    "installable": True,
    "application": True,
    "auto_install": False,
}
