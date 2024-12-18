import base64
import datetime
import re
import json
from dateutil.relativedelta import relativedelta
import hashlib
# import pkcs11
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import binascii
import requests
# from pkcs11 import Attribute, ObjectClass
# from asn1crypto import cms, util, algos, x509, tsp, core


class Invoice(models.Model):
    _inherit = 'account.move'

    # def Esign(self):
    #     token_label = 'Egypt Trust'
    #     user_pin = '85473359'
    #     new_str = self.get_document_cana()
    #     print(new_str)
    #     array = bytearray(new_str, 'utf_8')
    #     hasher = hashlib.sha256()
    #     hasher.update(array)
    #     data = hasher.digest()
    #     lib = pkcs11.lib('C:/Windows/System32/eps2003csp11.dll')
    #     # lib=pkcs11.lib('C:\Windows\SysWOW64\opensc_pkcs11.dll')
    #     try:
    #         token = lib.get_token(token_label=token_label)
    #     except:
    #         return 'Token is not connected', 201
    #     # token.exit()
    #     # pkcs11.session.close()
    #     try:
    #         session = token.open(user_pin=user_pin)
    #     except:
    #         return 'Token pin is not available now', 201
    #     privateKey = next(session.get_objects({
    #         Attribute.CLASS: ObjectClass.PRIVATE_KEY}))
    #     certObj = next(session.get_objects({
    #         Attribute.CLASS: ObjectClass.CERTIFICATE}))
    #
    #     cert = x509.Certificate.load(certObj[Attribute.VALUE])
    #     signed_value = privateKey.sign(
    #         bytes(data),
    #         mechanism=pkcs11.mechanisms.Mechanism.SHA256_RSA_PKCS)
    #     signed_value
    #     signed_time = datetime.datetime.now(tz=util.timezone.utc)
    #     bytesha256Cert = hashlib.sha256(cert.dump()).digest()
    #     EsscerttificateIDv2 = tsp.ESSCertIDv2()
    #     EsscerttificateIDv2['hash_algorithm'] = algos.DigestAlgorithm({'algorithm': "sha256"})
    #     EsscerttificateIDv2['cert_hash'] = bytesha256Cert
    #     ESSCertIDv2s = [EsscerttificateIDv2]
    #     ESSSigningCertificateV2 = tsp.SigningCertificateV2()
    #     ESSSigningCertificateV2['certs'] = ESSCertIDv2s
    #     MessagedigestV = bytes(data)
    #     signer = {
    #         'version': 'v1',
    #         'sid': cms.SignerIdentifier({
    #             'issuer_and_serial_number': cms.IssuerAndSerialNumber({
    #                 'issuer': cert.issuer,
    #                 'serial_number': cert.serial_number,
    #             }),
    #         }),
    #         'digest_algorithm': algos.DigestAlgorithm({'algorithm': "sha256"}),
    #         'signature': signed_value,
    #     }
    #     signer['signature_algorithm'] = algos.SignedDigestAlgorithm({'algorithm': "sha256_rsa"})
    #     signer['signed_attrs'] = [
    #         tsp.CMSAttribute({
    #             'type': tsp.CMSAttributeType('content_type'),
    #             'values': (tsp.ContentType('digested_data'),),
    #         }),
    #         tsp.CMSAttribute({
    #             'type': tsp.CMSAttributeType('message_digest'),
    #             'values': (MessagedigestV,),
    #         }),
    #         tsp.CMSAttribute({
    #             'type': tsp.CMSAttributeType('signing_time'),
    #             'values': (cms.Time({'utc_time': core.UTCTime(signed_time)}),)
    #         }),
    #         tsp.CMSAttribute({
    #             'type': tsp.CMSAttributeType('signing_certificate_v2'),
    #             'values': (ESSSigningCertificateV2,)
    #         }),
    #
    #     ]
    #     sd = cms.SignedData()
    #     sd['version'] = 'v3'
    #     encabContentInfo = cms.EncapsulatedContentInfo()
    #     encabContentInfo['content_type'] = "digested_data"
    #     sd['encap_content_info'] = encabContentInfo
    #     sd['digest_algorithms'] = [util.OrderedDict([
    #         ('algorithm', 'sha256'),
    #         ('parameters', None)])]
    #     sd['certificates'] = [cert]
    #     sd['signer_infos'] = [signer]
    #     asn1obj = cms.ContentInfo()
    #     asn1obj['content_type'] = 'signed_data'
    #     asn1obj['content'] = sd
    #     tosign = asn1obj['content']['signer_infos'][0]['signed_attrs'].dump()
    #     tosign = b'\x31' + tosign[1:]
    #     signaturesss = privateKey.sign(
    #         bytes(tosign),
    #         mechanism=pkcs11.mechanisms.Mechanism.SHA256_RSA_PKCS)
    #     asn1obj['content']['signer_infos'][0]['signature'] = signaturesss
    #     with open('signed_data1.der', 'wb+') as fout:
    #         fout.write(asn1obj.dump())
    #     base64.encode(open('signed_data1.der', 'rb'), open('hashedvaluetobesent.txt', 'wb'))
    #     f = open("hashedvaluetobesent.txt", "r")
    #     hashedValue = f.read()
    #     newtext = re.sub(r'(?<!\n)\n(?![\n\t])', ' ', hashedValue.replace('\r', ''))
    #     session.close()
    #     self.send_e_invoice_sign(newtext.rstrip())
    #
    #     # data = self.get_document_cana()
    #     # print(data)
    #     # headers = {
    #     #     'Content-Type': 'text/plain',
    #     # }
    #     # url = "https://localhost:44384/api/InvoiceHasher/Hash"
    #     # respond = requests.post(url, headers=headers, data=data, verify=False)
    #     # print(respond.text)
    #     #
    #     # data = respond.text
    #     # print(str(self.get_document_cana()))
    #     # signature_response = requests.get('http://192.168.1.161:5000/sign',
    #     #                                   verify=False, params={"data":self.get_document_cana(),
    #     #                                   'user_pin': '85473359',
    #     #                                    8.text
    #     # self.send_e_invoice_sign(signature_data)

#
