# -*- coding: utf-8 -*-

import math


def die():
    raise HTTP(404)


def get_pages_list(current_page, number_of_pages):
    """Returns the list of page numbers for pagination
    """
    # taken from http://pypi.python.org/pypi/django-pure-pagination

    PAGE_RANGE_DISPLAYED = 8
    MARGIN_PAGES_DISPLAYED = 2

    result = []
    if number_of_pages <= PAGE_RANGE_DISPLAYED:
        return range(1, number_of_pages+1)


    left_side = PAGE_RANGE_DISPLAYED/2
    right_side = PAGE_RANGE_DISPLAYED - left_side

    if current_page > number_of_pages - PAGE_RANGE_DISPLAYED/2:
        right_side = number_of_pages - current_page
        left_side = PAGE_RANGE_DISPLAYED - right_side
    elif current_page < PAGE_RANGE_DISPLAYED/2:
        left_side = current_page
        right_side = PAGE_RANGE_DISPLAYED - left_side

    for page in xrange(1, number_of_pages+1):
        if page <= MARGIN_PAGES_DISPLAYED:
            result.append(page)
            continue
        if page > number_of_pages - MARGIN_PAGES_DISPLAYED:
            result.append(page)
            continue
        if (page >= current_page - left_side) and (page <= current_page + right_side):
            result.append(page)
            continue
        if result[-1]:
            result.append(None)

    return result


def validate(table_name, id=None):
    """
    Verifies that table and id exists in db
    and returns corresponding Table and Row objects.
    """

    # auth_tables require superuser role
    if is_auth_table(table_name) and not auth.has_membership(role=plugins.instant_admin.superuser_role):
        redirect(auth.settings.on_failed_authorization)

    table_name in tables or die()
    table = db[table_name]

    if id:
        try:
            id = int(id)
        except ValueError:
            die()

        row = table[id] or die()
    else:
        row = None

    return table, row



@auth.requires_login()
def index():
    data = {}
    for table in tables:
        if auth.has_permission('read', table) and not is_auth_table(table):
            t = db[table]
            data[table] = db(t).count()

    return dict(data=data)


@auth.requires_permission('delete', request.args(0))
def confirm_delete():
    table, dummy = validate(request.args(0))
    ids = session.ids
    form = FORM()

    if form.accepts(request.vars, formname='delete_confirmation'):
        for id in ids:
            row = db[table][id] or die()
            del db[table][id]
            session.flash = '%s %s successfully deleted' % (singular(table), id)

        redirect(request.env.http_referrer or URL('list', args=table))

    return dict(table=table,
                ids=ids,
                form=form)


def handle_delete(table, ids):
    if not ids:
        return

    # If there is only on box checked, it is retuned as string. otherwise as list. Convert both to list.
    if isinstance(ids, basestring):
        ids = [ids]

    for id in ids:
        db[table][id] or die()

    session.ids = ids

    redirect(URL('confirm_delete', args=table))


@auth.requires_permission('delete', request.args(0))
def delete():
    table, row = validate(request.args(0), request.args(1))
    handle_delete(table, request.args(1))


@auth.requires_permission('read', request.args(0))
def list():
    table, dummy = validate(request.args(0))

    fields = [field for field in table.fields if table[field].readable and table[field].type is not 'blob']

    handle_delete(table, request.vars.bulk_ids)

    if request.vars.page:
        current_page = int(request.vars.page)
    else:
        current_page = 1

    query = table.id > 0

    # Search
    if request.vars.query:
        query_str = request.vars.query

        query = table.id == 0
        for field in table.fields:
            if table[field].type in ('string', 'text'):
                query = query | table[field].contains(query_str)

    # Sorting
    orderby = ~table['id']
    if request.vars.sort:
        sort_by = request.vars.sort
        sort_by in table.fields or die()
        orderby = table[sort_by]
    if request.vars.sort_reverse == 'true':
        orderby = ~orderby

    number_of_items = db(query).count()
    items_per_page = plugins.instant_admin.items_per_page
    number_of_pages = int(math.ceil(number_of_items / float(items_per_page)))
    pages = get_pages_list(current_page, number_of_pages)

    limitby=((current_page-1)*items_per_page,current_page*items_per_page)

    data = db(query).select(limitby=limitby, orderby=orderby)

    return dict(table=table,
                fields=fields,
                current_page=current_page,
                pages=pages,
                number_of_items=number_of_items,
                number_of_pages=number_of_pages,
                data=data)


