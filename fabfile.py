import os, sys
import time
import shutil
import zipfile
import filecmp
from path import path
from fabric.api import env, local, sudo, cd, prefix
from web2py_utils.test_runner import run
from gluon.fileutils import w2p_pack_plugin, w2p_unpack_plugin


plugin_name = 'instant_admin'
root = path(local("hg root", capture=True))
epoch = str(time.mktime(time.gmtime()))
tmp = path('/tmp')
web2py_location = tmp/epoch/'web2py'
web2py_app = web2py_location/'applications'/'welcome'


def setup_web2py():
    web2py_src = zipfile.ZipFile('/work/web2py_src.zip')
    web2py_src.extractall(web2py_location/'..')
    os.mkdir(web2py_app/'databases')


def pack():
    filename = "web2py.plugin.%s.w2p" % plugin_name
    packed_plugin = root/filename
    w2p_pack_plugin(packed_plugin, root, plugin_name)
    return packed_plugin


def unpack(packed_plugin):
    w2p_unpack_plugin(packed_plugin, web2py_app)
    # verify
    file1 = root/'controllers'/'plugin_instant_admin.py'
    file2 = web2py_app/'controllers'/'plugin_instant_admin.py'
    assert filecmp.cmp(file1, file2)


def setup():
    setup_web2py()
    packed_plugin = pack()
    unpack(packed_plugin)


def test():
    setup()
    shutil.copytree(root/'tests', web2py_app/'tests')
    os.chdir(web2py_location)
    run(app = 'welcome',
        test_key = 'VwK5QyAxyfc626j',
        test_options = {'verbosity': 3,
                        'detailed-errors':True,
                        'stop':True,
                        },
       )
