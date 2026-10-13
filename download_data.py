"""Save the selected World Bank indicators, with URLs and checksums."""
from pathlib import Path
import hashlib
import json
import urllib.request
from datetime import date

ROOT = Path(__file__).parent
COUNTRIES = 'IND;CHN;IDN;BRA;NGA;USA;JPN;DEU'

def download():
    folder = ROOT / 'data'
    folder.mkdir(exist_ok=True)
    sources = {}
    for indicator, filename in [('SP.POP.TOTL', 'population.json'),
                                ('SP.URB.TOTL.IN.ZS', 'urban_share.json')]:
        url = f'https://api.worldbank.org/v2/country/{COUNTRIES}/indicator/{indicator}?format=json&per_page=1000&date=1960:2025'
        blob = urllib.request.urlopen(url, timeout=90).read()
        response = json.loads(blob)
        if not isinstance(response, list) or len(response) != 2:
            raise ValueError('Unexpected World Bank response')
        if response[0]['pages'] != 1:
            raise ValueError('Response needs pagination')
        (folder / filename).write_bytes(blob)
        sources[filename] = {'url': url, 'records': len(response[1]),
                             'api_metadata': response[0],
                             'sha256': hashlib.sha256(blob).hexdigest()}
    (folder / 'provenance.json').write_text(json.dumps(
        {'retrieved_on': str(date.today()), 'sources': sources}, indent=2))

if __name__ == '__main__':
    download()
