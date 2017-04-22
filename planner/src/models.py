from datetime import date, timedelta
from django.db import models

class Roadmap(models.Model):
    title = models.CharField(max_length=64)

    def __str__(self):
        return ("Список задач: %s\n" +
                "Всего задач: %s") % \
                (self.title, self.tasks.count())

class Task(models.Model):
    title = models.CharField(max_length=64)
    estimate = models.DateField()
    available_states = (
        ('in_progress', 'Выполняется'),
        ('ready', 'Выполнена')
    )
    state = models.CharField(max_length=11, choices=available_states)
    roadmap = models.ForeignKey(
        Roadmap,
        models.CASCADE,
        related_name='tasks',
        related_query_name='task'
    )

    def __str__(self):
        return ("Задача: %s\n" +
                "Статус: %s\n" +
                "Выполнить до: %s\n") % \
                (self.title, self.state, self.estimate)

    @property
    def is_failed(self):
        return (self.state == "in_progress" and
                self.estimate < date.today())

    @property
    def is_critical(self):
        return (self.is_failed or self.estimate - date.today() <
                timedelta(days=3) and self.state == "in_progress")
