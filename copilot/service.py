"""Application policy owns routing, retrieval and rendering, never the model."""
import re
import time
from .security import Fault, require_company, suspicious, WRITE
from .integration import PO_PATTERN, EXCEPTIONS
from .providers import validate_selection

BUSINESS = re.compile(r'\b(purchase|order|po|blocked|receipt|invoice|approval|policy|threshold|supplier|payment|matching)\b', re.I)

class Copilot:
    def __init__(self, index, sap, provider):
        self.index, self.sap, self.provider = index, sap, provider

    def ask(self, principal, payload):
        start = time.perf_counter()
        if not isinstance(payload, dict) or set(payload)-{'company_code','purchase_order','question'}:
            raise Fault(400, 'invalid_request')
        company, question, po_id = (payload.get('company_code'),payload.get('question'),payload.get('purchase_order'))
        if (not isinstance(company,str) or not re.fullmatch(r'[A-Z]{2}\d{2}',company)
            or not isinstance(question,str) or not 3 <= len(question.strip()) <= 1000
            or any(ord(c)<32 for c in question)):
            raise Fault(400, 'invalid_request')
        require_company(principal, company)
        if po_id is not None and (not isinstance(po_id,str) or not PO_PATTERN.fullmatch(po_id)):
            raise Fault(400, 'invalid_purchase_order')
        if suspicious(question):
            return self.response('refused', [], start, 'Unsafe instruction detected; request business evidence only.')
        if WRITE.search(question):
            return self.response('refused', [], start, 'Read-only assistant. Financial actions require the approved SAP workflow.')
        if not BUSINESS.search(question):
            return self.response('abstained', [], start, 'No supported procurement question was identified.')
        evidence, search_query = [], question
        if po_id:
            row = self.sap.purchase_order(principal,company,po_id)
            text = (f"Purchase order {po_id} for {row['SupplierName']} is {row['Status']}; "
                    f"net amount {row['NetAmount']} {row['Currency']}; "
                    f"exception {row['ExceptionCode']}; last changed {row['LastChangedAt']}.")
            if suspicious(text):
                raise Fault(502, 'upstream_invalid')
            evidence.append({'id':f'sap:{po_id}', 'text':text,
                'source':{'kind':'live_api','resource':po_id,'company':company,
                          'version':row['LastChangedAt']}})
            search_query += ' '+EXCEPTIONS[row['ExceptionCode']]
        chunks = self.index.search(search_query,principal,company,k=3 if not po_id else 2)
        evidence += [{'id':c['id'],'text':c['text'],
                      'source':{'kind':'policy','title':c['title'], 'version':c['version']}}
                     for c in chunks]
        if not evidence:
            return self.response('abstained', [], start, 'No authorized supporting evidence was found.')
        proposed = self.provider.select(question,evidence)
        ids = validate_selection({'evidence_ids':proposed},evidence)
        # Live facts cannot disappear from the answer through model selection.
        if po_id and f'sap:{po_id}' not in ids:
            raise Fault(502, 'model_output_invalid')
        selected = [e for e in evidence if e['id'] in ids]
        return self.response('answered',selected,start)

    def response(self, status, evidence, start, message=None):
        return {'status':status,'answer':message or '\n'.join(f"{e['text']} [{e['id']}]" for e in evidence),
                'evidence':evidence,'provider':self.provider.name,
                'latency_ms':round((time.perf_counter()-start)*1000,2),
                'notice':'Synthetic demo. Evidence supports human review; no SAP writes are performed.'}
