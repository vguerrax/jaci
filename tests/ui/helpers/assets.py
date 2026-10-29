"""Dependências reais em cache e bloqueio de recursos externos opcionais."""
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[3]


def install_assets(context):
    assets={entry['url']:entry for entry in json.loads((ROOT/'tests/ui/assets.json').read_text())}
    for entry in assets.values():
        path=ROOT/'.cache/ui-assets'/entry['name']
        assert path.is_file(), 'Execute venv/bin/python -m scripts.setup_ui_assets'
        assert hashlib.sha256(path.read_bytes()).hexdigest()==entry['sha256']
    def route_resource(route):
        url=route.request.url
        if urlparse(url).hostname in ('127.0.0.1','localhost'):
            route.continue_()
        elif url in assets:
            entry=assets[url]
            route.fulfill(path=str(ROOT/'.cache/ui-assets'/entry['name']),
                          content_type='text/css' if entry['name'].endswith('.css') else 'application/javascript')
        elif route.request.resource_type in ('font','stylesheet'):
            route.fulfill(status=200,body='',content_type='text/css')
        else:
            route.abort()
    context.route('**/*',route_resource)
