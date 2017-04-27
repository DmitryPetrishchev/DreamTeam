from datetime import date, timedelta
from django.db import models
from django.db.models import F, Max, ExpressionWrapper

class Roadmap(models.Model):
    title = models.CharField(max_length=64)

    def __str__(self):
        return ("Список задач: '%s',\n" +
                "Всего задач: '%s'") % \
                (self.title, self.tasks.count())

class Task(models.Model):
    title = models.CharField(max_length=64)
    estimate = models.DateField()
    available_states = (
        ('in_progress', 'Выполняется'),
        ('ready', 'Выполнена')
    )
    state = models.CharField(
        max_length=11,
        default='in_progress',
        choices=available_states
    )
    create_date = models.DateField(auto_now_add=True, editable=False)
    roadmap = models.ForeignKey(
        Roadmap,
        models.CASCADE,
        related_name='tasks',
        related_query_name='task'
    )

    def __str__(self):
        return ("Задача: '%s',\n" +
                "Статус: '%s',\n" +
                "Выполнить до: '%s'\n") % \
                (self.title, self.state, self.estimate)

    def save(self, *args, **kwargs):
        super(Task, self).save(*args, **kwargs)
        if not hasattr(self, 'scores'):
            if self.state == "ready":
                Scores(task=self, points=self.calc_points).save()

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
        tasks = Task.objects.annotate(interval=ExpressionWrapper(
            F('estimate') - F('create_date'),
            output_field=models.DurationField()
        ))
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
        Task,
        models.CASCADE,
        related_name='scores',
        related_query_name='score'
    )
    date = models.DateTimeField(auto_now_add=True)
    points = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return ("Зачислено '%s' очков " +
                "за задачу '%s'(id=%s)") % \
                (self.points, self.task.title, self.task.id)
