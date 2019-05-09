import datetime
import hashlib
import hmac
import httplib
from urllib import quote
from urlparse import urlparse
import requests

def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

def getSignatureKey(key, dateStamp, regionName, serviceName):
    kDate = sign(('AWS4' + key).encode('utf-8'), dateStamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, 'aws4_request')
    return kSigning

class AWSRequestsAuth(requests.auth.AuthBase):
    def __init__(self,
                 aws_access_key,
                 aws_secret_access_key,
                 aws_host,
                 aws_region,
                 aws_service):

        self.aws_access_key = aws_access_key
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_host = aws_host
        self.aws_region = aws_region
        self.service = aws_service

    def __call__(self, r):
        aws_headers = self.get_aws_request_headers(r=r, aws_access_key=self.aws_access_key,
                                                   aws_secret_access_key=self.aws_secret_access_key)
        r.headers.update(aws_headers)
        return r

    def get_aws_request_headers(self, r, aws_access_key, aws_secret_access_key):
        t = datetime.datetime.utcnow()
        amzdate = t.strftime('%Y%m%dT%H%M%SZ')
        datestamp = t.strftime('%Y%m%d')

        canonical_uri = AWSRequestsAuth.get_canonical_path(r)
        canonical_querystring = AWSRequestsAuth.get_canonical_querystring(r)
        canonical_headers = ('host:' + self.aws_host + '\n' + 'x-amz-date:' + amzdate + '\n')
        signed_headers = 'host;x-amz-date'
        body = (r.body if r.body else bytes()).encode('utf-8')
        payload_hash = hashlib.sha256(body).hexdigest()

        canonical_request = "\n".join([
            r.method,
            canonical_uri,
            canonical_querystring,
            canonical_headers,
            signed_headers,
            payload_hash,
        ])

        algorithm = 'AWS4-HMAC-SHA256'
        credential_scope = '/'.join([
            datestamp,
            self.aws_region,
            self.service,
            'aws4_request',
        ])
        string_to_sign = '\n'.join([
            algorithm,
            amzdate,
            credential_scope,
            hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
        ])
        signing_key = getSignatureKey(aws_secret_access_key, datestamp, self.aws_region, self.service)

        string_to_sign_utf8 = string_to_sign.encode('utf-8')
        signature = hmac.new(signing_key, string_to_sign_utf8, hashlib.sha256).hexdigest()

        authorization_header = '%s Credential=%s/%s, SignedHeaders=%s, Signature=%s' % (algorithm,
                                                                                        aws_access_key,
                                                                                        credential_scope,
                                                                                        signed_headers,
                                                                                        signature,
                                                                                        )
        headers = {
            'Authorization': authorization_header,
            'x-amz-date': amzdate,
            'x-amz-content-sha256': payload_hash
        }
        return headers

    @classmethod
    def get_canonical_path(cls, r):
        parsedurl = urlparse(r.url)
        return quote(parsedurl.path if parsedurl.path else '/', safe='/-_.~')

    @classmethod
    def get_canonical_querystring(cls, r):
        canonical_querystring = ''

        parsedurl = urlparse(r.url)
        querystring_sorted = '&'.join(sorted(parsedurl.query.split('&')))

        for query_param in querystring_sorted.split('&'):
            key_val_split = query_param.split('=', 1)

            key = key_val_split[0]
            if len(key_val_split) > 1:
                val = key_val_split[1]
            else:
                val = ''

            if key:
                if canonical_querystring:
                    canonical_querystring += "&"
                canonical_querystring += u'='.join([key, val])

        return canonical_querystring


def patch_send():
    old_send = httplib.HTTPConnection.send

    def new_send(self, data):
        print data
        return old_send(self, data)  # return is not necessary, but never hurts, in case the library is changed

    httplib.HTTPConnection.send = new_send


patch_send()

auth = AWSRequestsAuth(aws_access_key='lv89_user1',
                       aws_secret_access_key='N9cB0RE3393FVvZB1O80qVPij9cQihKujKEetD9J',
                       aws_host='cmbdev.kxecs.itc.cmbchina.cn:9020',
                       aws_region='us-east-1',
                       aws_service='execute-api')
response = requests.get('http://cmbdev.kxecs.itc.cmbchina.cn:9020', auth=auth)
# print response.content
