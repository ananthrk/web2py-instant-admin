

def reset():
    """ Will truncate all tables and populates again with dummy data.
    """
    from gluon.contrib.populate import populate
    for table in tables:
        db[table].truncate()

    my_tables = ['users', 'products', 'purchases', 'dogs', 'survey']
    for table in my_tables:
        populate(db[table],100)
        db.commit()

    redirect(URL('welcome'))
