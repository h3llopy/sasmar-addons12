from openerp import fields, models ,api

class product_product(models.Model):

    _inherit = "product.product"
    
    shipwire_product_id = fields.Integer("Shipwire Product ID",copy=False)
    product_sync = fields.Boolean("Product Sync",copy=False)
    shipwire_length = fields.Float("Length",help="In inches.")
    shipwire_width = fields.Float("Width",help="In inches.")
    shipwire_height = fields.Float("Height",help="In inches.")
    shipwire_weight = fields.Float("Weight",help="In lbs.")
    
    _sql_constraints = [
        ('shipwire_product_id_uniq',
         'unique (barcode,shipwire_product_id)',
         'Shipwire product can be sync with one product only')
    ]

    