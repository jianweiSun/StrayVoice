# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-20 05:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0009_auto_20170118_1531'),
    ]

    operations = [
        migrations.AlterField(
            model_name='albumlikeship',
            name='created',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='songlikeship',
            name='created',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
    ]