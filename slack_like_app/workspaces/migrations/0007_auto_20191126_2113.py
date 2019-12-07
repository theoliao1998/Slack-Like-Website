# Generated by Django 2.2.5 on 2019-11-26 21:13

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0006_auto_20191126_0520'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datemessages',
            name='created_at',
        ),
        migrations.AddField(
            model_name='datemessages',
            name='date',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='workspace',
            name='sharelink',
            field=models.CharField(default='FrkMShfa2L8XyX', max_length=20),
        ),
    ]