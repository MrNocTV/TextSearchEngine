# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-02 02:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Doc',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tf', models.IntegerField()),
                ('doc', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='IR.Doc')),
            ],
        ),
        migrations.CreateModel(
            name='Term',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=250)),
                ('how_many', models.IntegerField()),
                ('idf', models.FloatField()),
            ],
        ),
        migrations.AddField(
            model_name='entry',
            name='term',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='IR.Term'),
        ),
    ]