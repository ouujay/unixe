# Generated by Django 4.2.4 on 2024-08-24 23:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musker', '0011_hashtag_alter_profile_date_modified'),
    ]

    operations = [
        migrations.AddField(
            model_name='meep',
            name='hashtags',
            field=models.ManyToManyField(blank=True, related_name='meeps', to='musker.hashtag'),
        ),
    ]
