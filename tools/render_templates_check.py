"""Render all Jinja2 templates in ./templates and perform basic HTML sanity checks.
This script will:
- Render each template with a safe minimal context (mocks for url_for and current_user).
- Check the rendered output contains <html> and </html>, and <!DOCTYPE html> when expected.
- Print a summary and exit non-zero if issues are found.

Usage: python tools\render_templates_check.py
"""
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from types import SimpleNamespace
import os
import sys

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), '..', 'templates')

loader = FileSystemLoader(TEMPLATES_DIR)
env = Environment(loader=loader, undefined=StrictUndefined)
# Minimal globals
env.globals['url_for'] = lambda *a, **k: '#'
env.globals['current_user'] = SimpleNamespace(is_authenticated=True, role='admin')

# Basic context used to render templates
base_context = {
    'current_user': env.globals['current_user'],
    'messages': [('info', 'OK')],
    'printers': [],
    'last_checked': '2025-11-11 12:00:00',
    'counts': {'online': 0, 'offline': 0, 'unknown': 0, 'invalid': 0},
    'locations': [],
    'search_query': '',
    'status_filter': 'all',
    'location_filter': 'all'
}

errors = []
rendered = 0

for root, dirs, files in os.walk(TEMPLATES_DIR):
    for fn in files:
        if not fn.endswith('.html'):
            continue
        rel = os.path.relpath(os.path.join(root, fn), TEMPLATES_DIR)
        try:
            tmpl = env.get_template(rel)
            out = tmpl.render(**base_context)
            rendered += 1
            # Basic sanity checks
            if '<html' not in out.lower() or '</html>' not in out.lower():
                errors.append((rel, 'Missing <html> or </html>'))
            if fn == 'index.html' and '<!doctype html>' not in out.lower():
                errors.append((rel, 'Missing <!DOCTYPE html> in index.html'))
        except Exception as e:
            errors.append((rel, f'RENDER ERROR: {e}'))

# Summary
print(f"Templates scanned: {rendered}")
if errors:
    print('Errors:')
    for t, msg in errors:
        print(f' - {t}: {msg}')
    sys.exit(1)
else:
    print('All templates rendered OK')
    sys.exit(0)
