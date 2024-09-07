import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'somenews.settings')

app = Celery('newspages')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send_mail_every_monday_8am': {
        'task': 'newspages.tasks.send_last_weak_post',
        'schedule': crontab(hour=8, minute=0, day_of_week='monday'),
    },
}
