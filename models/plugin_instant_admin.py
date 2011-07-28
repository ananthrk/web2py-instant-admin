import os
import copy


global_env = copy.copy(globals())

def get_databases(request):
    dbs = {}
    for (key, value) in global_env.items():
        cond = False
        try:
            cond = isinstance(value, GQLDB)
        except:
            cond = isinstance(value, SQLDB)
        if cond:
            dbs[key] = value
    return dbs


databases = get_databases(None)
db = databases.values()[0]  # Take only one database for now.
tables = db.tables
session.tables = sorted(tables)

if request.controller == 'plugin_instant_admin':
    auth.settings.controller = 'plugin_instant_admin'
    auth.settings.login_url = URL(c='plugin_instant_admin', f='user', args='login')
    auth.settings.on_failed_authentication = URL(c='plugin_instant_admin', f='user', args='login')
    auth.settings.on_failed_authorization = URL(c='plugin_instant_admin', f='user', args='not_authorized')
    auth.settings.login_next = URL(c='plugin_instant_admin', f='index')
    auth.settings.logout_next = URL(c='plugin_instant_admin', f='index')
    auth.settings.profile_next = URL(c='plugin_instant_admin', f='index')


def pretty(s):
    return str(s).replace('_',' ').title()


def plural(name):
    """Minimal and stupid"""
    name=pretty(name)

    if name.endswith('s'):
        return name
    else:
        return name + 's'


def singular(name):
    """Minimal and stupid"""
    name=pretty(name)

    if name.endswith('s'):
        return name[:-1]
    else:
        return name


def is_image(field):
    if field:
        extension = field.split('.')[-1].lower()
        if extension in ['gif', 'png', 'jpg', 'jpeg', 'bmp']:
            return True
    return False
