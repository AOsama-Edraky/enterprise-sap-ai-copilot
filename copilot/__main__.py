import argparse
import json
import signal
import threading
from pathlib import Path
from .runtime import running, credentials, provider_from_env, audit, ROOT
from .transport import request_json

def main():
    parser = argparse.ArgumentParser(description='Synthetic SAP enterprise AI copilot')
    parser.add_argument('command',choices=('serve','demo','eval'))
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    if args.command == 'serve':
        stop = threading.Event()
        signal.signal(signal.SIGINT,lambda *_:stop.set())
        signal.signal(signal.SIGTERM,lambda *_:stop.set())
        with running(api_port=8080,sap_port=8081,provider=provider_from_env(),
                     tokens=credentials(),telemetry=audit()):
            print('Copilot: http://127.0.0.1:8080 | Mock SAP: http://127.0.0.1:8081',flush=True)
            print('Generated demo tokens: .runtime/tokens.json | CTRL+C to stop',flush=True)
            stop.wait()
    elif args.command == 'demo':
        with running(provider=provider_from_env()) as (api,_,identity):
            base = f'http://127.0.0.1:{api.server_port}'
            cases = [
                ('buyer-eg',{'company_code':'EG01','purchase_order':'4500001001','question':'Why is this purchase order blocked?'}),
                ('buyer-eg',{'company_code':'EG01','question':'What is the purchase order approval threshold?'}),
                ('buyer-eg',{'company_code':'EG01','purchase_order':'4500001001','question':'Approve this purchase order'}),
            ]
            for who,payload in cases:
                result = request_json(base+'/v1/ask',{'Authorization':'Bearer '+identity.tokens[who]},payload,timeout=50)
                print(json.dumps({'question':payload['question'],**result},indent=2))
    else:
        from .evaluation import evaluate
        result = evaluate(provider_from_env())
        output = args.output or ROOT/'evals'/'latest-results.json'
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result,indent=2))
        raise SystemExit(0 if result['passed'] == result['total'] else 1)

if __name__ == '__main__':
    main()
