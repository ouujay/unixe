# Generated by Django 4.2.4 on 2024-08-28 03:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musker', '0019_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='hashtag',
            name='usage_count',
            field=models.IntegerField(default=0),
        ),
    ]
