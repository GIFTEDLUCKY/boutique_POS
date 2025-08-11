import os
import sys
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

# Detect if running on PythonAnywhere
on_pythonanywhere = 'PYTHONANYWHERE_DOMAIN' in os.environ or 'PYTHONANYWHERE' in os.environ

if on_pythonanywhere:
    # PythonAnywhere project directory
    project_home = '/home/giftedlucky/boutique_POS/boutique_POS'
    if project_home not in sys.path:
        sys.path.insert(0, project_home)

    # Try to activate the PythonAnywhere virtualenv (if activate_this.py exists)
    venv_activate = '/home/giftedlucky/boutique_POS/boutique_POS/venv/bin/activate_this.py'
    if os.path.exists(venv_activate):
        with open(venv_activate) as file_:
            exec(file_.read(), dict(__file__=venv_activate))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boutique_POS.settings')

# Load Django application
application = get_wsgi_application()

# Serve static files with WhiteNoise
application = WhiteNoise(application, root=os.path.join(os.path.dirname(__file__), 'staticfiles'))