@auth.requires_permission('read', request.args(0))
def show():
    table, row = validate(request.args(0), request.args(1))

    fields = [field for field in table.fields if table[field].readable and table[field].type is not 'blob']

    return dict(table=table,
                fields=fields,
                row=row)


@auth.requires_permission('create', request.args(0))
def new():
    table, dummy = validate(request.args(0))

    form = SQLFORM(table, formstyle="divs", showid=False, submit_button='Add')

    if form.accepts(request.vars, session):
        session.flash = '%s %s successfully created.' % (singular(table), form.vars.id)
        redirect(URL('list', args=table))
    elif form.errors:
        response.flash = 'Error. Please correct the issues marked in red below.'

    return dict(table=table,
                form=form)


@auth.requires_permission('update', request.args(0))
def edit():
    table, row = validate(request.args(0), request.args(1))

    form = SQLFORM(table,
                   record=row,
                   upload=URL('download'),
                   formstyle="divs",
                   showid=False,
                   submit_button='Save')

    if form.accepts(request.vars, session):
        session.flash = '%s %s successfully updated.' % (singular(table), row['id'])
        redirect(URL('list', args=table))
    elif form.errors:
        response.flash = 'Error. Please correct the issues marked in red below.'

    return dict(table=table,
                row=row,
                form=form)


def settings():
    data = {}
    for table in auth_tables:
        t = db[table]
        data[table] = db(t).count()

    return dict(data=data)


@auth.requires_login()
def download():
    return response.download(request,db)


def user():
    return dict(form=auth())


def create_roles():
    for role in plugins.instant_admin.roles:
        group = get_or_create_group(role, plugins.instant_admin.roles[role])

        for table in tables:
            if table not in auth_tables:
                if role == plugins.instant_admin.creator_role:
                    get_or_create_permission(group.id, 'create', table)
                elif role == plugins.instant_admin.reader_role:
                    get_or_create_permission(group.id, 'read', table)
                elif role == plugins.instant_admin.editor_role:
                    get_or_create_permission(group.id, 'update', table)
                elif role == plugins.instant_admin.deleter_role:
                    get_or_create_permission(group.id, 'delete', table)

            # For superuser, assign all permissions on all tables including auth tables
            if role == plugins.instant_admin.superuser_role:
                    get_or_create_permission(group.id, 'create', table)
                    get_or_create_permission(group.id, 'read', table)
                    get_or_create_permission(group.id, 'update', table)
                    get_or_create_permission(group.id, 'delete', table)


def create_users():
    superuser_role = plugins.instant_admin.superuser_role
    creator_role = plugins.instant_admin.creator_role
    reader_role = plugins.instant_admin.reader_role
    editor_role = plugins.instant_admin.editor_role
    deleter_role = plugins.instant_admin.deleter_role

    user = get_or_create_user(plugins.instant_admin.admin_user)
    auth.add_membership(user_id=user.id, role=superuser_role)
    auth.add_membership(user_id=user.id, role=creator_role)
    auth.add_membership(user_id=user.id, role=reader_role)
    auth.add_membership(user_id=user.id, role=editor_role)
    auth.add_membership(user_id=user.id, role=deleter_role)

    user = get_or_create_user(plugins.instant_admin.creator_user)
    auth.add_membership(user_id=user.id, role=creator_role)
    auth.add_membership(user_id=user.id, role=reader_role)

    user = get_or_create_user(plugins.instant_admin.reader_user)
    auth.add_membership(user_id=user.id, role=reader_role)

    user = get_or_create_user(plugins.instant_admin.editor_user)
    auth.add_membership(user_id=user.id, role=editor_role)
    auth.add_membership(user_id=user.id, role=reader_role)

    user = get_or_create_user(plugins.instant_admin.deleter_user)
    auth.add_membership(user_id=user.id, role=reader_role)
    auth.add_membership(user_id=user.id, role=deleter_role)


def welcome():
    """ First page to be visited after installation. Will create necessary roles and redirects to index."""
    create_roles()
    create_users()

    session.flash = "Welcome to Web2py Instant Admin"
    redirect(URL('index'))

