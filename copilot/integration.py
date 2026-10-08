"""Read-only anti-corruption layer: fixed route, authorization, schema, projection."""
import re
from urllib.parse import urlencode
from .security import Fault, require_company
from .transport import request_json, local_url

PO_PATTERN = re.compile(r'^\d{10}$')
SAFE_FIELDS = ('PurchaseOrder','CompanyCode','SupplierName','NetAmount','Currency',
               'Status','ExceptionCode','LastChangedAt')
EXCEPTIONS = {'receipt_missing':'goods receipt invoice matching',
              'approval_required':'approval high value', 'none':''}

class SAPClient:
    def __init__(self, base_url, service_token, identity):
        self.base_url = local_url(base_url)
        self.service_token, self.identity = service_token, identity

    def purchase_order(self, principal, company, po_id):
        require_company(principal, company)
        if not PO_PATTERN.fullmatch(po_id):
            raise Fault(400, 'invalid_purchase_order')
        result = request_json(
            f"{self.base_url}/odata/PurchaseOrders('{po_id}')?"+urlencode({'company':company}),
            {'Authorization':'Bearer '+self.identity.token_for(principal),
             'X-Service-Token':self.service_token})
        if not isinstance(result, dict) or not isinstance(result.get('value'), dict):
            raise Fault(502, 'upstream_invalid')
        row = result['value']
        if row.get('PurchaseOrder') != po_id or row.get('CompanyCode') != company:
            raise Fault(502, 'upstream_invalid')
        if any(not isinstance(row.get(k), str) or len(row[k]) > 200 for k in SAFE_FIELDS):
            raise Fault(502, 'upstream_invalid')
        if (row['ExceptionCode'] not in EXCEPTIONS or row['Status'] not in ('Blocked','Open')
            or row['Currency'] not in ('EGP','SAR') or not re.fullmatch(r'\d+(\.\d{2})?',row['NetAmount'])):
            raise Fault(502, 'upstream_invalid')
        return {k:row[k] for k in SAFE_FIELDS}
