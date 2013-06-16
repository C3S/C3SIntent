#!python
# this file enables deployment of this pyramid app using apache2 and mod_wsgi.
# move it to the top level folder of the project (where the 'env' is, one up)

import os

os.environ['PYTHON_EGG_CACHE'] = '/usr/local/pyramid/python-eggs'
import sys
#sys.path.append('/home/christoph/Code/github/env/bin/python2.6/site-packages')
sys.path.append('/home/yes/github/C3SIntent/c3sintent/')
sys.path.append('/home/yes/github/C3SIntent/')
#sys.path.append('/home/christoph/Code/github/OMCeVmembership/')

import site

ALLDIRS = ['/home/yes/github/env/bin/python2.7/site-packages']

# Remember original sys.path.
previous_sys_path = list(sys.path) 

# Add each new site-packages directory.
for directory in ALLDIRS:
  site.addsitedir(directory)

# Reorder sys.path so new directories at the front.
new_sys_path = [] 
for item in list(sys.path): 
    if item not in previous_sys_path: 
        new_sys_path.append(item) 
        sys.path.remove(item) 
sys.path[:0] = new_sys_path 
site.addsitedir('/home/yes/github/env/bin/python2.7/site-packages')


from pyramid.paster import get_app, setup_logging

HERE = os.path.dirname(__file__)

APP_INIFILE = os.path.join(HERE, 'production.ini')
setup_logging(APP_INIFILE)
application = get_app(APP_INIFILE, 'main')
