# Generated by Django 3.2.3 on 2021-05-27 08:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_post_datetime'),
    ]

    operations = [
        migrations.AddField(
            model_name='connection',
            name='datetime',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
