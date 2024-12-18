from dataclasses import dataclass
import ast
import base64
import datetime
import dateutil
import email
import email.policy
import hashlib
import hmac
import lxml
import logging
import pytz
import re
import socket
import time
import threading

from collections import namedtuple
from email.message import EmailMessage
from email import message_from_string, policy
from lxml import etree
from werkzeug import urls
from xmlrpc import client as xmlrpclib

from odoo import _, api, exceptions, fields, models, tools, registry, SUPERUSER_ID
from odoo.exceptions import MissingError
from odoo.osv import expression

from odoo.tools import ustr
from odoo.tools.misc import clean_context, split_every

from odoo import api, fields, models, _

import requests
import logging

_logger = logging.getLogger(__name__)


class InvoiceLines(models.Model):
    _inherit = 'account.move'

    def api_get_recent(self):
    def api_get_recent(self):
        for company in self.env.companies.filtered(lambda co: co.api_url):
            attachement_values_list = []

            url = f"{company.api_url}/api/v1.0/documents/recent?pageNo=&pageSize=1"  # ?pageNo={pageNo}&pageSize={pageSize}
            token = company.sudo().get_token()
            if not token:
                # self._raise_query_error("Not valid access token")
                return

            # headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Accept-Language': 'ar',
            #           'Authorization': f'bearer {token}'}

            headers = {
                "Authorization": "Bearer " + company.get_token(),
            }

            response = requests.request("GET", url, headers=headers, data={})
            _logger.info(f'{url} called {response.text}  {response.status_code}')

            if response.status_code == 200:
                result = response.json()
                for doc in result.get('result'):
                    invoice = self.env['account.move'].search([('uuid', '=', doc['uuid'])], limit=1)
                    if invoice:
                        if doc.get("status"):
                            invoice.doc_state = doc["status"]
                        if doc["cancelRequestDate"]:
                            invoice.cancelRequestDate = doc["cancelRequestDate"]
                        if doc.get("documentStatusReason"):
                            invoice.documentStatusReason = doc["documentStatusReason"]
                        if doc.get("rejectRequestDate"):
                            invoice.rejectRequestDate = doc["rejectRequestDate"]
                        if doc.get("publicUrl"):
                            invoice.publicUrl = doc["publicUrl"]
                    else:
                        attach = self.env['ir.attachment'].search(['|', ('name', '=', doc['uuid'] + ".pdf",),
                                                                   ('name', '=', doc['uuid'])], limit=1)
                        if not attach:
                            url1 = f"{company.api_url}/api/v1/documents/{doc['uuid']}/pdf"

                            payload1 = {}
                            headers1 = {
                                "Authorization": "Bearer " + company.get_token(),
                            }

                            response1 = requests.request("GET", url1, headers=headers1, data=payload1)
                            if response1.status_code == 200:
                                content = response1.content
                                if isinstance(content, str):
                                    content = content.encode('utf-8')
                                elif isinstance(content, EmailMessage):
                                    content = content.as_bytes()
                                attachement_values = {
                                    'name': doc['uuid'] + ".pdf",
                                    'datas': base64.b64encode(content),
                                    'type': 'binary',
                                    'description': f"Issuer id :{doc['issuerId']} Issuer Name :{doc['issuerName']} Document Date: {doc['dateTimeIssued']}" ,
                                    'res_model': 'account.move',
                                    'res_id': 0,
                                    'public': True,
                                }
                                attachement_values_list.append(attachement_values)
            if attachement_values_list:
                self.env['ir.attachment'].create(attachement_values_list)
