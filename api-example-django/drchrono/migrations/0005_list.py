# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-04-29 00:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drchrono', '0004_auto_20190428_1443'),
    ]

    operations = [
        migrations.CreateModel(
            name='List',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item', models.CharField(max_length=100)),
                ('finished', models.BooleanField(default=False)),
            ],
        ),
    ]