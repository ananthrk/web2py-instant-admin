import os, sys
import time
import fileinput
import shutil
import zipfile
import filecmp
from path import path
from fabric.api import env, local, sudo, cd, prefix
from web2py_utils.test_runner import run
from gluon.fileutils import w2p_pack_plugin, w2p_unpack_plugin


plugin_name = 'instant_admin'
root = path(local("hg root", capture=True))
dropbox = path(os.getenv('HOME'))/'Dropbox'/'Public'
epoch = str(time.mktime(time.gmtime()))
tmp = path('/tmp')
web2py_location = tmp/epoch/'web2py'
web2py_app = web2py_location/'applications'/'welcome'
web2py_demo_app = web2py_location/'applications'/'demo'


def install_web2py():
    web2py_src = zipfile.ZipFile('/work/web2py_src.zip')
    web2py_src.extractall(web2py_location/'..')
    os.mkdir(web2py_app/'databases')


def install_demo_app():
    os.rename(web2py_app, web2py_demo_app)
    shutil.copy(root/'demo'/'app.yaml', web2py_location)
    shutil.copy(root/'demo'/'cron.yaml', web2py_location)
    shutil.copy(root/'demo'/'index.yaml', web2py_location)
    shutil.copy(root/'demo'/'db.py', web2py_demo_app/'models')


def pack():
    filename = "web2py.plugin.%s.w2p" % plugin_name
    packed_plugin = dropbox/filename
    w2p_pack_plugin(packed_plugin, root, plugin_name)
    return packed_plugin


def unpack(packed_plugin):
    w2p_unpack_plugin(packed_plugin, web2py_demo_app)
    # verify
    file1 = root/'controllers'/'plugin_instant_admin.py'
    file2 = web2py_demo_app/'controllers'/'plugin_instant_admin.py'
    assert filecmp.cmp(file1, file2)


def install_plugin():
    packed_plugin = pack()
    unpack(packed_plugin)


def setup():
    install_web2py()
    install_demo_app()
    install_plugin()
    os.chdir(web2py_location)

    # Append logic to truncate existing data & populate dummy data.
    dest = open(web2py_demo_app/'controllers'/'plugin_instant_admin.py', 'a')
    src = open(root/'demo'/'extra_controller.py', 'r')
    dest.write(src.read())
    src.close()
    dest.close()


def test():
    setup()
    shutil.copytree(root/'tests', web2py_demo_app/'tests')
    run(app = 'demo',
        test_key = 'VwK5QyAxyfc626j',
        test_options = dict(verbosity=3,
                            stop=1)
       )


def dev():
    gae(dev=True)


def gae(dev=False):
    setup()
    shutil.copy(root/'demo'/'routes.py', web2py_location)

    # Add demo passwords
    src = open(root/'demo'/'user.html', 'r')
    dest = web2py_demo_app/'views'/'plugin_instant_admin'/'user.html'
    for line in fileinput.input(dest, inplace=1):
        print line,
        if line.startswith('{{block auth}}'):
            print src.read()
    src.close()

    # Add welcome message
    src = open(root/'demo'/'sidebar.html', 'r')
    dest = web2py_demo_app/'views'/'plugin_instant_admin'/'layout.html'
    for line in fileinput.input(dest, inplace=1):
        print line,
        if line.strip() == '{{#extra-sidebar}}':
            print src.read()
    src.close()

    # Add feedback widget
    src = open(root/'demo'/'layout.html', 'r')
    dest = web2py_demo_app/'views'/'plugin_instant_admin'/'layout.html'
    for line in fileinput.input(dest, inplace=1):
        if line.startswith('</body>'):
            print src.read()
        print line,
    src.close()

    if dev:
        local('dev_appserver.py .')
    else:
        local('appcfg.py update .')


