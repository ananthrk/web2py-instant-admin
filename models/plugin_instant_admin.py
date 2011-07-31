import os
import copy
from storage import Settings

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
tables = sorted(db.tables)
settings = Settings()

try:
    auth
except NameError:
    from gluon.tools import Auth
    auth = Auth(db)
    auth.define_tables()

auth_tables = [str(auth.settings.table_user),
               str(auth.settings.table_group),
               str(auth.settings.table_membership),
               str(auth.settings.table_permission),
               str(auth.settings.table_event),
               str(auth.settings.table_cas)
              ]

settings.superuser_role = "plugin_instant_admin_superuser"
settings.reader_role    = "plugin_instant_admin_reader",
settings.editor_role    = "plugin_instant_admin_editor"
settings.creator_role   = "plugin_instant_admin_creator"
settings.deleter_role   = "plugin_instant_admin_deleter"

settings.roles = roles = {}
roles[settings.superuser_role] = 'Super Users can create, read, update and delete records in all tables including Auth tables.'
roles[settings.reader_role] = 'Readers can read records in all tables.'
roles[settings.editor_role] = 'Editors can edit records in all tables.'
roles[settings.creator_role] = 'Creators can create records in all tables.'
roles[settings.deleter_role] = 'deleters can delete records in all tables.'


settings.admin_user = 'a'
settings.reader_user = 'ar'
settings.editor_user = 'ae'
settings.creator_user = 'ac'
settings.deleter_user = 'ad'

settings.extra_sidebar_title = ''
settings.extra_sidebar = []

settings.items_per_page = 20

from gluon.tools import PluginManager
plugins = PluginManager('instant_admin', **settings)


if request.controller == 'plugin_instant_admin':
    auth.settings.controller = 'plugin_instant_admin'
    auth.settings.login_url = URL(c='plugin_instant_admin', f='user', args='login')
    auth.settings.on_failed_authentication = URL(c='plugin_instant_admin', f='user', args='login')
    auth.settings.on_failed_authorization = URL(c='plugin_instant_admin', f='user', args='not_authorized')
    auth.settings.login_next = URL(c='plugin_instant_admin', f='index')
    auth.settings.logout_next = URL(c='plugin_instant_admin', f='index')
    auth.settings.profile_next = URL(c='plugin_instant_admin', f='index')


def is_auth_table(table_name):
    return str(table_name) in auth_tables


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

    if value is None:
        return value

    # Convert Id to Name
    if field.represent:
        value = field.represent(value)

    if field.type is 'blob':
        value = 'BLOB'

    elif field.type is 'password':
        value = '************'

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


def sidebar_tables():
    t = []
    for table in tables:
        if auth.has_permission('read', table) and not is_auth_table(table):
            li = LI(A(plural(table), _href=URL('list', args=table)),
                    _class="more")

            if table in request.args:
                li['_class'] = "active more"
            t.append(li)
    return t


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


def record_exists(table, field, value):
    table = str(table)
    field = str(fiel)
    return db(db[table][field]==value).select().first() is not None


def get_or_create_user(username):
    password = username
    if 'username' in auth.settings.table_user.fields():
        userkey = 'username'
    elif 'email' in auth.settings.table_user.fields():
        userkey = 'email'
        username = username + '@example.com'
    passfield = auth.settings.password_field
    user = db(auth.settings.table_user[userkey] == username).select().first()
    if not user:
        user_id = db.auth_user.insert(**{userkey:username,passfield:CRYPT(auth.settings.hmac_key)(password)[0]})
        user = auth.settings.table_user(user_id)
    return user


def get_or_create_group(role, description):
    group = db(auth.settings.table_group.role == role).select().first()
    if not group:
        group_id = auth.add_group(role=role, description=description)
        group = auth.settings.table_group(group_id)
    return group


def get_or_create_permission(group_id, name, table_name):
    query = auth.settings.table_permission.group_id == group_id
    query = query & (auth.settings.table_permission.name == name)
    query = query & (auth.settings.table_permission.table_name == table_name)
    permission = db(query).select().first()
    if not permission:
        permission_id = auth.add_permission(group_id, name, table_name)
        permission = auth.settings.table_permission(permission)
    return permission
