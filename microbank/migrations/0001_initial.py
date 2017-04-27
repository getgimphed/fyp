# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-27 09:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(db_column='id', primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30)),
                ('address', models.CharField(max_length=255)),
                ('mobile', models.BigIntegerField()),
                ('loanTaken', models.BinaryField()),
            ],
        ),
        migrations.CreateModel(
            name='ClientGroup',
            fields=[
                ('id', models.AutoField(db_column='id', primary_key=True, serialize=False)),
                ('groupId', models.CharField(db_column='g_id', max_length=32)),
                ('clientId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='microbank.Client')),
            ],
        ),
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.AutoField(db_column='id', primary_key=True, serialize=False)),
                ('groupOrSingle', models.BinaryField()),
                ('amount', models.IntegerField()),
                ('interestRate', models.DecimalField(decimal_places=2, max_digits=4)),
                ('clientId', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='microbank.Client')),
                ('groupId', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='microbank.ClientGroup')),
            ],
        ),
        migrations.CreateModel(
            name='LoanFor',
            fields=[
                ('id', models.AutoField(db_column='id', primary_key=True, serialize=False)),
                ('reason', models.CharField(max_length=32)),
            ],
        ),
    ]