"""Cache explícito de dependências visuais reais, fixadas por hash para testes UI."""
import hashlib
import json
from pathlib import Path
import httpx

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'tests/ui/assets.json'
CACHE=ROOT/'.cache/ui-assets'


def setup():
    CACHE.mkdir(parents=True,exist_ok=True)
    for entry in json.loads(MANIFEST.read_text()):
        target=CACHE/entry['name']
        if target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest()==entry['sha256']:
            continue
        response=httpx.get(entry['url'],follow_redirects=True,timeout=30)
        response.raise_for_status()
        if hashlib.sha256(response.content).hexdigest()!=entry['sha256']:
            raise ValueError('Hash de dependência UI divergente: '+entry['name'])
        target.write_bytes(response.content)


if __name__=='__main__':
    setup()
