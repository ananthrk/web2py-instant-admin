
def reset():
    import random
    from gluon.contrib.populate import populate
    for table in tables:
        db[table].truncate()
        if table not in auth_tables:
            populate(db[table],random.randint(100, 200))

    redirect(URL('welcome'))
