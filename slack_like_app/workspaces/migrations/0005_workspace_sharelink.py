# Generated by Django 2.2.5 on 2019-11-26 03:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0004_channel_users'),
    ]

    operations = [
        migrations.AddField(
            model_name='workspace',
            name='sharelink',
            field=models.CharField(default='UDby9yXfwKrRvm', max_length=20),
        ),
    ]
