"""Loopback demo HTTP boundary. Production should use a hardened ASGI gateway."""
import hmac
import json
import logging
import re
import threading
import time
import uuid
from collections import Counter
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, parse_qs
from .security import Fault, require_company, Limiter
from .integration import SAFE_FIELDS

class Telemetry:
    def __init__(self, logger=None):
        self.counts, self.lock = Counter(), threading.Lock()
        self.logger = logger or logging.getLogger('copilot.audit')
    def record(self, route, status, trace, elapsed):
        with self.lock:
            self.counts[f'{route}:{status}'] += 1
        self.logger.info(json.dumps({'event':'http_request','route':route,
                         'status':status,'request_id':trace,'latency_ms':round(elapsed,2)}))
    def snapshot(self):
        with self.lock:
            return {'requests':dict(self.counts)}

class Handler(BaseHTTPRequestHandler):
    server_version = 'PortfolioDemo/1.0'
    sys_version = ''
    def setup(self):
        super().setup()
        self.connection.settimeout(10)
    def log_message(self,*args):
        pass  # Never log headers, raw paths, prompts, tokens or business records.
    def reply(self,status,body,trace):
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(data)))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('X-Request-ID',trace)
        if status == 401:
            self.send_header('WWW-Authenticate','Bearer')
        if status == 429:
            self.send_header('Retry-After','60')
        self.end_headers()
        self.wfile.write(data)
    def body(self):
        if self.headers.get('Transfer-Encoding'):
            raise Fault(400,'invalid_request')
        if self.headers.get_content_type() != 'application/json':
            raise Fault(415,'json_required')
        try:
            if len(self.headers.get_all('Content-Length',[])) != 1:
                raise Fault(400,'invalid_request')
            n = int(self.headers['Content-Length'])
            if not 0 < n <= 8192:
                raise Fault(413,'request_too_large')
            raw = self.rfile.read(n)
            if len(raw) != n:
                raise Fault(400,'invalid_request')
            def unique(pairs):
                d = {}
                for k,v in pairs:
                    if k in d:
                        raise ValueError('duplicate key')
                    d[k] = v
                return d
            return json.loads(raw, object_pairs_hook=unique)
        except (ValueError,UnicodeError):
            raise Fault(400,'invalid_json') from None
    def handle_call(self):
        trace,start = uuid.uuid4().hex,time.perf_counter()
        route = {'/v1/ask':'ask','/metrics':'metrics','/healthz':'health'}.get(urlsplit(self.path).path,'unknown')
        status,body = 500,{'error':'internal_error'}
        acquired = self.server.slots.acquire(blocking=False)
        try:
            if not acquired:
                raise Fault(503,'busy')
            route,status,body = self.dispatch()
        except Fault as exc:
            status,body = exc.status,{'error':exc.code}
        except Exception:
            # Do not emit exception data that may contain credentials or payloads.
            status,body = 500,{'error':'internal_error'}
        finally:
            if acquired:
                self.server.slots.release()
            self.server.telemetry.record(route,status,trace,(time.perf_counter()-start)*1000)
        body['request_id'] = trace
        try:
            self.reply(status,body,trace)
        except (BrokenPipeError,ConnectionResetError):
            pass
    do_GET = handle_call
    do_POST = handle_call
    do_PUT = handle_call
    do_PATCH = handle_call
    do_DELETE = handle_call

class APIHandler(Handler):
    def dispatch(self):
        path = urlsplit(self.path).path
        if self.command == 'GET' and path == '/healthz':
            return 'health',200,{'status':'ok','mode':'synthetic-demo'}
        if path not in ('/v1/ask','/metrics'):
            raise Fault(404,'not_found')
        principal = self.server.identity.authenticate(self.headers.get('Authorization'))
        self.server.limiter.check(principal.subject)
        if path == '/metrics':
            if self.command != 'GET':
                raise Fault(405,'method_not_allowed')
            if 'operator' not in principal.roles:
                raise Fault(403,'forbidden_scope')
            return 'metrics',200,self.server.telemetry.snapshot()
        if self.command != 'POST':
            raise Fault(405,'method_not_allowed')
        return 'ask',200,self.server.copilot.ask(principal,self.body())

class MockHandler(Handler):
    def dispatch(self):
        path = urlsplit(self.path)
        if self.command == 'GET' and path.path == '/healthz':
            return 'health',200,{'status':'ok','mode':'synthetic-sap'}
        if self.command != 'GET':
            raise Fault(405,'read_only')
        if not hmac.compare_digest(self.headers.get('X-Service-Token',''),self.server.service_token):
            raise Fault(401,'unauthenticated')
        principal = self.server.identity.authenticate(self.headers.get('Authorization'))
        m = re.fullmatch(r"/odata/PurchaseOrders\('(\d{10})'\)",path.path)
        if not m:
            raise Fault(404,'not_found')
        query = parse_qs(path.query)
        if set(query) != {'company'} or len(query['company']) != 1:
            raise Fault(400,'invalid_request')
        company = query['company'][0]
        require_company(principal,company)
        for row in self.server.orders:
            if (row['PurchaseOrder'] == m[1] and row['CompanyCode'] == company
                and row['tenant'] == principal.tenant):
                # Projection at source as well as at integration boundary.
                return 'sap_read',200,{'value':{k:row[k] for k in SAFE_FIELDS}}
        raise Fault(404,'not_found')

def server(handler, identity, telemetry=None, port=0):
    srv = ThreadingHTTPServer(('127.0.0.1',port),handler)
    srv.identity, srv.telemetry = identity, telemetry or Telemetry()
    srv.slots, srv.limiter = threading.BoundedSemaphore(8), Limiter()
    srv.daemon_threads = True
    return srv
