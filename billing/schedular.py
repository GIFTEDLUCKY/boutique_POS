# billing/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from billing.sync import sync_sales

def start_sync_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(sync_sales, 'interval', minutes=1)  # runs every 1 minute
    scheduler.start()
    print("Background sync scheduler started.")
