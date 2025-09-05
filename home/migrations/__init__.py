from django.db import models
from django.utils import timezone
from celery import shared_task, Celery
from collections import Counter
from django.db.models import Sum
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from datetime import datetime


class Order(models.Model):
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    item_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()

class SalesReport(models.Model):
    date = models.DateField(unique=True)
    total_orders = models.PositiveIntegerField()
    total_sales = models.DecimalField(max_digits=10, decimal_places=2)
    top_item = models.CharField(max_length=100)


@shared_task
def generate_sales_report():
    today = timezone.now().date()
    if SalesReport.objects.filter(date=today).exists():
        return "Already exists"
    orders = Order.objects.filter(created_at__date=today)
    total_orders = orders.count()
    total_sales = orders.aggregate(s=Sum('total_price'))['s'] or 0
    counter = Counter()
    for o in orders:
        for i in o.items.all():
            counter[i.item_name] += i.quantity
    top_item = counter.most_common(1)[0][0] if counter else "-"
    SalesReport.objects.create(date=today, total_orders=total_orders, total_sales=total_sales, top_item=top_item)
    return "OK"


app = Celery('your_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


def setup_cron():
    sched, _ = CrontabSchedule.objects.get_or_create(minute='59', hour='23')
    PeriodicTask.objects.get_or_create(crontab=sched, name='Nightly Sales Report', task='your_app.tasks.generate_sales_report', start_time=datetime.now())
