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
    'name': 'Sasmar Theme',
    'description': 'Sasmar Theme For Odoo v12 Enterprise Edition',
    'category': 'Theme/Ecommerce',
    'version': '12.0.0.0',
    'author': 'BrowseInfo',
    'depends': ['base','website','website_sale','website_crm'],#,'product_bundle','delivery_shipwire', #'theme_default', 'website_multi_image_zoom',  'website_product_rating', 'website_region'
    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/templates/sasmar_theme.xml',
        'views/templates/product_view.xml',
        'views/templates/single_product_page.xml',
        'views/templates/cart_page.xml',
        'views/templates/checkout_page.xml',
        'views/templates/product_page.xml',
        'views/templates/faq.xml',
        'views/templates/retailers.xml',
        'views/templates/about_us.xml',
        'views/templates/free_shipping.xml',
        'views/templates/your_privacy.xml',
        'views/templates/our_terms.xml',
        'views/templates/wholesale_orders.xml',
        'views/templates/helpdesk.xml',
        'views/templates/contact_us.xml',
        'views/templates/register_page.xml',
        'views/templates/thanks_for_register_page.xml',
        
        'views/templates/our_mission.xml',
        'views/templates/our_responsibility.xml',
        'views/templates/innovation.xml',
        'views/templates/research_development.xml',
        'views/templates/partnerships.xml',
        'views/templates/submit_an_idea.xml',
        'views/templates/our_brands.xml',
        'views/templates/sasmar_brand_personal_lubricant.xml',
        'views/templates/conceive_plus.xml',
        'views/templates/erexia.xml',
        'views/templates/purfeet.xml',
        'views/templates/working_at_sasmar.xml',
        'views/templates/sitemap.xml',
        'views/templates/press_office.xml',
        'views/templates/careers.xml',
    ],
    'application': True,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
