# -*- coding: utf-8 -*-
import base64
import datetime
import re
import json
from collections import defaultdict
from odoo.tools import pdf
from dateutil.relativedelta import relativedelta
import hashlib
import requests
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import formatLang
import io
import codecs


class Company(models.Model):
    _inherit = "res.company"
    type = fields.Selection([("B", "Business"), ("P", "Natural person"), ("F", "Foreigner"),
                             ], default="B", store=True, required=1)
    taxpayerActivityCode = fields.Char("Taxpayer Activity Code", required=1)
    client_id = fields.Char("Tax Client Id", required=1)
    client_secret = fields.Char("Tax Client Secret", required=1)
    api_url = fields.Char("Api Url", required=1)
    vat = fields.Char(related="partner_id.vat", string="Tax ID", readonly=False, required=1)

    token = fields.Text("Api Token")
    token_expiry = fields.Datetime("Token Expiry", readonly=1)
    api_id_url = fields.Char("Api Identification Url", required=1)
    signature_key_file = fields.Binary(string="Certificate Key", help="Certificate Key in PFX format")
    signature_pass_phrase = fields.Text(string="Certificate Passkey", help="Passphrase for the certificate key",
                                        copy=False)

    def get_token(self):
        if not self.client_secret or not self.client_secret or not self.api_url or not self.api_id_url:
            raise UserError(_("Please assign company date"))
        if not self.token_expiry or self.token_expiry < datetime.datetime.now():
            company = self
            url = f"{company.api_id_url}/connect/token"
            payload = f"grant_type=client_credentials&client_id={company.client_id}&client_secret={company.client_secret}&scope=InvoicingAPI"
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Cookie": "3f6bf69972563c3e0e619b78edf73035=4c858439db6b09d41fe30d2a5907be47"
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code==200:
                access = json.loads(response.text)
                self.sudo().token = access["access_token"]
                self.sudo().token_expiry = datetime.datetime.now() + relativedelta(hours=1)
                return self.sudo().token
            else:
                raise UserError(_(response.text))
        else:
            return self.token


class Partner(models.Model):
    _inherit = "res.partner"
    building_number = fields.Char("Building Number", store=True, required=1)
    floor = fields.Char("Floor", store=True)
    room = fields.Char("Room", store=True)
    branchId = fields.Char("Branch Id", store=True, default="0")
    tax_type = fields.Selection([("B", "Business"), ("P", "Natural person"), ("F", "Foreigner"),
                                 ], "Tax Type", default="B", store=True)
    state_id = fields.Many2one("res.country.state", string="State", ondelete="restrict",
                               domain="[( 'country_id', '=?', country_id)]", required=1)
    country_id = fields.Many2one("res.country", string="Country", ondelete="restrict", required=1)
    street = fields.Char(required=1)
    city = fields.Char(required=1)


