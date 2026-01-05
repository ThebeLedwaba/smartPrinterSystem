import unittest
import os
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from types import SimpleNamespace
from helpers import get_base_context

class TemplateRenderTests(unittest.TestCase):
    def setUp(self):
        templates_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        loader = FileSystemLoader(templates_dir)
        self.env = Environment(loader=loader, undefined=StrictUndefined)
        self.env.globals['url_for'] = lambda *a, **k: '#'
        self.env.globals['current_user'] = SimpleNamespace(is_authenticated=True, role='admin')
        # Use helper factory for base context (keeps test and future tests consistent)
        self.base_context = get_base_context(self.env.globals['current_user'])

    def test_render_all_templates(self):
        templates_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        problems = []
        for root, dirs, files in os.walk(templates_dir):
            for fn in files:
                if not fn.endswith('.html'):
                    continue
                rel = os.path.relpath(os.path.join(root, fn), templates_dir)
                try:
                    tmpl = self.env.get_template(rel)
                    out = tmpl.render(**self.base_context)
                    if '<html' not in out.lower() or '</html>' not in out.lower():
                        problems.append(f"{rel}: missing <html> or </html>")
                except Exception as e:
                    problems.append(f"{rel}: RENDER ERROR: {e}")
        if problems:
            self.fail('Template render problems:\n' + '\n'.join(problems))

if __name__ == '__main__':
    unittest.main()
