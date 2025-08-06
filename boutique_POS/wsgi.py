import os
import sys
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

# Add your project directory to the Python path
project_home = '/home/giftedlucky/boutique_POS/boutique_POS'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Activate your virtualenv (optional but recommended)
activate_this = '/home/giftedlucky/boutique_POS/boutique_POS/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boutique_POS.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

application = WhiteNoise(application, root='/home/giftedlucky/boutique_POS/boutique_POS/staticfiles')