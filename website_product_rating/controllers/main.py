# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import werkzeug.urls
import werkzeug.wrappers
from odoo import http, SUPERUSER_ID
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale



class WebsiteProductReviewRating(WebsiteSale):
    @http.route(['/shop/product/comment/<int:product_template_id>'], type='http', auth="public", methods=['POST'], website=True)

    def website_product_review(self, product_template_id, **post):
        cr, uid, context = request.cr, request.uid, request.context
        description=post.get('short_description')
        review_rate = post.get('review')
        comment = post.get('comment')
        #customer_id = request.uid
        
        reviews_ratings = request.env['reviews.ratings'].sudo()
        reviews_ratings.sudo().create({'message_rate':review_rate, 'short_desc':description, 'review':comment, 'website_message':True, 'rating_product_id':product_template_id, 'customer_id':uid})

        return werkzeug.utils.redirect( request.httprequest.referrer + "#reviews" )

