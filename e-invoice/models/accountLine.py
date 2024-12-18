from odoo import api, fields, models, _

INTEGRITY_HASH_MOVE_FIELDS = ('date', 'journal_id', 'company_id')
INTEGRITY_HASH_LINE_FIELDS = ('debit', 'credit', 'account_id', 'partner_id')


class InvoiceLines(models.Model):
    _inherit = 'account.move.line'
    sale_type = fields.Selection(string="Product Type", selection=[('sale', 'Sale'), ('bouns', 'Bouns')],
                                 default='sale', store=True)
    price_new = fields.Float('New Price',store=True, digits='Product Price')

    @api.onchange('sale_type')
    def sale_type_change(self):
        if self.sale_type=='sale':
            self.price_unit = self.product_id.lst_price










