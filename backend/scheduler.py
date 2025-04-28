from apscheduler.schedulers.background import BackgroundScheduler
from services.task_replanner import replanify_all

def start_scheduler():
    scheduler = BackgroundScheduler()

    # Añadir job que se ejecute todos los días a las 2:00 AM
    scheduler.add_job(replanify_all, 'cron', hour=2, minute=0)

    scheduler.start()
