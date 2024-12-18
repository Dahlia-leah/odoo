from odoo import models, fields, api


class Product(models.Model):
    _inherit = 'product.template'

    item_type = fields.Selection([('GS1','GS1'),
                                  ('EGS','EGS'),
                                  ],string='ItemType',default='GS1')
    item_code = fields.Char('ItemCode')
    item_pricing = fields.Selection([('before','Before Discount'), ('after', 'After Discount')], default='after')


class UOM(models.Model):
    _inherit = 'uom.uom'

    unitCode = fields.Char('Unit Code')


class AccountingTax(models.Model):
    _inherit = 'account.tax'
    tax_code = fields.Char('Tax Code')
    subtype = fields.Char('Tax Sub Type')


class AccountingTaxGroup(models.Model):
    _inherit = 'account.tax.group'
    tax_code = fields.Char('Tax Code')

