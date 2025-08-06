import sys
import os

# Add your project directory to the sys.path
project_home = '/home/giftedlucky/boutique_POS'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set the Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'boutique_POS.settings'

# Activate virtualenv if using one (skip this if you don’t have a venv)
activate_this = '/home/giftedlucky/.virtualenvs/your_venv_name/bin/activate_this.py'
exec(open(activate_this).read(), dict(__file__=activate_this))

# Get the WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
