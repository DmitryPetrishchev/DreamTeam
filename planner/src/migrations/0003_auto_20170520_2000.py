# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-20 17:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('src', '0002_user_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='image',
            field=models.ImageField(default='src/users/None/no-img.png', upload_to='src/users/images/'),
        ),
    ]