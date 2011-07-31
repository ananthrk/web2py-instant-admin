
def reset():
    import random
    from gluon.contrib.populate import populate
    for table in tables:
        db[table].truncate()
        if table not in auth_tables:
            populate(db[table],random.randint(10, 100))

    redirect(URL('welcome'))
