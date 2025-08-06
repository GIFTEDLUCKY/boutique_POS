import os
import sys

path = '/home/giftedlucky/boutique_POS/boutique_POS'
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "boutique_POS.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
