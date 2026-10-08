"""Bounded JSON HTTP transport; no proxy inheritance or redirects."""
import json
from urllib.request import Request, build_opener, ProxyHandler, HTTPRedirectHandler
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from .security import Fault

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def local_url(url):
    parts = urlsplit(url)
    if (parts.scheme != 'http' or parts.hostname not in ('127.0.0.1', 'localhost')
        or parts.username or parts.password or parts.query or parts.fragment):
        raise ValueError('Demo endpoints must be fixed loopback HTTP URLs')
    return url.rstrip('/')

def request_json(url, headers=None, payload=None, timeout=3):
    body = None if payload is None else json.dumps(payload).encode()
    req = Request(url, data=body, headers={'Content-Type':'application/json', **(headers or {})})
    opener = build_opener(ProxyHandler({}), NoRedirect())
    try:
        with opener.open(req, timeout=timeout) as res:
            data = res.read(262145)
            if len(data) > 262144:
                raise Fault(502, 'upstream_invalid')
            return json.loads(data)
    except HTTPError as exc:
        # Only upstream 404 may be surfaced; don't expose upstream response bodies.
        raise Fault(404 if exc.code == 404 else 502,
                    'not_found' if exc.code == 404 else 'upstream_unavailable') from None
    except (URLError, TimeoutError, OSError):
        raise Fault(503, 'upstream_unavailable') from None
    except (ValueError, UnicodeError):
        raise Fault(502, 'upstream_invalid') from None
