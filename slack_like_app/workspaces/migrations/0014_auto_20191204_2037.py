# Generated by Django 2.2.5 on 2019-12-04 20:37

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0013_auto_20191204_2024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sharelink',
            name='expired_at',
            field=models.DateTimeField(default=datetime.datetime(2020, 1, 3, 20, 37, 46, 310829)),
        ),
    ]
