routes_in = (
    ('/$app/admin', '/$app/plugin_instant_admin/index'),
    ('/$app/admin/$anything', '/$app/plugin_instant_admin/$anything'),
)

routes_out = [(x, y) for (y, x) in routes_in]

routes_onerror = [
    ('*/404', '/demo/static/plugin_instant_admin/onerror404.html'),
    ('*/*', '/demo/static/plugin_instant_admin/onerror.html'),
]

default_application = "demo"
default_controller = "plugin_instant_admin"
default_function = "index"


