"""Reproducible startup and lifecycle used by CLI and integration tests."""
import json
import logging
import os
import secrets
import threading
from contextlib import contextmanager
from pathlib import Path
from .security import Identity, make_tokens
from .retrieval import Index
from .providers import ExtractiveProvider, OllamaProvider
from .integration import SAPClient
from .service import Copilot
from .http import APIHandler, MockHandler, Telemetry, server

ROOT = Path(__file__).resolve().parents[1]

def load(name):
    return json.loads((ROOT/'data'/name).read_text())

@contextmanager
def running(api_port=0, sap_port=0, provider=None, tokens=None, telemetry=None):
    identity = Identity(tokens or make_tokens())
    service_token = secrets.token_urlsafe(32)
    mock = server(MockHandler,identity,telemetry,port=sap_port)
    mock.service_token, mock.orders = service_token,load('purchase_orders.json')
    api = None
    threads = []
    try:
        sap = SAPClient(f'http://127.0.0.1:{mock.server_port}',service_token,identity)
        api = server(APIHandler,identity,telemetry,port=api_port)
        api.copilot = Copilot(Index(load('policies.json')),sap,provider or ExtractiveProvider())
        for srv in (mock,api):
            thread = threading.Thread(target=srv.serve_forever,daemon=True)
            thread.start(); threads.append(thread)
        yield api,mock,identity
    finally:
        for srv,thread in zip((mock,api),threads):
            srv.shutdown(); thread.join(timeout=2)
        mock.server_close()
        if api:
            api.server_close()

def credentials():
    folder = ROOT/'.runtime'
    folder.mkdir(mode=0o700,exist_ok=True)
    path = folder/'tokens.json'
    if path.exists():
        return json.loads(path.read_text())
    tokens = make_tokens()
    fd = os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as out:
        json.dump(tokens,out,indent=2)
    return tokens

def provider_from_env():
    name = os.environ.get('COPILOT_PROVIDER','extractive')
    if name == 'extractive':
        return ExtractiveProvider()
    if name == 'ollama':
        return OllamaProvider(os.environ.get('OLLAMA_URL','http://127.0.0.1:11434'),
                              os.environ.get('OLLAMA_MODEL','qwen2.5:3b'))
    raise ValueError('COPILOT_PROVIDER must be extractive or ollama')

def audit():
    folder = ROOT/'.runtime'
    folder.mkdir(mode=0o700,exist_ok=True)
    logger = logging.getLogger('copilot.audit')
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.FileHandler(folder/'audit.jsonl'))
    return Telemetry(logger)
