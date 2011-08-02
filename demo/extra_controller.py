

def reset():
    """ Will truncate all tables and populates again with dummy data.
    """
    from gluon.contrib.populate import populate
    for table in tables:
        db[table].truncate()

    count = request.args(0) or 100
    my_tables = ['users', 'products', 'purchases', 'dogs', 'survey']
    for table in my_tables:
        populate(db[table],int(count))
        db.commit()

    redirect(URL('welcome'))
