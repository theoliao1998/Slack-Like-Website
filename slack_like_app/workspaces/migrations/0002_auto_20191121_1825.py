# Generated by Django 2.2.5 on 2019-11-21 18:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='channelmessage',
            name='channel',
        ),
        migrations.AddField(
            model_name='datemessages',
            name='channel',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='workspaces.Channel'),
        ),
    ]
