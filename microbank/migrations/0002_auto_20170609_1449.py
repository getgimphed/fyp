# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-09 09:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('microbank', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='groupId',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='g_id', to='microbank.ClientGroup'),
        ),
    ]
