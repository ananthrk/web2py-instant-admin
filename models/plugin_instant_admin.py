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


try:
    auth
except NameError:
    from gluon.tools import Auth
    auth = Auth(db)
    auth.define_tables()

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


def is_image(value):
    if value:
        extension = value.split('.')[-1].lower()
        if extension in ['gif', 'png', 'jpg', 'jpeg', 'bmp']:
            return True
    return False


def pretty(s):
    s = str(s).replace('_',' ').title()
    if s.endswith(' Id'):
        s = s.replace(' Id', '')
    return s


def pretty_value(table, row, field_name):
    field = table[field_name]
    value = row[field_name]
    original_value = value

    if not value:
        return value

    # Convert Id to Name
    if field.represent:
        value = field.represent(value)

    if field.type is 'blob':
        value = 'BLOB'

    elif field.type.startswith('reference'):
        refers_to = field.type[10:]
        link_to = URL('show', args=(refers_to, original_value))
        value = A(value, _href=link_to)

    elif field.type is 'boolean':
        if original_value:
            value = IMG(_src=URL('static','plugin_instant_admin/images/icon-yes.png'),
                        _alt=value)
        else:
            value = IMG(_src=URL('static','plugin_instant_admin/images/icon-no.png'),
                        _alt=value)

    elif field.type is 'upload':
        download = URL('download', args=value)
        if is_image(value):
            value = IMG(_src=download,
                        _alt=value,
                        _width="200px")
        else:
            value = A(value, _href=download)

    return value


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

