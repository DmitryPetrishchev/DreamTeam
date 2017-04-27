# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-24 17:08
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('src', '0003_auto_20170420_1920'),
    ]

    operations = [
        migrations.CreateModel(
            name='Scores',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('points', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.AddField(
            model_name='task',
            name='create_date',
            field=models.DateField(default=datetime.date(2017, 4, 24), editable=False),
        ),
        migrations.AddField(
            model_name='scores',
            name='task',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='scores', related_query_name='score', to='src.Task'),
        ),
    ]
