"""Repeatable contract/quality gates over real local HTTP. Not a semantic LLM benchmark."""
import json
import time
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from .runtime import running, load, ROOT

def evaluate(provider):
    cases = json.loads((ROOT/'evals/scenarios.json').read_text())
    rows = []
    with running(provider=provider) as (api,_,identity):
        for case in cases:
            start = time.perf_counter()
            request = Request(f'http://127.0.0.1:{api.server_port}/v1/ask',
                data=json.dumps(case['request']).encode(), headers={
                'Content-Type':'application/json',
                'Authorization':'Bearer '+identity.tokens[case['persona']]})
            try:
                with urlopen(request,timeout=50) as res:
                    status,body = res.status,json.load(res)
            except HTTPError as exc:
                status,body = exc.code,json.load(exc)
            checks = {'http_status':status == case['expected_http']}
            if status == 200:
                evidence = body.get('evidence',[])
                ids = {e['id'] for e in evidence}
                checks['decision'] = body.get('status') == case['expected_status']
                checks['required_evidence'] = set(case['required_ids']) <= ids
                # Exact claim grounding: output is compiled from selected evidence.
                checks['grounded_rendering'] = (not evidence or body['answer'] ==
                    '\n'.join(f"{e['text']} [{e['id']}]" for e in evidence))
                principal = identity.authenticate('Bearer '+identity.tokens[case['persona']])
                policy_by_id = {c['id']:c for c in load('policies.json')}
                from .security import visible
                checks['authorized_policy_evidence'] = all(
                    e['id'] not in policy_by_id or visible(principal,case['request']['company_code'],policy_by_id[e['id']])
                    for e in evidence)
            serialized = json.dumps(body)
            checks['no_forbidden_data'] = all(s not in serialized for s in
                 case['forbidden_text']+['SYNTHETIC-NOT-A-REAL-BANK-ACCOUNT','SupplierBankAccount'])
            rows.append({'id':case['id'],'passed':all(checks.values()),'checks':checks,
                         'latency_ms':round((time.perf_counter()-start)*1000,2)})
    latencies = sorted(r['latency_ms'] for r in rows)
    return {'generated_at':datetime.now(timezone.utc).isoformat(),'provider':provider.name,
            'evaluation_type':'synthetic contract gates; not real-world semantic quality',
            'total':len(rows),'passed':sum(r['passed'] for r in rows),
            'p95_latency_ms':latencies[min(len(rows)-1,int(len(rows)*0.95))],
            'scenarios':rows}
