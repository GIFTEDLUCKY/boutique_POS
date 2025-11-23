# billing/apps.py
from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
import socket
import atexit

class BillingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'billing'

    def ready(self):
        import billing.signals  # keep your signals
        self.start_scheduler()

    def start_scheduler(self):
        from billing.sync import full_sync as sync_sales

        def check_internet(host="8.8.8.8", port=53, timeout=3):
            try:
                socket.setdefaulttimeout(timeout)
                socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
                return True
            except Exception:
                return False

        # Avoid running scheduler twice in autoreload
        if hasattr(self, 'scheduler_started'):
            return

        self.scheduler_started = True
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            lambda: sync_sales() if check_internet() else print("No internet. Will retry."),
            'interval',
            minutes=5,
            id='sync_sales_job',
            replace_existing=True
        )

        scheduler.start()
        print("Background sync scheduler started.")

        # Shutdown scheduler when Django exits
        atexit.register(lambda: scheduler.shutdown())
