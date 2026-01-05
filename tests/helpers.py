from types import SimpleNamespace


def get_base_context(current_user=None):
    """Return a rich base context to render templates in tests.

    Accepts an optional current_user SimpleNamespace so tests can set the same
    user object used by the Jinja environment.
    """
    if current_user is None:
        current_user = SimpleNamespace(is_authenticated=True, role='admin')

    return {
        'current_user': current_user,
        'messages': [('info', 'OK')],
        'printers': [],
        'last_checked': '2025-11-11 12:00:00',
        'counts': SimpleNamespace(online=0, offline=0, unknown=0, invalid=0),
        'status_counts': SimpleNamespace(online=0, offline=0, unknown=0, invalid=0),
        'locations': [],
        'search_query': '',
        'status_filter': 'all',
        'location_filter': 'all',
        'total_pages': 0,
        'charts': {'status': '', 'department': ''},
        'department_usage': {},
        'user_usage': {},
        'plot_url': '',
        'printer': {
            'name': 'Sample Printer',
            'ip': '192.0.2.1',
            'location': 'Office',
        },
        'details': {
            'details': {
                'model': 'Generic',
                'serial_number': 'N/A',
                'department': 'N/A',
                'firmware': 'N/A',
                'maintenance_date': 'N/A'
            },
            'supplies': {},
            'counters': {},
            'status': SimpleNamespace(state='Unknown', uptime_hours=0, alert_codes=[])
        },
        'print_jobs': [],
        'users': {'admin': SimpleNamespace(name='Administrator', role='admin')},
        'message': '',
        'alerts': [],
        'status': 'unknown'
    }
