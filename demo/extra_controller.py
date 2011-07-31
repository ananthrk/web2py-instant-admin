
def reset():
    from gluon.contrib.populate import populate
    for table in tables:
        db[table].truncate()
        if table not in auth_tables:
            populate(db[table],100)
            db.commit()

    redirect(URL('welcome'))
