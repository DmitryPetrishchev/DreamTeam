import os
from hashlib import sha256
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import ExpressionWrapper, F, Max
from django.utils.deconstruct import deconstructible


#потому что с обычной вложенной функцией не прокатит
@deconstructible
class UploadTo(object):
    def __init__(self, path):
        self.path = path

    def __call__(self, instance, filename):
        filename = sha256(str(datetime.now()).encode()).hexdigest()
        return os.path.join(self.path, filename)


class User(AbstractUser):
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    email = models.EmailField(max_length=64, unique=True)
    phone = models.CharField(max_length=16)
    age = models.PositiveSmallIntegerField(blank=True, null=True)
    region = models.CharField(blank=True, max_length=32)
    image = models.ImageField(blank=True, upload_to=UploadTo('users/images/'))
    statistics = models.ImageField(blank=True, upload_to='users/statistics/')

    def save(self, *args, **kwargs):
        if self.username != self.email:
            self.username = self.email
        super(User, self).save(*args, **kwargs)


class Roadmap(models.Model):
    title = models.CharField(max_length=32)
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='roadmaps',
        related_query_name='roadmap',
        editable=False
    )

    def __str__(self):
        return ("Список задач: %s,\n" +
                "Задач в списке: %s") % \
                (self.title, self.tasks.count())


class Task(models.Model):
    title = models.CharField(max_length=32)
    estimate = models.DateField()
    available_states = (
        ('in_progress', 'Выполняется'),
        ('ready', 'Выполнена')
    )
    state = models.CharField(
        max_length=16,
        default='in_progress',
        choices=available_states
    )
    create_date = models.DateField(auto_now_add=True, editable=False)
    roadmap = models.ForeignKey(
        to=Roadmap,
        on_delete=models.CASCADE,
        related_name='tasks',
        related_query_name='task'
    )

    def __str__(self):
        return ("Задача: %s,\n" +
                "Статус: %s,\n" +
                "Выполнить до: %s\n") % \
                (self.title, self.state, self.estimate)

    def save(self, *args, **kwargs):
        super(Task, self).save(*args, **kwargs)
        if not hasattr(self, 'scores'):
            if self.state == "ready":
                Scores.objects.create(task=self, points=self.calc_points)
        else:
            if self.state == 'in_progress':
                self.scores.delete()

    @property
    def is_failed(self):
        return (self.state == "in_progress" and
                self.estimate < date.today())

    @property
    def is_critical(self):
        return (self.is_failed or self.estimate - date.today() <
                timedelta(days=3) and self.state == "in_progress")

    @property
    def calc_points(self):
        tasks = Task.objects.annotate(
            interval=ExpressionWrapper(
                F('estimate') - F('create_date'),
                output_field=models.DurationField()
            )
        )
        max_estimate = tasks.aggregate(
            max_estimate=Max('interval')
        ).get('max_estimate')
        points = (date.today() - self.create_date) / \
                 (self.estimate - self.create_date) + \
                 (self.estimate - self.create_date) / \
                 max_estimate
        return points


class Scores(models.Model):
    task = models.OneToOneField(
        to=Task,
        on_delete=models.CASCADE,
        related_name='scores',
        related_query_name='score'
    )
    date = models.DateTimeField(auto_now_add=True)
    points = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return ("Зачислено %s очков " +
                "за задачу '%s'") % \
                (self.points, self.task.title)
