import os, sys
import time
import shutil
import zipfile
import filecmp
from fabric.api import env, local, sudo, cd, prefix
from web2py_utils.test_runner import run
from gluon.fileutils import w2p_pack_plugin, w2p_unpack_plugin


plugin_name = 'instant_admin'
root = local("hg root", capture=True)
epoch = int(time.mktime(time.gmtime()))
web2py_location = '/tmp/%s' % epoch
web2py_app = os.path.join(web2py_location, 'web2py', 'applications', 'examples')


def setup_web2py():
    web2py_src = zipfile.ZipFile('/work/web2py_src.zip')
    web2py_src.extractall(web2py_location)
    os.mkdir(os.path.join(web2py_app, 'databases'))


def pack():
    filename = "web2py.plugin.%s.w2p" % plugin_name
    packed_plugin = os.path.join(root, filename)
    w2p_pack_plugin(packed_plugin, root, plugin_name)
    return packed_plugin


def unpack(packed_plugin):
    w2p_unpack_plugin(packed_plugin, web2py_app)
    # verify
    file1 = os.path.join(root, 'controllers', 'plugin_instant_admin.py')
    file2 = os.path.join(web2py_app, 'controllers', 'plugin_instant_admin.py')
    assert filecmp.cmp(file1, file2)


def setup():
    setup_web2py()
    packed_plugin = pack()
    unpack(packed_plugin)
    shutil.copytree(os.path.join(root, 'tests'),
                    os.path.join(web2py_app, 'tests'))



def test():
    setup()
    os.chdir(os.path.join(web2py_location, 'web2py'))
    run(app = 'examples',
        test_key = 'VwK5QyAxyfc626j',
        test_options = {'verbosity': 3,
                        'detailed-errors':True,
                        'stop':True,
                        },
       )
