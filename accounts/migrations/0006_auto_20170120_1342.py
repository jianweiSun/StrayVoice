# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-20 05:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_profile_total_followers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='followship',
            name='created',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
    ]
