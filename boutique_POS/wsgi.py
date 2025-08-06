import os
import sys

# Tell Django we are on PythonAnywhere
os.environ['PYTHONANYWHERE'] = 'true'

# Set correct project directory
project_home = '/home/giftedlucky/boutique_POS/boutique_POS'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Activate your virtualenv
activate_this = '/home/giftedlucky/boutique_POS/boutique_POS/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boutique_POS.settings')

# Load the Django application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Serve static files with WhiteNoise
from whitenoise import WhiteNoise
application = WhiteNoise(application, root=os.path.join(project_home, 'staticfiles'))
