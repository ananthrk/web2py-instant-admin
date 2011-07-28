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


def create_super_user():
    admin = db.auth_user[111]
    admins = auth.add_group(role = 'Admin')
    auth.add_membership(admins, admin)

    for table in tables:
        auth.add_permission(admins, 'read', table)
        auth.add_permission(admins, 'list', table)
        auth.add_permission(admins, 'create', table)
        auth.add_permission(admins, 'update', table)
        auth.add_permission(admins, 'delete', table)

    return dict()


def validate(table_name, id=None):
    """
    Verifies that table and id exists in db
    and returns corresponding Table and Row objects.
    """
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
    orderby = table['id']
    if request.vars.sort:
        sort_by = request.vars.sort
        sort_by in table.fields or die()
        orderby = table[sort_by]
    if request.vars.sort_reverse == 'true':
        orderby = ~orderby

    number_of_items = db(query).count()
    items_per_page = 20
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


def download():
    return response.download(request,db)

def user():
    return dict(form=auth())


