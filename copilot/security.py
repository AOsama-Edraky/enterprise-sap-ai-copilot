"""Local opaque identities. This is a demo authenticator, not an OIDC implementation."""
from dataclasses import dataclass
import hmac
import re
import secrets
from collections import defaultdict, deque
from threading import Lock
from time import monotonic

class Fault(Exception):
    def __init__(self, status, code):
        self.status, self.code = status, code
        super().__init__(code)

@dataclass(frozen=True)
class Principal:
    subject: str
    tenant: str
    companies: tuple[str, ...]
    roles: tuple[str, ...]

PERSONAS = {
    'buyer-eg': Principal('buyer-eg', 'alpha', ('EG01',), ('procurement',)),
    'buyer-sa': Principal('buyer-sa', 'alpha', ('SA01',), ('procurement',)),
    'finance-eg': Principal('finance-eg', 'alpha', ('EG01',), ('finance',)),
    'buyer-beta': Principal('buyer-beta', 'beta', ('EG01',), ('procurement',)),
    'operator': Principal('operator', 'alpha', (), ('operator',)),
}

def make_tokens():
    return {name: secrets.token_urlsafe(32) for name in PERSONAS}

class Identity:
    def __init__(self, tokens):
        if set(tokens) != set(PERSONAS) or len(set(tokens.values())) != len(tokens):
            raise ValueError('Invalid demo identity configuration')
        self.tokens = tokens

    def authenticate(self, authorization):
        if not isinstance(authorization, str) or not authorization.startswith('Bearer '):
            raise Fault(401, 'unauthenticated')
        token = authorization[7:]
        for name, expected in self.tokens.items():
            if hmac.compare_digest(token, expected):
                return PERSONAS[name]
        raise Fault(401, 'unauthenticated')

    def token_for(self, principal):
        return self.tokens[principal.subject]

def require_company(principal, company):
    if company not in principal.companies:
        raise Fault(403, 'forbidden_scope')

def visible(principal, company, item):
    return (item['tenant'] == principal.tenant and company in item['companies']
            and bool(set(principal.roles).intersection(item['roles'])))

WRITE = re.compile(r'\b(approve|release|delete|update|pay|execute|post)\b', re.I)
INJECTION = re.compile(r'ignore\s+(all\s+)?(previous|prior)|system\s+prompt|developer\s+message|bypass\s+(security|authorization)|reveal\s+(secrets|tokens)', re.I)

def suspicious(text):
    return bool(INJECTION.search(text))

class Limiter:
    """Rolling window; per-process only, bounded to configured identities."""
    def __init__(self, limit=30, window=60, clock=monotonic):
        self.limit, self.window, self.clock = limit, window, clock
        self.events, self.lock = defaultdict(deque), Lock()

    def check(self, subject):
        with self.lock:
            now = self.clock()
            queue = self.events[subject]
            while queue and queue[0] <= now-self.window:
                queue.popleft()
            if len(queue) >= self.limit:
                raise Fault(429, 'rate_limited')
            queue.append(now)
