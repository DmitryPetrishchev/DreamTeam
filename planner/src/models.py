from django.db import models

class Roadmap(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return ("Список задач: %s\n" +
                "Всего задач: %s") % \
                (self.title, self.tasks.count())

class Task(models.Model):
    title = models.CharField(max_length=255)
    estimate = models.DateField()
    state = models.CharField(max_length=11)
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
