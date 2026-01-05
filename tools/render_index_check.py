from jinja2 import Environment, FileSystemLoader, StrictUndefined
from types import SimpleNamespace
import sys

loader = FileSystemLoader('templates')
env = Environment(loader=loader, undefined=StrictUndefined, keep_trailing_newline=True)
# Provide minimal globals and context the template expects
env.globals['url_for'] = lambda *a, **k: '#'

env.globals['current_user'] = SimpleNamespace(is_authenticated=True, role='admin')

context = {
    'current_user': env.globals['current_user'],
    'messages': [('success','All good')],
    'printers': [
        {
            'name': 'Printer1',
            'ip': '192.168.0.101',
            'location': 'Office',
            'status': 'online',
            'supplies': {'black_toner': 72},
            'counters': {'total_pages': 1234}
        }
    ],
    'last_checked': '2025-11-11 12:00:00',
    'counts': {'online': 1, 'offline': 0, 'unknown': 0, 'invalid': 0},
    'locations': ['Office'],
    'search_query': '',
    'status_filter': 'all',
    'location_filter': 'all'
}

try:
    tmpl = env.get_template('index.html')
    out = tmpl.render(**context)
    # Basic sanity checks
    if '<!DOCTYPE html>' in out and 'Printers - Smart Printer Monitoring' in out:
        print('RENDER OK')
    else:
        print('RENDERED, but basic checks failed')
except Exception:
    print('RENDER ERROR')
    import traceback
    traceback.print_exc()
    sys.exit(1)
