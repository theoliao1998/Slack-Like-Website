# Generated by Django 2.2.5 on 2019-12-04 20:04

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('workspaces', '0011_auto_20191204_1945'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='directmessage',
            name='seen',
        ),
        migrations.AddField(
            model_name='directmessage',
            name='dmsgunseen',
            field=models.ManyToManyField(default=[models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiver', to=settings.AUTH_USER_MODEL)], related_name='users_unseened', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='sharelink',
            name='expired_at',
            field=models.DateTimeField(default=datetime.datetime(2020, 1, 3, 20, 4, 0, 883512)),
        ),
    ]