class Invoice(models.Model):
    _inherit = "account.move"
    uuid = fields.Char("UUID", store=True, readonly=1, copy=0, tracking=True,)
    long_id = fields.Char("Long Id", store=True, readonly=1, copy=0, tracking=True,)
    doc_state = fields.Char("Document Status", store=True, readonly=1, copy=0, tracking=True,)
    doc_origin = fields.Char("Old Document", store=True, readonly=0, copy=0)
    discount_totals = fields.Monetary(string="Total Discount", compute="discount_total_amount", tracking=True)
    invoice_origin = fields.Char(string="Origin", readonly=False, tracking=True,
                                 help="The document(s) that generated the invoice.")
    doc_attach = fields.Binary()
    ref_uuid = fields.Char("Reference UUID", copy=0, tracking=True, )
    can_send = fields.Boolean(compute="can_send_e_invoice")
    cancelRequestDate = fields.Char("Cancel Request Date", readonly=1, copy=0, tracking=True, )
    rejectRequestDate = fields.Char("Reject Request Date", readonly=1, copy=0, tracking=True, )
    publicUrl = fields.Char("Public Url", readonly=1, copy=0, tracking=True, )
    documentStatusReason = fields.Selection([("Wrong buyer details", "Wrong buyer details"),
                                             ("Wrong invoice details", "Wrong invoice details")], "Cancellation Reason",
                                            copy=0, tracking=True, )

    def open_url(self):
        return {
            "type": "ir.actions.act_url",
            "target": "new",
            "url": self.publicUrl,
        }

    def cancel_e_invoice(self):
        company = self.env.company
        if not self.documentStatusReason:
            raise UserError(_("Please Choose Cancellation Reason"))
        url = f"{company.api_url}/api/v1.0/documents/state/{self.uuid}/state"

        payload = json.dumps({
            "status": "cancelled",
            "reason": "Wrong invoice details"
        })
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + company.get_token(),
            "Cookie": "75fd0698a2e84d6b8a3cb94ae54530f3=cfa1e52204bb4461a95abb903c8d00de"
        }

        response = requests.request("PUT", url, headers=headers, data=payload)
        if response.text != "true":
            raise UserError(_(response.text))
        self.get_document_info()

    def can_send_e_invoice(self):
        for record in self:
            record.can_send = False
            if record.state == "posted" and record.move_type in ("out_refund", "out_invoice"):
                if not record.uuid or (record.uuid and record.doc_state == "Invalid"):
                    record.can_send = True

    @api.onchange("invoice_line_ids")
    def discount_total_amount(self):
        for order in self:
            order.discount_totals = 0.00
            total_dist = 0
            for line in order.invoice_line_ids:
                total_dist += round((line.p_unit * line.quantity * line.discount / 100), 5)
            order.discount_totals = total_dist

        return

    def _compute_invoice_taxes_group(self):
        for move in self:

            # Not working on something else than invoices.
            if not move.is_invoice(include_receipts=True):
                move.amount_by_group = []
                continue
            lang_env = move.with_context(lang=move.partner_id.lang).env
            balance_multiplicator = -1 if move.is_inbound() else 1
            tax_lines = move.line_ids.filtered('tax_line_id')
            base_lines = move.line_ids.filtered('tax_ids')
            tax_group_mapping = defaultdict(lambda: {
                'base_lines': set(),
                'base_amount': 0.0,
                'tax_amount': 0.0,
            })

            # Compute base amounts.
            for base_line in base_lines:
                base_amount = balance_multiplicator * (
                    base_line.amount_currency if base_line.currency_id else base_line.balance)

                for tax in base_line.tax_ids.flatten_taxes_hierarchy():

                    if base_line.tax_line_id.tax_code == tax.tax_code:
                        continue

                    tax_group_vals = tax_group_mapping[tax.tax_code]
                    if base_line not in tax_group_vals['base_lines']:
                        tax_group_vals['base_amount'] += base_amount
                        tax_group_vals['base_lines'].add(base_line)

            # Compute tax amounts.
            for tax_line in tax_lines:
                tax_amount = balance_multiplicator * (
                    tax_line.amount_currency if tax_line.currency_id else tax_line.balance)
                tax_group_vals = tax_group_mapping[tax_line.tax_line_id.tax_code]
                tax_group_vals['tax_amount'] += tax_amount

            tax_groups = tax_group_mapping.keys()
            amount_by_group = []
            for tax_group in tax_groups:
                tax_group_vals = tax_group_mapping[tax_group]
                amount_by_group.append((
                    tax_group,
                    tax_group_vals['tax_amount'],
                    tax_group_vals['base_amount'],
                    formatLang(lang_env, tax_group_vals['tax_amount'], currency_obj=move.currency_id),
                    formatLang(lang_env, tax_group_vals['base_amount'], currency_obj=move.currency_id),
                    len(tax_group_mapping),
                    tax_group
                ))
            return amount_by_group

    def get_document_cana(self):
        document = self.get_document_data()
        # def document_rec(value):
        #     data=""
        #     if type(value) is dict:
        #         for d, r in o.items():
        #             if type(r) is dict:
        #                 data +document_rec(r)
        #             data += "\"" + str(d).upper() + "\""
        #             data += "\"" + str(r) + "\""
        #     return data
        new_value = ""
        for attribute, value in document.items():
            new_value += "\"" + attribute.upper() + "\""
            if type(value) is dict:
                for l, o in value.items():
                    new_value += "\"" + str(l).upper() + "\""
                    if type(o) is dict:
                        for d, r in o.items():
                            new_value += "\"" + str(d).upper() + "\""
                            new_value += "\"" + str(r) + "\""
                    else:
                        new_value += "\"" + str(o) + "\""
            elif value and type(value) is list:
                for t in value:
                    new_value += "\"" + attribute.upper() + "\""
                    for l, o in t.items():
                        new_value += "\"" + str(l).upper() + "\""
                        if type(o) is dict:
                            for n, z in o.items():
                                new_value += "\"" + str(n).upper() + "\""
                                new_value += "\"" + str(z) + "\""

                        elif type(o) is list:
                            for t in o:
                                new_value += "\"" + str(l).upper() + "\""
                                for q, w in t.items():
                                    new_value += "\"" + str(q).upper() + "\""
                                    if type(w) is dict:
                                        for a, x in w.items():
                                            new_value += "\"" + str(a).upper() + "\""
                                            new_value += "\"" + str(x) + "\""
                                    else:
                                        new_value += "\"" + str(w) + "\""
                        else:
                            new_value += "\"" + str(o) + "\""

            else:
                new_value += "\"" + str(value) + "\""
        new_str = new_value
        array = bytearray(new_str, 'utf_8')
        hasher = hashlib.sha256()
        hasher.update(array)
        data = hasher.digest()
        return new_str

        # return hashlib.sha256(new_value.encode("utf-8")).hexdigest()
        # return base64.b64encode(hashlib.sha256(new_value.encode()).hexdigest().encode())

    def get_document_data(self):
        invoice_lines = []
        taxTotals = []
        document = {}
        for record in self:
            if record.move_type == "out_invoice":
                type = "I"
            elif record.move_type == "out_refund":
                type = "C"
            else:
                type = ""
            amount_by_group = record._compute_invoice_taxes_group()
            if amount_by_group:
                for tax in amount_by_group:
                    taxTotals.append({
                        "taxType": tax[0],
                        "amount": round(tax[1] / record.currency_id.rate, 5)
                    })
            if not taxTotals:
                taxTotals.append({
                    "taxType": "T1",
                    "amount": 0.0
                })
            issuer = {
                "address": {"branchId": record.company_id.partner_id.branchId or "0",
                            "country": record.company_id.partner_id.country_id.code or "",
                            "governate": record.company_id.partner_id.state_id.name or "",
                            "regionCity": record.company_id.partner_id.city or "",
                            "street": record.company_id.partner_id.street or "",
                            "buildingNumber": record.company_id.partner_id.building_number or "",
                            "floor": record.company_id.partner_id.floor or "",
                            "room": record.company_id.partner_id.room or "",
                            "landmark": "",
                            "postalCode": record.company_id.partner_id.zip or "",
                            "additionalInformation": "",

                            },
                "type": record.company_id.type or "",
                "id": record.company_id.vat or "",
                "name": record.company_id.name or "",
            }
            receiver = {
                "address": {
                    "country": record.partner_id.country_id.code or "",
                    "governate": record.partner_id.state_id.name or "",
                    "regionCity": record.partner_id.city or "",
                    "street": record.partner_id.street or "",
                    "buildingNumber": record.partner_id.building_number or "",
                    "floor": record.partner_id.floor or "",
                    "room": record.partner_id.room or "",
                    "landmark": "",
                    "additionalInformation": "",
                    "postalCode": record.partner_id.zip or "",

                },
                "type": record.partner_id.tax_type or "",
                "id": record.partner_id.vat or "",
                "name": record.partner_id.name or "",
            }
            discount_totals = 0.0
            extradiscount_totals = 0.0
            for line in record.invoice_line_ids:
                taxes = []
                total_tax = 0
                itemsDiscount = 0
                if line.tax_ids:
                    unit = line.p_unit - (line.p_unit * line.discount / 100)
                    if line.sale_type == "bouns":
                        unit = line.p_unit - (line.p_unit * line.discount / 100)
                    taxes2 = line.tax_ids.compute_all(unit,
                                                      line.move_id.currency_id, line.quantity, product=line.product_id,
                                                      partner=line.move_id.partner_id)
                    for tax in taxes2["taxes"]:
                        total_tax += round(tax["amount"], 5)
                        tax_id = line.tax_ids.filtered(lambda t: t.id == tax["id"])
                        if not tax_id.tax_code:
                            raise UserError(_("Please Define Tax Code For taxes"))
                        taxes.append({
                            "taxType": line.tax_ids.filtered(lambda t: t.id == tax["id"]).tax_code,
                            "amount": round(tax["amount"] / record.currency_id.rate, 5),
                            "subType": line.tax_ids.filtered(lambda t: t.id == tax["id"]).subtype,
                            "rate": line.tax_ids.filtered(lambda t: t.id == tax["id"]).amount
                        })
                if line.sale_type == "bouns":
                    price = 0
                    price_dif = round(
                        (line.p_unit - (line.p_unit * line.discount / 100)) * line.quantity,
                        5)
                    total = total_tax
                    netTotal = round(line.price_subtotal, 5)
                    discounts = {
                        "rate": 0,
                        "amount": 0
                    }
                else:
                    itemsDiscount = round(line.quantity * line.p_unit * (line.discount / 100), 5)
                    price = line.p_unit
                    price_dif = 0
                    total = line.price_total
                    netTotal = round(line.price_subtotal, 5)
                    discounts = {
                        "rate": line.discount,
                        "amount": round(itemsDiscount / record.currency_id.rate, 5)
                    }
                    discount_totals += itemsDiscount
                    itemsDiscount = 0

                invoice_lines.append({
                    "description": line.name or "",
                    "itemType": line.product_id.item_type or "",
                    "itemCode": line.product_id.item_code or "",
                    "internalCode": line.product_id.default_code or "",
                    "unitType": line.product_uom_id.unitCode or "EA",
                    "quantity": line.quantity,
                    "unitValue": {
                        "currencySold": record.currency_id.name,
                        "amountEGP": round (price / record.currency_id.rate ,5),
                        "amountSold": 0.0 if record.company_id.currency_id == record.currency_id else price,
                        "currencyExchangeRate": 0.0 if record.company_id.currency_id == record.currency_id else round(1 / record.currency_id.rate, 5)
                    },
                    "salesTotal": round(line.quantity * round(price / record.currency_id.rate , 5), 5),
                    "valueDifference":  round(price_dif / record.currency_id.rate, 5),
                    "totalTaxableFees": 0.0,
                    "discount":  discounts,

                    "netTotal": round(netTotal / record.currency_id.rate, 5),
                    "itemsDiscount": round(itemsDiscount / record.currency_id.rate, 5),
                    "taxableItems": taxes,
                    "total":round(total / record.currency_id.rate, 5),

                })

            document = {
                "issuer": issuer,
                "receiver": receiver,
                "documentType": type,
                "documentTypeVersion": "1.0",
                "dateTimeIssued": str(record.invoice_date) + "T00:00:00Z",
                "taxpayerActivityCode": record.company_id.taxpayerActivityCode or "",
                "purchaseOrderReference": "",
                "purchaseOrderDescription": "",
                "salesOrderReference": record.invoice_origin or "",
                "salesOrderDescription": "",
                "proformaInvoiceNumber": "",
                "payment": {
                    "bankName": "",
                    "bankAddress": "",
                    "bankAccountNo": "",
                    "bankAccountIBAN": "",
                    "swiftCode": "",
                    "terms": ""
                },
                "delivery": {
                    "approach": "",
                    "packaging": "",
                    "dateValidity": "",
                    "exportPort": "",
                    "countryOfOrigin": "",
                    "grossWeight": 0.0,
                    "netWeight": 0.0,
                    "terms": ""
                },
                "internalID": record.name,
                "invoiceLines": invoice_lines,
                "totalSalesAmount": round((record.amount_untaxed + discount_totals + extradiscount_totals )/ record.currency_id.rate, 5),
                "totalDiscountAmount": round(discount_totals / record.currency_id.rate, 5),
                "netAmount": round((record.amount_untaxed + extradiscount_totals) / record.currency_id.rate, 5),
                "taxTotals": taxTotals,
                "extraDiscountAmount": 0.0,
                "totalItemsDiscountAmount":  round(extradiscount_totals / record.currency_id.rate, 5),
                "totalAmount": round(record.amount_total / record.currency_id.rate, 5),

            }
            if record.move_type == "out_refund" and record.ref_uuid:
                document["references"] = record.ref_uuid.split(",")
            # if record.invoice_origin:
            #     document["salesOrderReference"] = record.invoice_origin
        return document

    def send_e_invoice(self):
        for record in self:
            document = record.get_document_data()
            document["documentTypeVersion"] = "0.9"

            payload = json.dumps({
                "documents": [document]})
            company = record.env.company.sudo()
            url = f"{company.api_url}/api/v1/documentsubmissions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + company.get_token()
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            print(response.status_code)

            if response.status_code == 202:
                response_dict = response.json()
                if response_dict.get("acceptedDocuments"):
                    record.uuid = response_dict.get("acceptedDocuments")[0]["uuid"]
                    record.long_id = response_dict.get("acceptedDocuments")[0]["longId"]
                if response_dict.get("rejectedDocuments"):
                    raise UserError(_(response_dict["rejectedDocuments"]))
            else:
                raise UserError(_(response.text))

    def send_e_invoice_sign(self, signature):
        for record in self:
            document = record.get_document_data()
            if signature:
                print(signature)
                document["signatures"] = [{
                    "signatureType": "I",
                    "value": signature
                }]
            payload = json.dumps({
                "documents": [document]}, ensure_ascii=False)
            print(payload)
            company = record.env.company.sudo()
            url = f"{company.api_url}/api/v1.0/documentsubmissions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + company.get_token()
            }
            response = requests.request("POST", url, headers=headers, data=str(payload).encode('utf-8'))
            print(response.status_code)
            if response.status_code == 202:
                response_dict = response.json()
                if response_dict["acceptedDocuments"]:
                    record.uuid = response_dict["acceptedDocuments"][0]["uuid"]
                    record.long_id = response_dict["acceptedDocuments"][0]["longId"]
                if response_dict["rejectedDocuments"]:
                    raise UserError(_(response_dict["rejectedDocuments"]))
            else:
                raise UserError(_(response.text))

    def get_document_info(self):
        for record in self:
            company = record.env.company
            url = f"{company.api_url}/api/v1/documents/{record.uuid}/details"

            payload = {}
            headers = {
                "Authorization": "Bearer " + company.get_token(),
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            response_dict = response.json()
            if response_dict and response.status_code == 200:
                if response_dict["validationResults"]:
                    record.doc_state = response_dict["validationResults"]["status"]
                if response_dict["cancelRequestDate"]:
                    record.cancelRequestDate = response_dict["cancelRequestDate"]
                if response_dict["documentStatusReason"]:
                    record.documentStatusReason = response_dict["documentStatusReason"]
                if response_dict["rejectRequestDate"]:
                    record.rejectRequestDate = response_dict["rejectRequestDate"]
                if response_dict["publicUrl"]:
                    record.publicUrl = response_dict["publicUrl"]
            elif response.status_code != 200:
                raise UserError(_(response_dict["error"]))

    def get_document_file(self):
        for record in self:
            company = record.env.company
            url = f"{company.api_url}/api/v1/documents/{record.uuid}/pdf"

            payload = {}
            headers = {
                "Authorization": "Bearer " + company.get_token(),
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                record.with_context(no_new_invoice=True).message_post(body=_('ETA invoice has been received'),
                                                                      attachments=[('ETA invoice of %s.pdf' % record.name,
                                                                                  response.content)])

            elif response.status_code != 200:
                raise UserError(_(response.json().get("error")))

    #

    @api.onchange('state')
    def onchange_state_tax(self):
        self._recompute_tax_lines()


